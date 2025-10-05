from app.extensions import db
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .associations import followers, user_bookmarks

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_bio = db.Column(db.Text, nullable=True)

    notes = db.relationship('Note', backref='owner', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    
    following = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    bookmarked_notes = db.relationship(
        'Note', secondary=user_bookmarks,
        backref=db.backref('bookmarked_by', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
