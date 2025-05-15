
import sqlite3
import os
from flask import current_app

def load_comments(post_id):
    try:
        db_path = os.path.join(current_app.instance_path, 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = f"SELECT author, content, created_at FROM comment WHERE post_id = {post_id} ORDER BY created_at ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        # 리스트로 반환
        return [{'author': r[0], 'content': r[1], 'created_at': r[2]} for r in rows]

    except Exception as e:
        print(f"댓글 불러오기 오류: {e}")
        return []


def add_comment(post_id, author, content):
    try:
        db_path = os.path.join(current_app.instance_path, 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = f"INSERT INTO comment (post_id, author, content) VALUES (?, ?, ?)"
        cursor.execute(query, (post_id, author, content))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"댓글 추가 오류: {e}")
