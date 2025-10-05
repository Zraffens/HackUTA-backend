from flask import request, send_file
from flask_restx import Resource, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from .dto import NoteDto
from ...models.note import Note
from ...models.user import User
from ...models.comment import Comment
from ...models.reaction import NoteReaction
from ...services.file_service import save_file, fix_file_path
from ...services.ocr_service import ocr_service
from ...utils.pagination import paginate_query
from ... import db
import logging
import os

logger = logging.getLogger(__name__)

api = NoteDto.api
_note_display = NoteDto.note_display
_note_paginated = NoteDto.note_paginated
_note_create = NoteDto.note_create
_comment = NoteDto.comment
_comment_create = NoteDto.comment_create
_reaction_create = NoteDto.reaction_create
_reaction_summary = NoteDto.reaction_summary
_collaborator_add = NoteDto.collaborator_add
_collaborator = NoteDto.collaborator

@api.route('')
class NoteList(Resource):
    @api.doc(params={
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 10, max: 100)'
    })
    @api.marshal_with(_note_paginated)
    def get(self):
        """List all public notes (paginated)"""
        query = Note.query.filter_by(is_public=True)
        return paginate_query(query)

    @jwt_required()
    @api.expect(_note_create, validate=True)
    def post(self):
        """Create a new note with OCR conversion"""
        args = _note_create.parse_args()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()

        # Save the original file (PDF or image)
        file = args['file']
        file_path = save_file(file)
        if not file_path:
            return {'message': 'File type not allowed or file save failed'}, 400

        # Create the note with 'pending' OCR status
        new_note = Note(
            title=args['title'],
            description=args['description'],
            is_public=args['is_public'],
            owner_id=user.id,
            file_path=file_path,
            ocr_status='pending'
        )
        db.session.add(new_note)
        db.session.commit()
        
        # Start OCR conversion asynchronously (or synchronously for now)
        logger.info(f"Starting OCR conversion for note {new_note.public_id}")
        
        try:
            # Update status to processing
            new_note.ocr_status = 'processing'
            db.session.commit()
            
            # Convert to markdown using MonkeyOCR
            output_filename = f"note_{new_note.public_id}"
            markdown_path = ocr_service.convert_to_markdown(file_path, output_filename)
            
            if markdown_path:
                # Update note with markdown path
                new_note.markdown_path = markdown_path
                new_note.ocr_status = 'completed'
                logger.info(f"OCR conversion completed for note {new_note.public_id}")
            else:
                new_note.ocr_status = 'failed'
                logger.error(f"OCR conversion failed for note {new_note.public_id}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error during OCR conversion: {str(e)}")
            new_note.ocr_status = 'failed'
            db.session.commit()
        
        return marshal(new_note, _note_display), 201


@api.route('/search')
class NoteSearch(Resource):
    @api.doc(params={
        'q': 'Search query (searches in title and description)',
        'tags': 'Comma-separated tag names',
        'course_id': 'Filter by course ID',
        'is_public': 'Filter by public/private (true/false)',
        'owner': 'Filter by owner username',
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 10, max: 100)'
    })
    @api.marshal_with(_note_paginated)
    def get(self):
        """Search and filter notes (paginated)"""
        query = Note.query
        
        # Text search in title and description
        search_text = request.args.get('q', '').strip()
        if search_text:
            search_pattern = f'%{search_text}%'
            query = query.filter(
                (Note.title.ilike(search_pattern)) |
                (Note.description.ilike(search_pattern))
            )
        
        # Filter by tags
        tag_names = request.args.get('tags', '').strip()
        if tag_names:
            from ...models.tag import Tag
            tag_list = [t.strip() for t in tag_names.split(',') if t.strip()]
            if tag_list:
                # Join with tags and filter
                query = query.join(Note.tags).filter(Tag.name.in_(tag_list))
        
        # Filter by course
        course_id = request.args.get('course_id', '').strip()
        if course_id:
            from ...models.course import Course
            query = query.join(Note.courses).filter(Course.public_id == course_id)
        
        # Filter by visibility
        is_public = request.args.get('is_public', '').strip()
        if is_public:
            if is_public.lower() == 'true':
                query = query.filter(Note.is_public == True)
            elif is_public.lower() == 'false':
                query = query.filter(Note.is_public == False)
        else:
            # Default to public only if not authenticated
            from flask_jwt_extended import verify_jwt_in_request
            try:
                verify_jwt_in_request(optional=True)
                current_user_public_id = get_jwt_identity()
                if not current_user_public_id:
                    query = query.filter(Note.is_public == True)
            except:
                query = query.filter(Note.is_public == True)
        
        # Filter by owner username
        owner_username = request.args.get('owner', '').strip()
        if owner_username:
            query = query.join(Note.owner).filter(User.username == owner_username)
        
        return paginate_query(query)


@api.route('/recommended')
class NoteRecommended(Resource):
    @jwt_required()
    @api.doc(params={
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 10, max: 100)'
    })
    @api.marshal_with(_note_paginated)
    def get(self):
        """Get personalized note recommendations using multi-strategy algorithm"""
        try:
            current_user_public_id = get_jwt_identity()
            user = User.query.filter_by(public_id=current_user_public_id).first()
            
            if not user:
                return {'message': 'User not found'}, 404
            
            from ...models.tag import Tag
            from ...models.course import Course
            from ...models.associations import note_tags, user_bookmarks, course_users, note_courses
            from sqlalchemy import func, distinct
            from sqlalchemy.orm import joinedload
            
            # Build recommendation score
            scored_notes = {}
            
            # Strategy 1: Notes with tags from bookmarked notes (weight: 3)
            try:
                # Get tags from bookmarked notes
                bookmarked_note_ids = db.session.query(user_bookmarks.c.note_id).filter(
                    user_bookmarks.c.user_id == user.id
                ).subquery()
                
                bookmarked_tag_ids = db.session.query(note_tags.c.tag_id).filter(
                    note_tags.c.note_id.in_(bookmarked_note_ids)
                ).distinct().subquery()
                
                if db.session.query(bookmarked_tag_ids).first():
                    # Get notes with similar tags (excluding user's own notes and bookmarked notes)
                    similar_notes = db.session.query(Note).join(User, Note.owner_id == User.id).join(note_tags).filter(
                        note_tags.c.tag_id.in_(bookmarked_tag_ids),
                        Note.is_public == True,
                        Note.owner_id != user.id,
                        ~Note.id.in_(bookmarked_note_ids)  # Exclude already bookmarked
                    ).distinct().all()
                    
                    for note in similar_notes:
                        if note.public_id not in scored_notes:
                            scored_notes[note.public_id] = {'note': note, 'score': 0}
                        scored_notes[note.public_id]['score'] += 3
            except Exception as e:
                logger.warning(f"Strategy 1 (bookmarked tags) failed: {str(e)}")
            
            # Strategy 2: Notes from followed users (weight: 5)
            try:
                followed_users = user.following.all()
                if followed_users:
                    followed_user_ids = [u.id for u in followed_users]
                    notes_from_followed = Note.query.join(User, Note.owner_id == User.id).filter(
                        Note.owner_id.in_(followed_user_ids),
                        Note.is_public == True
                    ).all()
                    
                    for note in notes_from_followed:
                        if note.public_id not in scored_notes:
                            scored_notes[note.public_id] = {'note': note, 'score': 0}
                        scored_notes[note.public_id]['score'] += 5
            except Exception as e:
                logger.warning(f"Strategy 2 (followed users) failed: {str(e)}")
            
            # Strategy 3: Notes from user's enrolled courses (weight: 4)
            try:
                user_course_ids = db.session.query(course_users.c.course_id).filter(
                    course_users.c.user_id == user.id
                ).subquery()
                
                if db.session.query(user_course_ids).first():
                    notes_from_courses = db.session.query(Note).join(User, Note.owner_id == User.id).join(note_courses).filter(
                        note_courses.c.course_id.in_(user_course_ids),
                        Note.is_public == True,
                        Note.owner_id != user.id
                    ).distinct().all()
                    
                    for note in notes_from_courses:
                        if note.public_id not in scored_notes:
                            scored_notes[note.public_id] = {'note': note, 'score': 0}
                        scored_notes[note.public_id]['score'] += 4
            except Exception as e:
                logger.warning(f"Strategy 3 (course notes) failed: {str(e)}")
            
            # Strategy 4: Popular notes by view count (weight: 1)
            try:
                popular_notes = Note.query.join(User, Note.owner_id == User.id).filter(
                    Note.is_public == True,
                    Note.owner_id != user.id,
                    Note.view_count > 0
                ).order_by(Note.view_count.desc()).limit(20).all()
                
                for note in popular_notes:
                    if note.public_id not in scored_notes:
                        scored_notes[note.public_id] = {'note': note, 'score': 0}
                    scored_notes[note.public_id]['score'] += 1
            except Exception as e:
                logger.warning(f"Strategy 4 (popular notes) failed: {str(e)}")
            
            # Strategy 5: Recently created public notes (weight: 0.5)
            try:
                from datetime import datetime, timedelta
                recent_cutoff = datetime.utcnow() - timedelta(days=7)
                recent_notes = Note.query.join(User, Note.owner_id == User.id).filter(
                    Note.is_public == True,
                    Note.owner_id != user.id,
                    Note.created_at >= recent_cutoff
                ).order_by(Note.created_at.desc()).limit(15).all()
                
                for note in recent_notes:
                    if note.public_id not in scored_notes:
                        scored_notes[note.public_id] = {'note': note, 'score': 0}
                    scored_notes[note.public_id]['score'] += 0.5
            except Exception as e:
                logger.warning(f"Strategy 5 (recent notes) failed: {str(e)}")
            
            # Sort by score and extract notes
            if scored_notes:
                sorted_recommendations = sorted(
                    scored_notes.values(),
                    key=lambda x: (-x['score'], -x['note'].view_count, -x['note'].id)  # Secondary sort by views and ID
                )
                recommended_notes = [item['note'] for item in sorted_recommendations]
            else:
                # Fallback: return popular public notes if no recommendations
                recommended_notes = Note.query.join(User, Note.owner_id == User.id).filter(
                    Note.is_public == True,
                    Note.owner_id != user.id
                ).order_by(Note.view_count.desc()).limit(50).all()
            
            # Manually paginate the list
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            per_page = max(1, min(per_page, 100))
            page = max(1, page)
            
            start = (page - 1) * per_page
            end = start + per_page
            
            total = len(recommended_notes)
            items = recommended_notes[start:end]
            pages = (total + per_page - 1) // per_page if total > 0 else 1
            
            return {
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'has_next': page < pages,
                'has_prev': page > 1
            }
            
        except Exception as e:
            logger.error(f"Error in recommendations: {str(e)}", exc_info=True)
            # Return fallback recommendations
            try:
                fallback_notes = Note.query.join(User, Note.owner_id == User.id).filter(
                    Note.is_public == True
                ).order_by(Note.view_count.desc()).limit(10).all()
                
                return {
                    'items': fallback_notes,
                    'total': len(fallback_notes),
                    'pages': 1,
                    'current_page': 1,
                    'has_next': False,
                    'has_prev': False
                }
            except:
                return {
                    'items': [],
                    'total': 0,
                    'pages': 1,
                    'current_page': 1,
                    'has_next': False,
                    'has_prev': False
                }


@api.route('/<public_id>')
@api.param('public_id', 'The note identifier')
class NoteDetail(Resource):
    @api.marshal_with(_note_display)
    def get(self, public_id):
        """Fetch a given note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        if not note.is_public:
            # This would require auth and checking if user is owner or collaborator
            # For now, just return 403 if private
            return {'message': 'Access forbidden'}, 403
        
        # Increment view count
        if note.view_count is None:
            note.view_count = 1
        else:
            note.view_count += 1
        db.session.commit()
        
        return note

    @jwt_required()
    def put(self, public_id):
        """Update a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()

        if note.owner_id != user.id:
            return {'message': 'You are not the owner of this note'}, 403

        data = request.get_json()
        note.title = data.get('title', note.title)
        note.description = data.get('description', note.description)
        note.is_public = data.get('is_public', note.is_public)
        db.session.commit()
        return marshal(note, _note_display)

    @jwt_required()
    def delete(self, public_id):
        """Delete a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()

        # Allow deletion if user is the owner OR if user is an admin
        if note.owner_id != user.id and not user.is_admin:
            return {'message': 'You are not the owner of this note'}, 403
        
        logger.info(f"User {user.username} (admin: {user.is_admin}) deleting note {public_id}: {note.title}")
        
        # Optional: delete file from filesystem
        # import os
        # if os.path.exists(note.file_path):
        #     os.remove(note.file_path)

        db.session.delete(note)
        db.session.commit()
        return '', 204


@api.route('/<public_id>/comments')
@api.param('public_id', 'The note identifier')
class NoteComments(Resource):
    @api.marshal_list_with(_comment)
    def get(self, public_id):
        """Get all comments for a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        return note.comments
    
    @jwt_required()
    @api.expect(_comment_create, validate=True)
    def post(self, public_id):
        """Add a comment to a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        data = request.get_json()
        new_comment = Comment(
            content=data['content'],
            user_id=user.id,
            note_id=note.id
        )
        db.session.add(new_comment)
        db.session.commit()
        
        return marshal(new_comment, _comment), 201


@api.route('/<public_id>/react')
@api.param('public_id', 'The note identifier')
class NoteReactions(Resource):
    @jwt_required()
    @api.expect(_reaction_create, validate=True)
    def post(self, public_id):
        """React to a note (toggle reaction)"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        data = request.get_json()
        reaction_type = data['reaction_type']
        
        # Validate reaction type
        valid_reactions = ['concise', 'detailed', 'readable']
        if reaction_type not in valid_reactions:
            return {'message': f'Invalid reaction type. Must be one of: {", ".join(valid_reactions)}'}, 400
        
        # Check if user already reacted with this type
        existing_reaction = NoteReaction.query.filter_by(
            user_id=user.id,
            note_id=note.id,
            reaction_type=reaction_type
        ).first()
        
        if existing_reaction:
            # Toggle: remove the reaction
            db.session.delete(existing_reaction)
            db.session.commit()
            message = f'Reaction "{reaction_type}" removed'
        else:
            # Add new reaction
            new_reaction = NoteReaction(
                user_id=user.id,
                note_id=note.id,
                reaction_type=reaction_type
            )
            db.session.add(new_reaction)
            db.session.commit()
            message = f'Reaction "{reaction_type}" added'
        
        # Get reaction counts
        reaction_counts = {
            'concise': NoteReaction.query.filter_by(note_id=note.id, reaction_type='concise').count(),
            'detailed': NoteReaction.query.filter_by(note_id=note.id, reaction_type='detailed').count(),
            'readable': NoteReaction.query.filter_by(note_id=note.id, reaction_type='readable').count()
        }
        
        return {
            'message': message,
            'reactions': reaction_counts
        }, 200
    
    @api.marshal_with(_reaction_summary)
    def get(self, public_id):
        """Get reaction counts for a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        
        reaction_counts = {
            'concise': NoteReaction.query.filter_by(note_id=note.id, reaction_type='concise').count(),
            'detailed': NoteReaction.query.filter_by(note_id=note.id, reaction_type='detailed').count(),
            'readable': NoteReaction.query.filter_by(note_id=note.id, reaction_type='readable').count()
        }
        
        return reaction_counts


@api.route('/<public_id>/collaborators')
@api.param('public_id', 'The note identifier')
class NoteCollaborators(Resource):
    @api.marshal_list_with(_collaborator)
    def get(self, public_id):
        """Get all collaborators for a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        return note.collaborators
    
    @jwt_required()
    @api.expect(_collaborator_add, validate=True)
    def post(self, public_id):
        """Add a collaborator to a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        # Check if current user is the owner
        if note.owner_id != user.id:
            return {'message': 'Only the note owner can add collaborators'}, 403
        
        data = request.get_json()
        collaborator = User.query.filter_by(username=data['username']).first()
        
        if not collaborator:
            return {'message': 'User not found'}, 404
        
        # Check if already a collaborator
        if collaborator in note.collaborators:
            return {'message': 'User is already a collaborator'}, 400
        
        # Prevent adding owner as collaborator
        if collaborator.id == note.owner_id:
            return {'message': 'Cannot add note owner as collaborator'}, 400
        
        note.collaborators.append(collaborator)
        db.session.commit()
        
        return marshal(collaborator, _collaborator), 201


@api.route('/<public_id>/markdown')
@api.param('public_id', 'The note identifier')
class NoteMarkdown(Resource):
    def get(self, public_id):
        """Get the markdown content of a note"""
        logger.info(f"Markdown request for note: {public_id}")
        
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        logger.info(f"Found note: {note.title}, OCR status: {note.ocr_status}")
        
        # Check OCR status
        if note.ocr_status == 'pending':
            logger.info(f"Note {public_id} OCR is pending")
            return {'message': 'OCR conversion is pending', 'status': 'pending'}, 202
        elif note.ocr_status == 'processing':
            logger.info(f"Note {public_id} OCR is processing")
            return {'message': 'OCR conversion is in progress', 'status': 'processing'}, 202
        elif note.ocr_status == 'failed':
            logger.warning(f"Note {public_id} OCR failed")
            return {'message': 'OCR conversion failed', 'status': 'failed'}, 500
        
        # Check if markdown file exists with path correction
        if not note.markdown_path:
            logger.warning(f"Note {public_id} has no markdown path")
            return {'message': 'Markdown file not found', 'status': 'not_found'}, 404
        
        logger.info(f"Note {public_id} markdown path: {note.markdown_path}")
        corrected_path = fix_file_path(note.markdown_path)
        logger.info(f"Corrected markdown path: {corrected_path}")
        
        if not corrected_path or not os.path.exists(corrected_path):
            logger.error(f"Markdown file does not exist: {corrected_path}")
            return {'message': 'Markdown file not found', 'status': 'not_found'}, 404
        
        # Read and return markdown content
        try:
            with open(corrected_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            logger.info(f"Successfully loaded markdown for {public_id}, length: {len(markdown_content)}")
            return {
                'status': 'completed',
                'markdown': markdown_content,
                'file_path': note.markdown_path
            }, 200
        except Exception as e:
            logger.error(f"Error reading markdown file: {str(e)}")
            return {'message': 'Error reading markdown file', 'status': 'error'}, 500


@api.route('/<public_id>/markdown/status')
@api.param('public_id', 'The note identifier')
class NoteMarkdownStatus(Resource):
    def get(self, public_id):
        """Get markdown availability status for debugging"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        
        status_info = {
            'note_id': public_id,
            'title': note.title,
            'ocr_status': note.ocr_status,
            'has_markdown_path': bool(note.markdown_path),
            'markdown_path': note.markdown_path,
        }
        
        if note.markdown_path:
            corrected_path = fix_file_path(note.markdown_path)
            status_info['corrected_path'] = corrected_path
            status_info['file_exists'] = os.path.exists(corrected_path) if corrected_path else False
            
            if corrected_path and os.path.exists(corrected_path):
                try:
                    with open(corrected_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        status_info['file_size'] = len(content)
                        status_info['preview'] = content[:200] + '...' if len(content) > 200 else content
                except Exception as e:
                    status_info['read_error'] = str(e)
        
        return status_info, 200


@api.route('/<public_id>/file')
@api.param('public_id', 'The note identifier')
class NoteFileAccess(Resource):
    def get(self, public_id):
        """Access the original file (for viewing/downloading)"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        
        if not note.file_path:
            return {'message': 'File not found'}, 404
        
        # Fix file path and normalize separators for cross-platform compatibility
        corrected_path = fix_file_path(note.file_path)
        
        if not corrected_path or not os.path.exists(corrected_path):
            return {'message': 'File not found'}, 404
        
        # Increment view count (not download count for viewing)
        if note.view_count is None:
            note.view_count = 1
        else:
            note.view_count += 1
        db.session.commit()
        
        # Return file for viewing (not as attachment)
        return send_file(
            corrected_path,
            as_attachment=False,  # Allow inline viewing
            download_name=f"{note.title}.{note.file_path.split('.')[-1]}"
        )


@api.route('/<public_id>/download/original')
@api.param('public_id', 'The note identifier')
class NoteOriginalDownload(Resource):
    def get(self, public_id):
        """Download the original handwritten note (PDF/image)"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        
        if not note.file_path:
            return {'message': 'Original file not found'}, 404
        
        # Fix file path and normalize separators for cross-platform compatibility
        corrected_path = fix_file_path(note.file_path)
        
        if not corrected_path or not os.path.exists(corrected_path):
            return {'message': 'Original file not found'}, 404
        
        # Increment download count
        if note.download_count is None:
            note.download_count = 1
        else:
            note.download_count += 1
        db.session.commit()
        
        return send_file(
            corrected_path,
            as_attachment=True,
            download_name=f"{note.title}_original.{note.file_path.split('.')[-1]}"
        )


@api.route('/<public_id>/download/markdown')
@api.param('public_id', 'The note identifier')
class NoteMarkdownDownload(Resource):
    def get(self, public_id):
        """Download the markdown version of a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        
        if note.ocr_status != 'completed' or not note.markdown_path:
            return {'message': 'Markdown file not available'}, 404
        
        # Fix file path and normalize separators for cross-platform compatibility
        corrected_path = fix_file_path(note.markdown_path)
        
        if not corrected_path or not os.path.exists(corrected_path):
            return {'message': 'Markdown file not found'}, 404
        
        # Increment download count
        if note.download_count is None:
            note.download_count = 1
        else:
            note.download_count += 1
        db.session.commit()
        
        return send_file(
            corrected_path,
            as_attachment=True,
            download_name=f"{note.title}.md"
        )


@api.route('/<public_id>/ocr-status')
@api.param('public_id', 'The note identifier')
class NoteOCRStatus(Resource):
    def get(self, public_id):
        """Get the OCR conversion status of a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        
        return {
            'public_id': note.public_id,
            'title': note.title,
            'ocr_status': note.ocr_status,
            'has_markdown': note.markdown_path is not None,
            'markdown_path': note.markdown_path
        }, 200


@api.route('/<public_id>/bookmark')
@api.param('public_id', 'The note identifier')
class NoteBookmark(Resource):
    @jwt_required()
    def post(self, public_id):
        """Bookmark a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        # Check if already bookmarked
        if note in user.bookmarked_notes:
            return {'message': 'Note already bookmarked'}, 400
        
        user.bookmarked_notes.append(note)
        db.session.commit()
        
        return {'message': 'Note bookmarked successfully'}, 201
    
    @jwt_required()
    def delete(self, public_id):
        """Remove bookmark from a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        # Check if bookmarked
        if note not in user.bookmarked_notes:
            return {'message': 'Note not bookmarked'}, 400
        
        user.bookmarked_notes.remove(note)
        db.session.commit()
        
        return {'message': 'Bookmark removed successfully'}, 200


@api.route('/<public_id>/stats')
@api.param('public_id', 'The note identifier')
class NoteStats(Resource):
    def get(self, public_id):
        """Get statistics for a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        
        return {
            'public_id': note.public_id,
            'title': note.title,
            'view_count': note.view_count,
            'download_count': note.download_count,
            'comment_count': len(note.comments),
            'collaborator_count': len(note.collaborators),
            'bookmark_count': len(note.bookmarked_by),
            'reaction_counts': {
                'concise': sum(1 for r in note.reactions if r.reaction_type == 'concise'),
                'detailed': sum(1 for r in note.reactions if r.reaction_type == 'detailed'),
                'readable': sum(1 for r in note.reactions if r.reaction_type == 'readable')
            }
        }, 200
