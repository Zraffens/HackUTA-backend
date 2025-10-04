from flask import request
from flask_restx import Resource
from .dto import UserDto
from ...models.user import User
from ... import db

api = UserDto.api
_user = UserDto.user
_user_create = UserDto.user_create

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

@api.route('/<public_id>')
@api.param('public_id', 'User public ID')
class UserDetail(Resource):
    @api.marshal_with(_user)
    def get(self, public_id):
        user = User.query.filter_by(public_id=public_id).first_or_404()
        return user
