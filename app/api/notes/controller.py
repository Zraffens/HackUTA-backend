from flask import request
from flask_restx import Resource, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from .dto import NoteDto
from ...models.note import Note
from ...models.user import User
from ...services.file_service import save_file
from ... import db

api = NoteDto.api
_note_display = NoteDto.note_display
_note_create = NoteDto.note_create

@api.route('')
class NoteList(Resource):
    @api.marshal_list_with(_note_display)
    def get(self):
        """List all public notes"""
        return Note.query.filter_by(is_public=True).all()

    @jwt_required()
    @api.expect(_note_create, validate=True)
    def post(self):
        """Create a new note"""
        args = _note_create.parse_args()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()

        file = args['file']
        file_path = save_file(file)
        if not file_path:
            return {'message': 'File type not allowed or file save failed'}, 400

        new_note = Note(
            title=args['title'],
            description=args['description'],
            is_public=args['is_public'],
            owner_id=user.id,
            file_path=file_path
        )
        db.session.add(new_note)
        db.session.commit()
        
        return marshal(new_note, _note_display), 201

@api.route('/<public_id>')
@api.param('public_id', 'The note identifier')
class NoteDetail(Resource):
    @api.marshal_with(_note_display)
    def get(self, public_id):
        """Fetch a given note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        if not note.is_public:
            # This would require auth and checking if user is owner or collaborator
            # For now, just return 403 if private
            return {'message': 'Access forbidden'}, 403
        return note

    @jwt_required()
    def put(self, public_id):
        """Update a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()

        if note.owner_id != user.id:
            return {'message': 'You are not the owner of this note'}, 403

        data = request.get_json()
        note.title = data.get('title', note.title)
        note.description = data.get('description', note.description)
        note.is_public = data.get('is_public', note.is_public)
        db.session.commit()
        return marshal(note, _note_display)

    @jwt_required()
    def delete(self, public_id):
        """Delete a note"""
        note = Note.query.filter_by(public_id=public_id).first_or_404()
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()

        if note.owner_id != user.id:
            return {'message': 'You are not the owner of this note'}, 403
        
        # Optional: delete file from filesystem
        # import os
        # if os.path.exists(note.file_path):
        #     os.remove(note.file_path)

        db.session.delete(note)
        db.session.commit()
        return '', 204
