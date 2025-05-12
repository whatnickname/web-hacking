
from . import db
from .models import Comment

def load_comments(post_id):
    return Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()

def add_comment(post_id, author, content):
    comment = Comment(post_id=post_id, author=author, content=content)
    db.session.add(comment)
    db.session.commit()
