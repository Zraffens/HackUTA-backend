from app.extensions import db

class NoteReaction(db.Model):
    __tablename__ = 'notereaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    reaction_type = db.Column(db.String(50), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'note_id', 'reaction_type', name='_user_note_reaction_uc'),)
