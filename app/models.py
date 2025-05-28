from datetime import datetime

from app.extensions import db
from app.utils import generate_uuid_32

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(
        db.String(32),
        primary_key=True,
        default=generate_uuid_32,
    )
    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
    )
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
    )
    password = db.Column(
        db.String(255),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
    )


    def __repr__(self):
        return f"<User id={self.id} username={self.username} email={self.email}>"
