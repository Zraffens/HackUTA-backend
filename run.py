import os
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'dev')

from app.models.user import User
from app.models.course import Course
from app.models.note import Note
from app.models.comment import Comment
from app.models.reaction import NoteReaction
from app.models.blocklist import BlocklistedToken

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Course=Course, Note=Note,
                Comment=Comment, NoteReaction=NoteReaction,
                BlocklistedToken=BlocklistedToken)


if __name__ == "__main__":
    app.run()
