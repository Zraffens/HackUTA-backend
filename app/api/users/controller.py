from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .dto import UserDto
from ...models.user import User
from ...models.note import Note
from ... import db

api = UserDto.api
_user = UserDto.user
_user_create = UserDto.user_create
_user_profile = UserDto.user_profile

@api.route('')
class UserList(Resource):
    @api.marshal_list_with(_user)
    def get(self):
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
