from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from  flask_login import login_user, login_required, logout_user, current_user

auth= Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')  # 입력된 사용자 ID
        password = request.form.get('password')  # 입력된 비밀번호

        user = User.query.get(user_id)  # ID로 사용자 조회

        if user:  # 사용자가 존재하는 경우
            if check_password_hash(user.password, password):  # 비밀번호 확인
                flash('로그인 성공!', category='success')
                login_user(user, remember=True)  # 사용자 로그인
                return redirect(url_for('views.home'))  # 홈으로 리다이렉트
            else:
                flash('비밀번호를 다시 시도해 주세요.', category='error')
        else:
            flash('존재하지 않는 ID입니다.', category='error')

    return render_template("login.html", user=current_user)  # 로그인 페이지 재렌더링


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        passwordCon = request.form.get('passwordCon')
        user_id = request.form.get('user_id')  # HTML에서 받은 user_id
        nickname = request.form.get('nickname')

        if email is None or password is None or passwordCon is None or user_id is None or nickname is None:
            flash('모든 필드를 입력해 주세요.', category='error')
            return redirect(url_for('auth.signup'))

        # try:
        #     user_id = int(user_id)  # 문자열을 정수로 변환
        # except ValueError:
        #     flash('ID는 숫자여야 합니다.', category='error')
        #     return redirect(url_for('auth.signup'))

        user = User.query.filter_by(id=user_id).first()  # user_id 대신 id로 수정
        if user:
            flash('ID already exists', category='error')
        elif len(email) < 10:
            flash('Enter the correct email', category='error')
        elif password != passwordCon:
            flash('Passwords don\'t match', category='error')
        elif len(password) < 4:
            flash('Password must be at least 7 characters', category='error')
        elif len(user_id) < 2:
            flash('ID must be at least 2 characters', category='error')
        elif len(nickname) < 2:
            flash('Nickname must be at least 2 characters', category='error')
        else:
            new_user = User(nickname=nickname, email=email, id=user_id, password=generate_password_hash(password, method='pbkdf2:sha256'))  # user_id를 id로 수정
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)
