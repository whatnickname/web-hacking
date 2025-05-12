from .models import Post
from . import db
import os

current_path = os.path.dirname(__file__)
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
static_path = os.path.abspath(static_path)

def save(title, content, nickname):
    new_post = Post(title=title, content=content, nickname=nickname)
    db.session.add(new_post)
    db.session.commit()

def load_list():
    return Post.query.order_by(Post.id.desc()).all()

def now_index():
    last_post = Post.query.order_by(Post.id.desc()).first()
    return last_post.id if last_post else 0

def load_board(idx):
    return Post.query.get(idx)

def update_post(index, new_title, new_content):
    post = Post.query.get(index)
    if post:
        post.title = new_title
        post.content = new_content
        db.session.commit()

def delete_post(index):
    post = Post.query.get(index)
    if post:
        db.session.delete(post)
        db.session.commit()

    filename = f"{index}.jpeg"
    image_path = os.path.join(static_path, filename)
    if os.path.exists(image_path):
        os.remove(image_path)
