from app.extensions import db
from datetime import datetime
from .associations import course_users

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

    users = db.relationship('User', secondary=course_users, lazy='subquery',
                            backref=db.backref('courses', lazy=True))
