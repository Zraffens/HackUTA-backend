from app.extensions import db
import uuid
from datetime import datetime
from .associations import note_collaborators, note_courses

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', backref='note', lazy=True, cascade="all, delete-orphan")
    reactions = db.relationship('NoteReaction', backref='note', lazy=True, cascade="all, delete-orphan")
    
    collaborators = db.relationship('User', secondary=note_collaborators, lazy='subquery',
                                    backref=db.backref('collaborating_notes', lazy=True))
    courses = db.relationship('Course', secondary=note_courses, lazy='subquery',
                              backref=db.backref('notes', lazy=True))
