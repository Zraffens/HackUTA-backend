from flask import request, jsonify
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import uuid

from app.extensions import db
from app.models import User, Note, Comment, Tag, Course
from app.models.associations import user_bookmarks
from app.utils.admin_auth import admin_required, get_current_admin
from app.services.file_service import fix_file_path
from .dto import (
    admin_ns, dashboard_stats_model, admin_user_list_model, admin_note_list_model,
    user_action_model, note_action_model, paginated_users_model, paginated_notes_model,
    user_create_admin_model, note_create_admin_model, comment_admin_model, comment_action_model,
    tag_admin_model, tag_action_model, tag_create_model, course_admin_model, course_action_model,
    course_create_model, paginated_comments_model, paginated_tags_model, paginated_courses_model
)


@admin_ns.route('/dashboard/stats')
class AdminDashboardStats(Resource):
    @admin_ns.doc('get_dashboard_statistics')
    @admin_ns.marshal_with(dashboard_stats_model)
    @jwt_required()
    @admin_required
    def get(self):
        """Get comprehensive dashboard statistics for admin panel"""
        try:
            # Calculate date ranges
            today = datetime.utcnow().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # User Statistics
            total_users = User.query.count()
            admin_users = User.query.filter_by(is_admin=True).count()
            new_users_today = User.query.filter(func.date(User.created_at) == today).count()
            new_users_this_week = User.query.filter(func.date(User.created_at) >= week_ago).count()
            new_users_this_month = User.query.filter(func.date(User.created_at) >= month_ago).count()
            
            # Note Statistics
            total_notes = Note.query.count()
            public_notes = Note.query.filter_by(is_public=True).count()
            private_notes = Note.query.filter_by(is_public=False).count()
            notes_today = Note.query.filter(func.date(Note.created_at) == today).count()
            notes_this_week = Note.query.filter(func.date(Note.created_at) >= week_ago).count()
            notes_this_month = Note.query.filter(func.date(Note.created_at) >= month_ago).count()
            
            # View and download stats
            total_views = db.session.query(func.sum(Note.view_count)).scalar() or 0
            total_downloads = db.session.query(func.sum(Note.download_count)).scalar() or 0
            
            # System Statistics
            total_comments = Comment.query.count()
            total_bookmarks = db.session.query(user_bookmarks).count()
            total_tags = Tag.query.count()
            total_courses = Course.query.count()
            
            return {
                'user_stats': {
                    'total_users': total_users,
                    'admin_users': admin_users,
                    'new_users_today': new_users_today,
                    'new_users_this_week': new_users_this_week,
                    'new_users_this_month': new_users_this_month
                },
                'note_stats': {
                    'total_notes': total_notes,
                    'public_notes': public_notes,
                    'private_notes': private_notes,
                    'notes_today': notes_today,
                    'notes_this_week': notes_this_week,
                    'notes_this_month': notes_this_month,
                    'total_views': total_views,
                    'total_downloads': total_downloads
                },
                'system_stats': {
                    'total_comments': total_comments,
                    'total_bookmarks': total_bookmarks,
                    'total_tags': total_tags,
                    'total_courses': total_courses
                }
            }
        
        except Exception as e:
            return {'message': f'Error retrieving dashboard stats: {str(e)}'}, 500


@admin_ns.route('/users')
class AdminUserManagement(Resource):
    @admin_ns.doc('get_all_users')
    @admin_ns.marshal_with(paginated_users_model)
    @jwt_required()
    @admin_required
    def get(self):
        """Get paginated list of all users for admin management"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '', type=str)
            
            # Build query
            query = User.query
            
            if search:
                query = query.filter(
                    db.or_(
                        User.username.contains(search),
                        User.email.contains(search),
                        User.full_name.contains(search) if hasattr(User, 'full_name') else False
                    )
                )
            
            # Order by creation date (newest first)
            query = query.order_by(User.created_at.desc())
            
            # Paginate
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            users_data = []
            for user in pagination.items:
                notes_count = Note.query.filter_by(owner_id=user.id).count()
                users_data.append({
                    'id': user.id,
                    'public_id': user.public_id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': getattr(user, 'full_name', user.username),
                    'is_admin': user.is_admin,
                    'created_at': user.created_at,
                    'notes_count': notes_count,
                    'last_login': None  # Would need to implement login tracking
                })
            
            return {
                'users': users_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        
        except Exception as e:
            return {'message': f'Error retrieving users: {str(e)}'}, 500


@admin_ns.route('/users/<string:user_id>/action')
class AdminUserAction(Resource):
    @admin_ns.doc('perform_user_action')
    @admin_ns.expect(user_action_model)
    @jwt_required()
    @admin_required
    def post(self, user_id):
        """Perform administrative actions on a user"""
        try:
            data = request.get_json()
            action = data.get('action')
            
            user = User.query.filter_by(public_id=user_id).first()
            if not user:
                return {'message': 'User not found'}, 404
            
            current_admin = get_current_admin()
            
            # Prevent admin from demoting themselves
            if action == 'demote' and user.id == current_admin.id:
                return {'message': 'Cannot demote yourself'}, 400
            
            if action == 'promote':
                user.is_admin = True
                message = f'User {user.username} promoted to admin'
            elif action == 'demote':
                user.is_admin = False
                message = f'User {user.username} demoted from admin'
            elif action == 'delete':
                username = user.username
                db.session.delete(user)
                db.session.commit()
                return {'message': f'User {username} deleted successfully'}, 200
            elif action == 'suspend':
                # Would need to implement user suspension logic
                message = f'User {user.username} suspended (feature to be implemented)'
            elif action == 'activate':
                # Would need to implement user activation logic
                message = f'User {user.username} activated (feature to be implemented)'
            else:
                return {'message': 'Invalid action'}, 400
            
            db.session.commit()
            return {'message': message}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error performing user action: {str(e)}'}, 500


@admin_ns.route('/notes')
class AdminNoteManagement(Resource):
    @admin_ns.doc('get_all_notes')
    @admin_ns.marshal_with(paginated_notes_model)
    @jwt_required()
    @admin_required
    def get(self):
        """Get paginated list of all notes for admin management"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '', type=str)
            status_filter = request.args.get('status', '', type=str)
            
            # Build query with join to get owner information
            query = Note.query.join(User, Note.owner_id == User.id)
            
            if search:
                query = query.filter(
                    db.or_(
                        Note.title.contains(search),
                        User.username.contains(search)
                    )
                )
            
            if status_filter:
                if status_filter == 'public':
                    query = query.filter(Note.is_public == True)
                elif status_filter == 'private':
                    query = query.filter(Note.is_public == False)
                elif status_filter in ['pending', 'processing', 'completed', 'failed']:
                    query = query.filter(Note.ocr_status == status_filter)
            
            # Order by creation date (newest first)
            query = query.order_by(Note.created_at.desc())
            
            # Paginate
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            notes_data = []
            for note in pagination.items:
                notes_data.append({
                    'id': note.id,
                    'public_id': note.public_id,
                    'title': note.title,
                    'owner_username': note.owner.username,
                    'is_public': note.is_public,
                    'view_count': note.view_count,
                    'download_count': note.download_count,
                    'created_at': note.created_at,
                    'ocr_status': note.ocr_status
                })
            
            return {
                'notes': notes_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        
        except Exception as e:
            return {'message': f'Error retrieving notes: {str(e)}'}, 500


@admin_ns.route('/notes/<string:note_id>/action')
class AdminNoteAction(Resource):
    @admin_ns.doc('perform_note_action')
    @admin_ns.expect(note_action_model)
    @jwt_required()
    @admin_required
    def post(self, note_id):
        """Perform administrative actions on a note"""
        try:
            data = request.get_json()
            action = data.get('action')
            
            note = Note.query.filter_by(public_id=note_id).first()
            if not note:
                return {'message': 'Note not found'}, 404
            
            if action == 'hide':
                note.is_public = False
                message = f'Note "{note.title}" hidden from public view'
            elif action == 'unhide':
                note.is_public = True
                message = f'Note "{note.title}" made public'
            elif action == 'delete':
                # Soft delete - just hide it
                note.is_public = False
                message = f'Note "{note.title}" hidden from public (soft delete)'
            elif action == 'force_delete':
                # Hard delete with file cleanup
                import os
                
                note_title = note.title
                files_deleted = []
                
                if note.file_path:
                    corrected_file_path = fix_file_path(note.file_path)
                    if corrected_file_path and os.path.exists(corrected_file_path):
                        os.remove(corrected_file_path)
                        files_deleted.append('original file')
                
                if note.markdown_path:
                    corrected_markdown_path = fix_file_path(note.markdown_path)
                    if corrected_markdown_path and os.path.exists(corrected_markdown_path):
                        os.remove(corrected_markdown_path)
                        files_deleted.append('markdown file')
                
                db.session.delete(note)
                db.session.commit()
                
                return {
                    'message': f'Note "{note_title}" permanently deleted',
                    'files_deleted': files_deleted
                }, 200
            else:
                return {'message': 'Invalid action'}, 400
            
            db.session.commit()
            return {'message': message}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error performing note action: {str(e)}'}, 500


@admin_ns.route('/system/cleanup')
class AdminSystemCleanup(Resource):
    @admin_ns.doc('system_cleanup')
    @jwt_required()
    @admin_required
    def post(self):
        """Perform system cleanup tasks"""
        try:
            # TODO: Implement cleanup tasks like:
            # - Remove orphaned files
            # - Clean up failed OCR processing
            # - Remove temporary files
            # - Database maintenance
            
            return {'message': 'System cleanup initiated (feature to be implemented)'}, 200
        
        except Exception as e:
            return {'message': f'Error during system cleanup: {str(e)}'}, 500


@admin_ns.route('/analytics/popular-notes')
class AdminPopularNotes(Resource):
    @admin_ns.doc('get_popular_notes')
    @jwt_required()
    @admin_required
    def get(self):
        """Get most popular notes by views and downloads"""
        try:
            limit = request.args.get('limit', 10, type=int)
            
            # Most viewed notes
            most_viewed = Note.query.filter_by(is_public=True)\
                .order_by(Note.view_count.desc())\
                .limit(limit).all()
            
            # Most downloaded notes
            most_downloaded = Note.query.filter_by(is_public=True)\
                .order_by(Note.download_count.desc())\
                .limit(limit).all()
            
            viewed_data = [{
                'id': note.public_id,
                'title': note.title,
                'owner': note.owner.username,
                'view_count': note.view_count,
                'created_at': note.created_at
            } for note in most_viewed]
            
            downloaded_data = [{
                'id': note.public_id,
                'title': note.title,
                'owner': note.owner.username,
                'download_count': note.download_count,
                'created_at': note.created_at
            } for note in most_downloaded]
            
            return {
                'most_viewed': viewed_data,
                'most_downloaded': downloaded_data
            }, 200
        
        except Exception as e:
            return {'message': f'Error retrieving popular notes: {str(e)}'}, 500


# =============================================================================
# COMPREHENSIVE CRUD OPERATIONS FOR ALL ENTITIES
# =============================================================================

@admin_ns.route('/users/create')
class AdminCreateUser(Resource):
    @admin_ns.doc('create_user')
    @admin_ns.expect(user_create_admin_model)
    @jwt_required()
    @admin_required
    def post(self):
        """Create a new user (admin only)"""
        try:
            data = request.get_json()
            
            # Check if username or email already exists
            existing_user = User.query.filter(
                (User.username == data['username']) | 
                (User.email == data['email'])
            ).first()
            
            if existing_user:
                return {'message': 'Username or email already exists'}, 400
            
            # Create new user
            new_user = User(
                public_id=str(uuid.uuid4()),
                username=data['username'],
                email=data['email'],
                is_admin=data.get('is_admin', False),
                profile_bio=data.get('profile_bio', '')
            )
            new_user.set_password(data['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            return {
                'message': f'User {data["username"]} created successfully',
                'user_id': new_user.public_id
            }, 201
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating user: {str(e)}'}, 500


@admin_ns.route('/users/<string:user_id>/delete')
class AdminDeleteUser(Resource):
    @admin_ns.doc('delete_user')
    @jwt_required()
    @admin_required
    def delete(self, user_id):
        """Permanently delete a user and all associated data"""
        try:
            user = User.query.filter_by(public_id=user_id).first()
            if not user:
                return {'message': 'User not found'}, 404
            
            current_admin = get_current_admin()
            
            # Prevent admin from deleting themselves
            if user.id == current_admin.id:
                return {'message': 'Cannot delete yourself'}, 400
            
            username = user.username
            
            # Delete associated data
            # Notes will be cascade deleted due to foreign key constraints
            # Comments will be cascade deleted
            # Bookmarks will be cascade deleted
            
            db.session.delete(user)
            db.session.commit()
            
            return {'message': f'User {username} and all associated data deleted successfully'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting user: {str(e)}'}, 500


@admin_ns.route('/notes/<string:note_id>/delete')
class AdminDeleteNote(Resource):
    @admin_ns.doc('force_delete_note')
    @jwt_required()
    @admin_required
    def delete(self, note_id):
        """Permanently delete a note and associated files"""
        try:
            import os
            
            note = Note.query.filter_by(public_id=note_id).first()
            if not note:
                return {'message': 'Note not found'}, 404
            
            note_title = note.title
            
            # Delete physical files with path correction
            files_deleted = []
            if note.file_path:
                corrected_file_path = fix_file_path(note.file_path)
                if corrected_file_path and os.path.exists(corrected_file_path):
                    os.remove(corrected_file_path)
                    files_deleted.append('original file')
            
            if note.markdown_path:
                corrected_markdown_path = fix_file_path(note.markdown_path)
                if corrected_markdown_path and os.path.exists(corrected_markdown_path):
                    os.remove(corrected_markdown_path)
                    files_deleted.append('markdown file')
            
            # Delete from database (comments and bookmarks will cascade)
            db.session.delete(note)
            db.session.commit()
            
            return {
                'message': f'Note "{note_title}" deleted successfully',
                'files_deleted': files_deleted
            }, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting note: {str(e)}'}, 500


@admin_ns.route('/comments')
class AdminCommentManagement(Resource):
    @admin_ns.doc('get_all_comments')
    @admin_ns.marshal_with(paginated_comments_model)
    @jwt_required()
    @admin_required
    def get(self):
        """Get paginated list of all comments"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '', type=str)
            
            # Build query with joins
            query = Comment.query.join(User, Comment.user_id == User.id)\
                                 .join(Note, Comment.note_id == Note.id)
            
            if search:
                query = query.filter(
                    db.or_(
                        Comment.content.contains(search),
                        User.username.contains(search),
                        Note.title.contains(search)
                    )
                )
            
            query = query.order_by(Comment.created_at.desc())
            
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            comments_data = []
            for comment in pagination.items:
                comments_data.append({
                    'id': comment.id,
                    'content': comment.content[:200] + '...' if len(comment.content) > 200 else comment.content,
                    'author_username': comment.author.username,
                    'note_title': comment.note.title,
                    'note_id': comment.note.public_id,
                    'created_at': comment.created_at
                })
            
            return {
                'comments': comments_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        
        except Exception as e:
            return {'message': f'Error retrieving comments: {str(e)}'}, 500


@admin_ns.route('/comments/<int:comment_id>')
class AdminCommentAction(Resource):
    @admin_ns.doc('delete_comment')
    @jwt_required()
    @admin_required
    def delete(self, comment_id):
        """Delete a comment"""
        try:
            comment = Comment.query.get(comment_id)
            if not comment:
                return {'message': 'Comment not found'}, 404
            
            db.session.delete(comment)
            db.session.commit()
            
            return {'message': 'Comment deleted successfully'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting comment: {str(e)}'}, 500


@admin_ns.route('/tags')
class AdminTagManagement(Resource):
    @admin_ns.doc('get_all_tags')
    @admin_ns.marshal_with(paginated_tags_model)
    @jwt_required()
    @admin_required
    def get(self):
        """Get paginated list of all tags"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '', type=str)
            
            query = Tag.query
            
            if search:
                query = query.filter(Tag.name.contains(search))
            
            query = query.order_by(Tag.name)
            
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            tags_data = []
            for tag in pagination.items:
                notes_count = len(tag.notes) if tag.notes else 0
                tags_data.append({
                    'id': tag.id,
                    'name': tag.name,
                    'created_at': getattr(tag, 'created_at', None),
                    'notes_count': notes_count
                })
            
            return {
                'tags': tags_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        
        except Exception as e:
            return {'message': f'Error retrieving tags: {str(e)}'}, 500
    
    @admin_ns.doc('create_tag')
    @admin_ns.expect(tag_create_model)
    @jwt_required()
    @admin_required
    def post(self):
        """Create a new tag"""
        try:
            data = request.get_json()
            
            # Check if tag already exists
            existing_tag = Tag.query.filter_by(name=data['name']).first()
            if existing_tag:
                return {'message': 'Tag already exists'}, 400
            
            new_tag = Tag(name=data['name'])
            db.session.add(new_tag)
            db.session.commit()
            
            return {
                'message': f'Tag "{data["name"]}" created successfully',
                'tag_id': new_tag.id
            }, 201
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating tag: {str(e)}'}, 500


@admin_ns.route('/tags/<int:tag_id>')
class AdminTagAction(Resource):
    @admin_ns.doc('delete_tag')
    @jwt_required()
    @admin_required
    def delete(self, tag_id):
        """Delete a tag (removes from all notes)"""
        try:
            tag = Tag.query.get(tag_id)
            if not tag:
                return {'message': 'Tag not found'}, 404
            
            tag_name = tag.name
            
            db.session.delete(tag)
            db.session.commit()
            
            return {'message': f'Tag "{tag_name}" deleted successfully'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting tag: {str(e)}'}, 500


@admin_ns.route('/courses')
class AdminCourseManagement(Resource):
    @admin_ns.doc('get_all_courses')
    @admin_ns.marshal_with(paginated_courses_model)
    @jwt_required()
    @admin_required
    def get(self):
        """Get paginated list of all courses"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '', type=str)
            
            query = Course.query
            
            if search:
                query = query.filter(
                    db.or_(
                        Course.name.contains(search),
                        Course.code.contains(search)
                    )
                )
            
            query = query.order_by(Course.name)
            
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            courses_data = []
            for course in pagination.items:
                notes_count = len(course.notes) if course.notes else 0
                students_count = len(course.enrolled_students) if course.enrolled_students else 0
                courses_data.append({
                    'id': course.id,
                    'name': course.name,
                    'code': course.code,
                    'created_at': getattr(course, 'created_at', None),
                    'notes_count': notes_count,
                    'students_count': students_count
                })
            
            return {
                'courses': courses_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        
        except Exception as e:
            return {'message': f'Error retrieving courses: {str(e)}'}, 500
    
    @admin_ns.doc('create_course')
    @admin_ns.expect(course_create_model)
    @jwt_required()
    @admin_required
    def post(self):
        """Create a new course"""
        try:
            data = request.get_json()
            
            # Check if course code already exists
            existing_course = Course.query.filter_by(code=data['code']).first()
            if existing_course:
                return {'message': 'Course code already exists'}, 400
            
            new_course = Course(
                name=data['name'],
                code=data['code'],
                description=data.get('description', '')
            )
            db.session.add(new_course)
            db.session.commit()
            
            return {
                'message': f'Course "{data["name"]}" created successfully',
                'course_id': new_course.id
            }, 201
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating course: {str(e)}'}, 500


@admin_ns.route('/courses/<int:course_id>')
class AdminCourseAction(Resource):
    @admin_ns.doc('delete_course')
    @jwt_required()
    @admin_required
    def delete(self, course_id):
        """Delete a course (removes from all notes and students)"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return {'message': 'Course not found'}, 404
            
            course_name = course.name
            
            db.session.delete(course)
            db.session.commit()
            
            return {'message': f'Course "{course_name}" deleted successfully'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting course: {str(e)}'}, 500


@admin_ns.route('/bulk-actions/users')
class AdminBulkUserActions(Resource):
    @admin_ns.doc('bulk_user_actions')
    @jwt_required()
    @admin_required
    def post(self):
        """Perform bulk actions on multiple users"""
        try:
            data = request.get_json()
            user_ids = data.get('user_ids', [])
            action = data.get('action')
            
            if not user_ids or not action:
                return {'message': 'user_ids and action are required'}, 400
            
            current_admin = get_current_admin()
            results = []
            
            for user_id in user_ids:
                user = User.query.filter_by(public_id=user_id).first()
                if not user:
                    results.append({'user_id': user_id, 'status': 'not_found'})
                    continue
                
                # Prevent admin from affecting themselves
                if user.id == current_admin.id:
                    results.append({'user_id': user_id, 'status': 'cannot_modify_self'})
                    continue
                
                if action == 'delete':
                    db.session.delete(user)
                    results.append({'user_id': user_id, 'status': 'deleted'})
                elif action == 'promote':
                    user.is_admin = True
                    results.append({'user_id': user_id, 'status': 'promoted'})
                elif action == 'demote':
                    user.is_admin = False
                    results.append({'user_id': user_id, 'status': 'demoted'})
                else:
                    results.append({'user_id': user_id, 'status': 'invalid_action'})
            
            db.session.commit()
            
            return {
                'message': f'Bulk action {action} completed',
                'results': results
            }, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error performing bulk action: {str(e)}'}, 500


@admin_ns.route('/bulk-actions/notes')
class AdminBulkNoteActions(Resource):
    @admin_ns.doc('bulk_note_actions')
    @jwt_required()
    @admin_required
    def post(self):
        """Perform bulk actions on multiple notes"""
        try:
            data = request.get_json()
            note_ids = data.get('note_ids', [])
            action = data.get('action')
            
            if not note_ids or not action:
                return {'message': 'note_ids and action are required'}, 400
            
            results = []
            
            for note_id in note_ids:
                note = Note.query.filter_by(public_id=note_id).first()
                if not note:
                    results.append({'note_id': note_id, 'status': 'not_found'})
                    continue
                
                if action == 'delete':
                    # Delete physical files with path correction
                    import os
                    if note.file_path:
                        corrected_file_path = fix_file_path(note.file_path)
                        if corrected_file_path and os.path.exists(corrected_file_path):
                            os.remove(corrected_file_path)
                    if note.markdown_path:
                        corrected_markdown_path = fix_file_path(note.markdown_path)
                        if corrected_markdown_path and os.path.exists(corrected_markdown_path):
                            os.remove(corrected_markdown_path)
                    
                    db.session.delete(note)
                    results.append({'note_id': note_id, 'status': 'deleted'})
                elif action == 'hide':
                    note.is_public = False
                    results.append({'note_id': note_id, 'status': 'hidden'})
                elif action == 'unhide':
                    note.is_public = True
                    results.append({'note_id': note_id, 'status': 'unhidden'})
                else:
                    results.append({'note_id': note_id, 'status': 'invalid_action'})
            
            db.session.commit()
            
            return {
                'message': f'Bulk action {action} completed',
                'results': results
            }, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error performing bulk action: {str(e)}'}, 500


@admin_ns.route('/system/database-cleanup')
class AdminDatabaseCleanup(Resource):
    @admin_ns.doc('database_cleanup')
    @jwt_required()
    @admin_required
    def post(self):
        """Perform database cleanup operations"""
        try:
            cleanup_results = {}
            
            # Clean up orphaned comments (comments without notes)
            orphaned_comments = Comment.query.filter(~Comment.note_id.in_(
                db.session.query(Note.id)
            )).all()
            
            for comment in orphaned_comments:
                db.session.delete(comment)
            
            cleanup_results['orphaned_comments_removed'] = len(orphaned_comments)
            
            # Clean up empty tags (tags with no notes)
            empty_tags = Tag.query.filter(~Tag.id.in_(
                db.session.query(Note.tags.property.local_side)
            )).all()
            
            for tag in empty_tags:
                db.session.delete(tag)
            
            cleanup_results['empty_tags_removed'] = len(empty_tags)
            
            # Update null counters
            null_view_notes = Note.query.filter(Note.view_count.is_(None)).all()
            null_download_notes = Note.query.filter(Note.download_count.is_(None)).all()
            
            for note in null_view_notes:
                note.view_count = 0
            
            for note in null_download_notes:
                note.download_count = 0
            
            cleanup_results['null_counters_fixed'] = len(null_view_notes) + len(null_download_notes)
            
            db.session.commit()
            
            return {
                'message': 'Database cleanup completed',
                'results': cleanup_results
            }, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error during database cleanup: {str(e)}'}, 500
