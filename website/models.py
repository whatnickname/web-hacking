from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id=db.Column(db.String(150), primary_key=True)
    data=db.Column(db.String(10000))
    data=db.Column(db.DateTime(timezone=True), default=func.now())
    user_id=db.Column(db.String(150), db.ForeignKey('user.id'))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    image = db.Column(db.LargeBinary)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    post = db.relationship('Post', backref=db.backref('comments', cascade='all, delete-orphan', lazy=True))

class User(db.Model, UserMixin):
    id=db.Column(db.String(150), primary_key=True)
    email=db.Column(db.String(150), unique=True)
    nickname=db.Column(db.String(150), unique=True)
    password=db.Column(db.String(150))
    notes=db.relationship("Note")
    