from ..extensions import db
from datetime import datetime

class Tag(db.Model):
    __tablename__ = 'tag'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to notes through association table
    notes = db.relationship('Note', secondary='note_tags', back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'
