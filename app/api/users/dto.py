from flask_restx import Namespace, fields

class UserDto:
    api = Namespace('users', description='User related operations')
    user = api.model('User', {
        'public_id': fields.String,
        'email': fields.String,
        'username': fields.String,
        'profile_bio': fields.String,
        'created_at': fields.DateTime,
    })
    user_create = api.model('UserCreate', {
        'email': fields.String(required=True),
        'username': fields.String(required=True),
        'password': fields.String(required=True),
    })
