from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.tag import Tag
from app.models.note import Note
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

# Create namespace
api = Namespace('tags', description='Tag operations')

# DTO Models
tag_dto = api.model('Tag', {
    'id': fields.Integer(readonly=True, description='Tag ID'),
    'name': fields.String(required=True, description='Tag name'),
    'note_count': fields.Integer(readonly=True, description='Number of notes with this tag'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

tag_input_dto = api.model('TagInput', {
    'name': fields.String(required=True, description='Tag name', min_length=1, max_length=50)
})

# Routes
@api.route('/')
class TagList(Resource):
    @api.doc('list_tags', description='Get all tags')
    @api.marshal_list_with(tag_dto)
    def get(self):
        """List all tags"""
        tags = Tag.query.all()
        return [{
            'id': tag.id,
            'name': tag.name,
            'note_count': len(tag.notes),
            'created_at': tag.created_at
        } for tag in tags]
    
    @api.doc('create_tag', description='Create a new tag')
    @api.expect(tag_input_dto)
    @api.marshal_with(tag_dto, code=201)
    @jwt_required()
    def post(self):
        """Create a new tag"""
        data = request.get_json()
        tag_name = data.get('name', '').strip().lower()
        
        if not tag_name:
            api.abort(400, 'Tag name is required')
        
        # Check if tag already exists
        existing_tag = Tag.query.filter_by(name=tag_name).first()
        if existing_tag:
            return {
                'id': existing_tag.id,
                'name': existing_tag.name,
                'note_count': len(existing_tag.notes),
                'created_at': existing_tag.created_at
            }, 200
        
        # Create new tag
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit()
        
        logger.info(f"Tag created: {tag.name}")
        
        return {
            'id': tag.id,
            'name': tag.name,
            'note_count': 0,
            'created_at': tag.created_at
        }, 201


@api.route('/<int:tag_id>')
@api.param('tag_id', 'Tag identifier')
@api.response(404, 'Tag not found')
class TagResource(Resource):
    @api.doc('get_tag', description='Get a tag by ID')
    @api.marshal_with(tag_dto)
    def get(self, tag_id):
        """Get a specific tag"""
        tag = Tag.query.get_or_404(tag_id)
        return {
            'id': tag.id,
            'name': tag.name,
            'note_count': len(tag.notes),
            'created_at': tag.created_at
        }
    
    @api.doc('delete_tag', description='Delete a tag')
    @api.response(204, 'Tag deleted')
    @jwt_required()
    def delete(self, tag_id):
        """Delete a tag"""
        tag = Tag.query.get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()
        
        logger.info(f"Tag deleted: {tag.name}")
        
        return '', 204


@api.route('/<int:tag_id>/notes')
@api.param('tag_id', 'Tag identifier')
@api.response(404, 'Tag not found')
class TagNotes(Resource):
    @api.doc('get_tag_notes', description='Get all notes with this tag')
    def get(self, tag_id):
        """Get all notes with a specific tag"""
        tag = Tag.query.get_or_404(tag_id)
        
        # Get current user if authenticated
        try:
            current_user_id = get_jwt_identity()
        except:
            current_user_id = None
        
        # Filter notes based on visibility
        notes = []
        for note in tag.notes:
            # Show public notes or notes owned by current user
            if note.is_public or (current_user_id and note.owner_id == current_user_id):
                notes.append({
                    'public_id': note.public_id,
                    'title': note.title,
                    'description': note.description,
                    'is_public': note.is_public,
                    'view_count': note.view_count,
                    'created_at': note.created_at.isoformat(),
                    'owner': {
                        'public_id': note.owner.public_id,
                        'username': note.owner.username
                    }
                })
        
        return {
            'tag': {
                'id': tag.id,
                'name': tag.name
            },
            'notes': notes,
            'total': len(notes)
        }


@api.route('/popular')
class PopularTags(Resource):
    @api.doc('get_popular_tags', description='Get most popular tags')
    @api.param('limit', 'Number of tags to return', type='integer', default=10)
    def get(self):
        """Get most popular tags by note count"""
        limit = request.args.get('limit', 10, type=int)
        
        tags = Tag.query.all()
        tags_with_counts = [{
            'id': tag.id,
            'name': tag.name,
            'note_count': len(tag.notes),
            'created_at': tag.created_at
        } for tag in tags]
        
        # Sort by note count
        tags_with_counts.sort(key=lambda x: x['note_count'], reverse=True)
        
        return tags_with_counts[:limit]
