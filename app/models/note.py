from app.extensions import db
import uuid
from datetime import datetime
from .associations import note_collaborators, note_courses, note_tags, user_bookmarks
import os

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)  # Original handwritten note (PDF/image)
    markdown_path = db.Column(db.String(255), nullable=True)  # Converted markdown file
    ocr_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    is_public = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)  # Track views
    download_count = db.Column(db.Integer, default=0)  # Track downloads
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', backref='note', lazy=True, cascade="all, delete-orphan")
    reactions = db.relationship('NoteReaction', backref='note', lazy=True, cascade="all, delete-orphan")
    
    collaborators = db.relationship('User', secondary=note_collaborators, lazy='subquery',
                                    backref=db.backref('collaborating_notes', lazy=True))
    courses = db.relationship('Course', secondary=note_courses, lazy='subquery',
                              backref=db.backref('notes', lazy=True))
    tags = db.relationship('Tag', secondary=note_tags, lazy='subquery',
                           back_populates='notes')
    bookmarked_by = db.relationship('User', secondary=user_bookmarks, lazy='subquery',
                                    backref=db.backref('bookmarked_notes', lazy=True))

    @property
    def has_markdown(self):
        """Check if note has markdown content available"""
        return (self.ocr_status == 'completed' and 
                self.markdown_path and 
                os.path.exists(self.markdown_path))
    
    @property
    def markdown_url(self):
        """Get the API endpoint URL for fetching markdown content"""
        return f"/api/notes/{self.public_id}/markdown"
