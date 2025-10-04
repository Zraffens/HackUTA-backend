from flask import Blueprint
from flask_restx import Api

from .auth.controller import api as auth_ns
from .notes.controller import api as notes_ns
# from .users.controller import api as users_ns
# from .courses.controller import api as courses_ns

api_bp = Blueprint('api', __name__)

api = Api(api_bp,
          title='Note-Sharing API',
          version='1.0',
          description='A REST API for a student note-sharing platform',
          )

api.add_namespace(auth_ns, path='/auth')
api.add_namespace(notes_ns, path='/notes')
# api.add_namespace(users_ns, path='/users')
# api.add_namespace(courses_ns, path='/courses')
