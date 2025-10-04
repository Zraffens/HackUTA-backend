from flask_restx import Namespace, fields
from werkzeug.datastructures import FileStorage

class NoteDto:
    api = Namespace('notes', description='Notes related operations')
    
    note_owner = api.model('NoteOwner', {
        'username': fields.String(description='owner username'),
    })

    note_display = api.model('NoteDisplay', {
        'public_id': fields.String(description='note public id'),
        'title': fields.String(description='note title'),
        'description': fields.String(description='note description'),
        'is_public': fields.Boolean(description='is note public'),
        'created_at': fields.DateTime(description='note creation date'),
        'owner': fields.Nested(note_owner)
    })

    note_create = api.parser()
    note_create.add_argument('title', type=str, required=True, help='Title of the note', location='form')
    note_create.add_argument('description', type=str, help='Description of the note', location='form')
    note_create.add_argument('is_public', type=bool, default=True, help='Is the note public?', location='form')
    note_create.add_argument('file', type=FileStorage, required=True, help='The note PDF file', location='files')
