from flask import request
from flask_restx import Resource, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from .dto import NoteDto
from ...models.note import Note
from ...models.user import User
from ...models.comment import Comment
from ...models.reaction import NoteReaction
from ...services.file_service import save_file
from ... import db

api = NoteDto.api
_note_display = NoteDto.note_display
_note_create = NoteDto.note_create
_comment = NoteDto.comment
_comment_create = NoteDto.comment_create
_reaction_create = NoteDto.reaction_create
_reaction_summary = NoteDto.reaction_summary
_collaborator_add = NoteDto.collaborator_add
_collaborator = NoteDto.collaborator

@api.route('')
class NoteList(Resource):
    @api.marshal_list_with(_note_display)
    def get(self):
        """List all public notes"""
        return Note.query.filter_by(is_public=True).all()

    @jwt_required()
    @api.expect(_note_create, validate=True)
    def post(self):
        """Create a new note"""
        args = _note_create.parse_args()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()

        file = args['file']
        file_path = save_file(file)
        if not file_path:
            return {'message': 'File type not allowed or file save failed'}, 400

        new_note = Note(
            title=args['title'],
            description=args['description'],
            is_public=args['is_public'],
            owner_id=user.id,
            file_path=file_path
        )
        db.session.add(new_note)
        db.session.commit()
        
        return marshal(new_note, _note_display), 201

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

        if note.owner_id != user.id:
            return {'message': 'You are not the owner of this note'}, 403
        
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
