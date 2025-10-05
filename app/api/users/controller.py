from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .dto import UserDto
from ...models.user import User
from ...models.note import Note
from ...utils.pagination import paginate_query
from ... import db

api = UserDto.api
_user = UserDto.user
_user_create = UserDto.user_create
_user_profile = UserDto.user_profile

@api.route('')
class UserList(Resource):
    @api.doc(params={
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 10, max: 100)'
    })
    @api.marshal_list_with(_user)
    def get(self):
        # Note: For pagination, we'd need to add a paginated model to DTO
        # For now, keeping it simple
        return User.query.all()

    @api.expect(_user_create, validate=True)
    def post(self):
        data = request.get_json()
        new_user = User(email=data['email'], username=data['username'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201

@api.route('/<username>')
@api.param('username', 'Username')
class UserDetail(Resource):
    @api.marshal_with(_user_profile)
    def get(self, username):
        """Get user profile with stats"""
        user = User.query.filter_by(username=username).first_or_404()
        
        profile = {
            'public_id': user.public_id,
            'username': user.username,
            'profile_bio': user.profile_bio,
            'created_at': user.created_at,
            'followers_count': user.followers.count(),
            'following_count': user.following.count(),
            'notes_count': Note.query.filter_by(owner_id=user.id, is_public=True).count()
        }
        
        return profile


@api.route('/<username>/follow')
@api.param('username', 'Username to follow')
class UserFollow(Resource):
    @jwt_required()
    def post(self, username):
        """Follow a user"""
        current_user_public_id = get_jwt_identity()
        current_user = User.query.filter_by(public_id=current_user_public_id).first()
        user_to_follow = User.query.filter_by(username=username).first_or_404()
        
        # Prevent self-following
        if current_user.id == user_to_follow.id:
            return {'message': 'You cannot follow yourself'}, 400
        
        # Check if already following
        if user_to_follow in current_user.following.all():
            return {'message': 'You are already following this user'}, 400
        
        current_user.following.append(user_to_follow)
        db.session.commit()
        
        return {'message': f'You are now following {username}'}, 200


@api.route('/<username>/unfollow')
@api.param('username', 'Username to unfollow')
class UserUnfollow(Resource):
    @jwt_required()
    def post(self, username):
        """Unfollow a user"""
        current_user_public_id = get_jwt_identity()
        current_user = User.query.filter_by(public_id=current_user_public_id).first()
        user_to_unfollow = User.query.filter_by(username=username).first_or_404()
        
        # Check if following
        if user_to_unfollow not in current_user.following.all():
            return {'message': 'You are not following this user'}, 400
        
        current_user.following.remove(user_to_unfollow)
        db.session.commit()
        
        return {'message': f'You have unfollowed {username}'}, 200


@api.route('/me/bookmarks')
class UserBookmarks(Resource):
    @jwt_required()
    @api.doc(params={
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 10, max: 100)'
    })
    def get(self):
        """Get current user's bookmarked notes (paginated)"""
        from ...api.notes.dto import NoteDto
        from ...models.associations import user_bookmarks
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        # Get paginated bookmarks using a proper query
        bookmarks_query = Note.query.join(user_bookmarks).filter(
            user_bookmarks.c.user_id == user.id
        ).order_by(user_bookmarks.c.bookmarked_at.desc())
        
        result = paginate_query(bookmarks_query)
        
        # Marshal the notes
        from flask_restx import marshal
        result['items'] = marshal(result['items'], NoteDto.note_display)
        
        return result, 200


@api.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    def get(self):
        """Get current user's profile information"""
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        if not user:
            return {'message': 'User not found'}, 404
        
        return {
            'public_id': user.public_id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'profile_bio': user.profile_bio,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }, 200


@api.route('/me')
class UserMe(Resource):
    @jwt_required()
    @api.marshal_with(_user)
    def get(self):
        """Get current user's details"""
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        if not user:
            return {'message': 'User not found'}, 404
        
        return user, 200


@api.route('/me/stats')
class UserStats(Resource):
    @jwt_required()
    def get(self):
        """Get current user's statistics"""
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        # Calculate total views and downloads across all notes
        total_views = sum(note.view_count for note in user.notes)
        total_downloads = sum(note.download_count for note in user.notes)
        
        return {
            'username': user.username,
            'total_notes': len(user.notes),
            'public_notes': sum(1 for note in user.notes if note.is_public),
            'private_notes': sum(1 for note in user.notes if not note.is_public),
            'total_views': total_views,
            'total_downloads': total_downloads,
            'followers_count': user.followers.count(),
            'following_count': user.following.count(),
            'bookmarks_count': len(user.bookmarked_notes),
            'comments_count': len(user.comments)
        }, 200
