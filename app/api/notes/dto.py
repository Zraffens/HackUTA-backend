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
        'owner': fields.Nested(note_owner),
        'ocr_status': fields.String(description='OCR conversion status: pending, processing, completed, failed'),
        'has_markdown': fields.Boolean(description='Whether markdown version is available')
    })
    
    note_paginated = api.model('NotePaginated', {
        'items': fields.List(fields.Nested(note_display)),
        'total': fields.Integer(description='Total number of items'),
        'pages': fields.Integer(description='Total number of pages'),
        'current_page': fields.Integer(description='Current page number'),
        'has_next': fields.Boolean(description='Whether there is a next page'),
        'has_prev': fields.Boolean(description='Whether there is a previous page')
    })

    note_create = api.parser()
    note_create.add_argument('title', type=str, required=True, help='Title of the note', location='form')
    note_create.add_argument('description', type=str, help='Description of the note', location='form')
    note_create.add_argument('is_public', type=bool, default=True, help='Is the note public?', location='form')
    note_create.add_argument('file', type=FileStorage, required=True, help='The note PDF file', location='files')
    
    # Comment DTOs
    comment_author = api.model('CommentAuthor', {
        'username': fields.String(description='comment author username'),
    })
    
    comment = api.model('Comment', {
        'id': fields.Integer(description='comment id'),
        'content': fields.String(description='comment content'),
        'created_at': fields.DateTime(description='comment creation date'),
        'author': fields.Nested(comment_author)
    })
    
    comment_create = api.model('CommentCreate', {
        'content': fields.String(required=True, description='comment content')
    })
    
    # Reaction DTOs
    reaction_create = api.model('ReactionCreate', {
        'reaction_type': fields.String(required=True, description='Type of reaction: concise, detailed, or readable')
    })
    
    reaction_summary = api.model('ReactionSummary', {
        'concise': fields.Integer(description='Number of concise reactions'),
        'detailed': fields.Integer(description='Number of detailed reactions'),
        'readable': fields.Integer(description='Number of readable reactions')
    })
    
    # Collaborator DTOs
    collaborator_add = api.model('CollaboratorAdd', {
        'username': fields.String(required=True, description='Username of user to add as collaborator')
    })
    
    collaborator = api.model('Collaborator', {
        'public_id': fields.String(description='User public id'),
        'username': fields.String(description='Username'),
        'email': fields.String(description='Email')
    })
