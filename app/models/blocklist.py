from app.extensions import db

class BlocklistedToken(db.Model):
    __tablename__ = 'blocklistedtoken'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
