from flask_login import login_required, current_user
from flask import Flask, render_template, request, redirect, url_for, Blueprint
from website import database
import os
from website import comments

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
    database.save(title, content, nickname)
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

@views.route('/board_info/<int:index>/', methods=['GET', 'POST'])
def board_info(index):
    board_info = database.load_board(index)
    title = board_info["title"]
    content = board_info["content"]
    writer = board_info["nickname"]

    # 이미지 경로 생성
    filename = f"{index}.jpeg"
    photo = url_for('static', filename=filename)
    photo_path = os.path.join(static_path, filename)
    check = os.path.exists(photo_path)

    if request.method == "POST":
        content = request.form["content"]
        author = current_user.nickname
        comments.add_comment(index, author, content)
        return redirect(url_for("views.board_info", index=index))

    comment_list = comments.load_comments(index)
    nickname = current_user.nickname

    return render_template(
        "board_info.html",
        title=title,
        content=content,
        photo=photo,
        check=check,
        user=current_user,
        comments=comment_list,
        index=index,
        nickname=nickname,
        writer=writer

    )

@views.route('/edit/<int:index>/', methods=['GET', 'POST'])
def edit_post(index):
    board_info = database.load_board(index)
    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        database.update_post(index, new_title, new_content)

        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename != '':
            os.makedirs(static_path, exist_ok=True)
            file_path = os.path.join(static_path, f"{index}.jpeg")
            uploaded_file.save(file_path)

        return redirect(url_for('views.board_info', index=index))

    filename = f"{index}.jpeg"
    photo_path = os.path.join(static_path, filename)
    check = os.path.exists(photo_path)

    return render_template('edit.html', post=board_info, index=index, user=current_user, check=check)

@views.route('/delete/<int:index>')
def delete_post(index):
    database.delete_post(index)
    return redirect(url_for('views.list'))

@views.route('/delete_image/<int:index>')
def delete_image(index):
    filename = f"{index}.jpeg"
    image_path = os.path.join(static_path, filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    return redirect(url_for('views.edit_post', index=index))
