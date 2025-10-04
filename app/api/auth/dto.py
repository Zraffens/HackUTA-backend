from flask_restx import Namespace, fields

class AuthDto:
    api = Namespace('auth', description='Authentication related operations')
    user_register = api.model('UserRegister', {
        'email': fields.String(required=True, description='user email address'),
        'username': fields.String(required=True, description='user username'),
        'password': fields.String(required=True, description='user password'),
    })
    user_login = api.model('UserLogin', {
        'email': fields.String(required=True, description='user email address'),
        'password': fields.String(required=True, description='user password'),
    })
    tokens = api.model('Tokens', {
        'access_token': fields.String(description='access token'),
        'refresh_token': fields.String(description='refresh token'),
    })
