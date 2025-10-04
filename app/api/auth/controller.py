from flask import request
from flask_restx import Resource
from ..auth.dto import AuthDto
from ...models.user import User
from ... import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from ...models.blocklist import BlocklistedToken

api = AuthDto.api
_user_register = AuthDto.user_register
_user_login = AuthDto.user_login

@api.route('/register')
class UserRegister(Resource):
    @api.expect(_user_register, validate=True)
    def post(self):
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 409
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already taken'}, 409
        
        new_user = User(
            email=data['email'],
            username=data['username']
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

@api.route('/login')
class UserLogin(Resource):
    @api.expect(_user_login, validate=True)
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.public_id)
            refresh_token = create_refresh_token(identity=user.public_id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        return {'message': 'Invalid credentials'}, 401

@api.route('/refresh')
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return {'access_token': new_access_token}, 200

@api.route('/logout')
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        blocklisted_token = BlocklistedToken(jti=jti)
        db.session.add(blocklisted_token)
        db.session.commit()
        return {'message': 'Successfully logged out'}, 200
