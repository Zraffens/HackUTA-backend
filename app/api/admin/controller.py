from flask import request, jsonify
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_

from app.extensions import db
from app.models import User, Note, Comment, Tag, Course
from app.models.associations import user_bookmarks
from app.utils.admin_auth import admin_required, get_current_admin
from .dto import (
    admin_ns, dashboard_stats_model, admin_user_list_model, admin_note_list_model,
    user_action_model, note_action_model, paginated_users_model, paginated_notes_model
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
                # For now, just hide it. Actual deletion would need file cleanup
                note.is_public = False
                message = f'Note "{note.title}" marked for deletion (hidden from public)'
                # TODO: Implement actual file deletion logic
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
