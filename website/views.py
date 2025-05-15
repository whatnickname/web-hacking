from flask_login import login_required, current_user
from flask import Flask, render_template, request, redirect, url_for, Blueprint, send_file, current_app
from website import database, comments
import os
from . import db
from .models import Post
import sqlite3

views = Blueprint('views', __name__)

# 현재 파일 위치 기준 경로들
current_path = os.path.dirname(__file__)
comments_path = os.path.join(current_path, "comments.csv")

static_path = os.path.join(os.path.dirname(__file__), "..", "static")
static_path = os.path.abspath(static_path)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/main')
def main():
    return render_template("main.html", user=current_user)

@views.route('/upload')
def upload():
    return render_template("upload.html", user=current_user)

@views.route('/apply_photo')
def photo_apply():
    title = request.args.get("title")
    content = request.args.get("content")
    nickname = current_user.nickname
    new_post = Post(title=title, content=content, nickname=nickname)
    db.session.add(new_post)
    db.session.commit()
    #database.save(title, content, nickname)
    return render_template("apply_photo.html", user=current_user)

@views.route('/upload_done', methods=["POST"])
def upload_done():
    uploaded_file = request.files["file"]
    if uploaded_file.filename != '':
        os.makedirs(static_path, exist_ok=True)
        save_path = os.path.join(static_path, f"{database.now_index()}.jpeg")
        uploaded_file.save(save_path)
    return redirect(url_for("views.main"))


@views.route('/list')
def list():
    board_list = database.load_list()
    length = len(board_list)
    return render_template("list.html", board_list=board_list, length=length, user=current_user)

@views.route('/board_info', methods=['GET', 'POST'])
def board_info():
    filename = request.args.get("filename")

    # 1. 유효성 검사
    if not filename:
        return "파일명이 제공되지 않았습니다.", 400
    if not filename.endswith(".jpeg"):
        return "잘못된 파일 확장자입니다.", 400
    
    try:
        index = int(filename[:-5])  # "3.jpeg" → "3" → 3
    except ValueError:
        return "파일명에서 인덱스를 추출할 수 없습니다.", 400

    # 2. 게시글 로드
    post = database.load_board(index)
    if post is None:
        return "게시글을 찾을 수 없습니다.", 404

    title = post.title
    content = post.content
    writer = post.nickname

    # 3. 이미지 경로 확인
    photo = url_for('static', filename=filename)
    photo_path = os.path.join(static_path, filename)
    check = os.path.exists(photo_path)

    # 4. 댓글 처리
    if request.method == "POST":
        comment_text = request.form["content"]
        author = current_user.nickname
        comments.add_comment(index, author, comment_text)
        return redirect(url_for("views.board_info", filename=filename))

    comment_list = comments.load_comments(index)

    return render_template(
        "board_info.html",
        title=title,
        content=content,
        photo=photo,
        check=check,
        user=current_user,
        comments=comment_list,
        filename=filename,
        nickname=current_user.nickname,
        writer=writer,
        index=index
    )



@views.route('/edit', methods=['GET', 'POST'])
def edit_post():
    filename = request.args.get("filename")
    index = int(filename.replace(".jpeg", ""))  # "3.jpeg" → 3
    board_info = database.load_board(index)

    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        database.update_post(index, new_title, new_content)

        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename != '':
            os.makedirs(static_path, exist_ok=True)
            file_path = os.path.join(static_path, filename)
            uploaded_file.save(file_path)

        return redirect(url_for('views.board_info', filename=filename, index=index))

    # GET 요청일 때 이미지 존재 여부 확인
    photo_path = os.path.join(static_path, filename)
    check = os.path.exists(photo_path)

    return render_template('edit.html', post=board_info, filename=filename, user=current_user, check=check, index=index)

@views.route('/delete')
def delete_post():
    filename = request.args.get("filename")

    # 유효성 검사
    if not filename or not filename.endswith(".jpeg") or not filename[:-5].isdigit():
        return "유효하지 않은 파일명입니다.", 400

    index = int(filename.replace(".jpeg", ""))
    database.delete_post(index)

    # 이미지 파일도 함께 삭제 (선택 사항)
    image_path = os.path.join(static_path, filename)
    if os.path.exists(image_path):
        os.remove(image_path)

    return redirect(url_for('views.list'))


@views.route('/delete_image')
def delete_image():
    filename = request.args.get("filename")
    print(filename)
    if not filename or not filename.endswith(".jpeg"):
        return "유효하지 않은 파일명입니다.", 400

    index = int(filename.replace(".jpeg", ""))
    image_path = os.path.join(static_path, filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    return redirect(url_for('views.edit_post', filename=filename))


@views.route('/download')
def download_image():
    filename = request.args.get('filename')  # 파일명을 URL 파라미터로 받음
    file_path = os.path.join(static_path, filename)
    print(file_path)
    if os.path.exists(file_path):
        return send_file(file_path)
    return "파일을 찾을 수 없습니다.", 404

@views.route('/download_image')
def download_by_filename():
    filename = request.args.get('filename')  # 파일명을 URL 파라미터로 받음
    file_path = os.path.join(static_path, filename)
    return send_file(file_path, as_attachment=True)




@views.route('/search')
def search():
    query = request.args.get('q', '')
    result = []
    
    try:
        db_path = os.path.join(current_app.instance_path, 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ⚠️ SQL Injection 실습을 위한 취약한 쿼리
        sql = f"SELECT id, title, content, nickname FROM post WHERE title LIKE '%{query}%'"
        print(f"실행된 쿼리: {sql}")
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        # 튜플을 Post 모양으로 흉내 내기
        result = [{'id': r[0], 'title': r[1], 'content': r[2], 'nickname': r[3]} for r in rows]

    except Exception as e:
        result = []
        print(f"검색 오류: {e}")

    return render_template(
        "search_results.html",
        query=query,
        board_list=result,
        length=len(result),
        user=current_user
    )




