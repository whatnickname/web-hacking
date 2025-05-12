# 필요한 모듈 임포트
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app # current_app 임포트 확인
# .models에서 User 모델 임포트 (SQLAlchemy 사용 부분 및 User 객체 사용 위함)
from .models import User
#from . import db # 회원가입 처리에서 SQLAlchemy 객체 사용 안 함 (Raw SQL 사용)

from werkzeug.security import generate_password_hash, check_password_hash
from  flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import os # os 모듈 임포트 확인
import openpyxl # 쿼리 저장 시 필요
import sqlite3 # SQLite 직접 연결을 위해 추가

# DB_NAME 변수를 auth.py 파일 내에서 다시 정의하여 NameError 해결
# __init__.py에서도 정의되어 있지만, 각 모듈에서 필요시 정의하거나 임포트하는 것이 일반적입니다.
DB_NAME = 'database.db'

# Blueprint 객체 생성
auth = Blueprint('auth', __name__)

# --- 로그인 라우트 ---
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')  # 입력된 사용자 ID
        password = request.form.get('password')  # 입력된 비밀번호

        # SQLAlchemy ORM을 사용하여 ID로 사용자 조회
        user = User.query.get(user_id)

        if user:  # 사용자가 존재하는 경우
            # 저장된 해시된 비밀번호와 입력된 비밀번호 비교
            if check_password_hash(user.password, password):
                flash('로그인 성공!', category='success')
                # Flask-Login의 login_user 함수로 사용자 로그인 세션 설정
                login_user(user, remember=True)  # 'remember=True'는 로그인 상태 유지를 위한 옵션
                # 로그인 성공 후 홈 페이지로 리다이렉트
                return redirect(url_for('views.home'))
            else:
                # 비밀번호 불일치 시 오류 메시지 플래시
                flash('비밀번호를 다시 시도해 주세요.', category='error')
        else:
            # 사용자 ID가 존재하지 않는 경우 오류 메시지 플래시
            flash('존재하지 않는 ID입니다.', category='error')

    # GET 요청이거나 POST 처리 중 오류로 리다이렉트되지 않은 경우, 로그인 페이지 템플릿 렌더링
    return render_template("login.html", user=current_user)


# --- 로그아웃 라우트 ---
@auth.route('/logout')
@login_required # 로그인된 사용자만 접근 가능
def logout():
    # Flask-Login의 logout_user 함수로 사용자 세션 해제
    logout_user()
    # 로그아웃 후 로그인 페이지로 리다이렉트
    return redirect(url_for('auth.login'))


# --- 쿼리 저장 라우트 (추가 기능) ---
@auth.route('/query', methods=['GET', 'POST'])
@login_required # 로그인된 사용자만 접근 가능
def query_door():
    if request.method == 'POST':
        query = request.form.get('query') # 사용자로부터 입력받은 쿼리
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 현재 로그인된 사용자의 닉네임을 사용 (Flask-Login 제공 current_user 객체 활용)
        username = current_user.nickname if current_user.is_authenticated else 'Anonymous' # is_authenticated 속성 확인

        # 텍스트 파일에 저장하기
        # 'a' 모드(append)로 열어 기존 내용에 추가합니다. 파일이 없으면 생성됩니다.
        # 파일 경로는 현재 작업 디렉토리를 기준으로 합니다.
        try:
            with open('queries.txt', 'a', encoding='utf-8') as f:
                f.write(f'{timestamp} - {username}: {query}\n')
        except Exception as e:
            print(f"Error writing to queries.txt: {e}") # 오류 발생시 터미널 출력

        # 엑셀 파일에 저장하기 (openpyxl 라이브러리 사용)
        excel_file = 'queries.xlsx'
        try:
            # 파일이 없으면 헤더와 함께 새로 생성합니다.
            if not os.path.exists(excel_file):
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = 'Queries' # 시트 이름 설정
                sheet.append(['Timestamp', 'Username', 'Query']) # 헤더 행 추가
                workbook.save(excel_file) # 파일 저장

            # 기존 파일에 데이터를 추가합니다.
            workbook = openpyxl.load_workbook(excel_file) # 기존 파일 로드
            sheet = workbook.active # 활성 시트 선택
            sheet.append([timestamp, username, query]) # 새 데이터 행 추가
            workbook.save(excel_file) # 변경사항 저장

            flash('Query successfully saved!', category='success') # 성공 메시지 플래시

        except Exception as e:
            # 엑셀 파일 작업 중 오류 발생 시 메시지 플래시 및 터미널 출력
            flash(f'Error saving query to Excel: {e}', category='error')
            print(f"Error saving query to Excel: {e}")

        # 쿼리 저장 처리 후 홈 페이지로 리다이렉트합니다.
        return redirect(url_for('views.home'))

    # GET 요청 시 query.html 템플릿을 렌더링합니다.
    return render_template('query.html', user=current_user)


# --- 회원가입 라우트 ---
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # POST 요청이 들어온 경우 (폼 제출)
    if request.method == 'POST':
        # 폼 데이터 가져오기
        email = request.form.get('email')
        password = request.form.get('password')
        passwordCon = request.form.get('passwordCon') # 비밀번호 확인 필드
        user_id_str = request.form.get('user_id')  # 사용자 ID (HTML 폼에서 문자열로 받음)
        nickname = request.form.get('nickname')

        # 입력값 기본 유효성 검사 (필수 필드 누락 체크)
        if not all([email, password, passwordCon, user_id_str, nickname]):
            flash('모든 필드를 입력해 주세요.', category='error')
            return redirect(url_for('auth.signup')) # 오류 시 회원가입 페이지로 리다이렉트
        
        user_id = user_id_str.strip()


        # 추가적인 유효성 검사 (길이, 비밀번호 일치 등)
        if len(email) < 10:
            flash('올바른 이메일 주소를 입력해 주세요.', category='error')
            return redirect(url_for('auth.signup'))
        elif password != passwordCon:
            flash('비밀번호가 일치하지 않습니다.', category='error')
            return redirect(url_for('auth.signup'))
        elif len(password) < 4: # 메시지와 검사 기준 일치 (최소 4자)
            flash('비밀번호는 최소 4자 이상이어야 합니다.', category='error')
            return redirect(url_for('auth.signup'))
        elif len(user_id) < 2: # ID가 2 이상의 숫자여야 함
             flash('ID는 2 이상의 숫자여야 합니다.', category='error')
             return redirect(url_for('auth.signup'))
        elif len(nickname) < 2:
            flash('닉네임은 최소 2자 이상이어야 합니다.', category='error')
            return redirect(url_for('auth.signup'))


        # --- SQLite 데이터베이스 연결 및 Raw SQL 작업 시작 ---
        # Flask 애플리케이션의 instance_path를 기준으로 데이터베이스 파일의 절대 경로를 구성합니다.
        # __init__.py와 동일한 경로를 사용하여 SQLAlchemy와 sqlite3가 같은 파일을 바라보게 합니다.
        # 이 시점에서는 요청 컨텍스트 내이므로 current_app 객체 사용 가능합니다.
        db_path_absolute = os.path.join(current_app.instance_path, DB_NAME)

        # 디버깅을 위해 실제 연결 시도하는 경로를 터미널에 출력합니다.
        # print(f"App Root Path: {current_app.root_path}") # 필요시 루트 경로 디버깅
        print(f"Attempting to connect to database at absolute path from auth.py: {db_path_absolute}")


        conn = None # 데이터베이스 연결 객체 초기화
        cursor = None # 커서 객체 초기화
        try:
            # SQLite 데이터베이스 연결 시도
            # 파일이 없으면 sqlite3.connect()가 자동으로 파일을 생성합니다.
            # 하지만 __init__.py에서 SQLAlchemy의 create_all()로 테이블 구조까지 만들어주는 것이 일반적입니다.
            conn = sqlite3.connect(db_path_absolute) # 절대 경로 사용
            cursor = conn.cursor() # 커서 객체 생성 (SQL 쿼리 실행에 사용)

            # --- 사용자 ID 중복 확인 (Raw SQL) ---
            # **경고: 사용자 입력(user_id)을 직접 쿼리 문자열에 삽입하는 것은 SQL Injection 위험이 매우 높습니다.**
            # **이 방식은 요청하신 대로 구현한 예시이며, 실제 운영 환경에서는 절대 사용하면 안 됩니다.**
            # 안전한 방식은 매개변수화된 쿼리(Parameterized Query)를 사용하는 것입니다.
            # 예: cursor.execute("SELECT id FROM user WHERE id = ?", (user_id,))
            cursor.execute(f"SELECT id FROM user WHERE id = '{user_id}'") # SQL Injection 위험 지점
            existing_user_id = cursor.fetchone() # 결과 한 행 가져오기

            if existing_user_id:
                 flash('이미 존재하는 ID입니다.', category='error')
                 return redirect(url_for('auth.signup')) # 오류 시 회원가입 페이지로 리다이렉트

            # --- 이메일 중복 확인 (Raw SQL) ---
            # **경고: 사용자 입력(email)을 직접 쿼리 문자열에 삽입하는 것은 SQL Injection 위험이 매우 높습니다.**
            cursor.execute(f"SELECT email FROM user WHERE email = '{email}'") # SQL Injection 위험 지점
            existing_user_email = cursor.fetchone()

            if existing_user_email:
                 flash('이미 존재하는 이메일 주소입니다.', category='error')
                 return redirect(url_for('auth.signup'))

             # --- 닉네임 중복 확인 (Raw SQL) ---
             # **경고: 사용자 입력(nickname)을 직접 쿼리 문자열에 삽입하는 것은 SQL Injection 위험이 매우 높습니다.**
            cursor.execute(f"SELECT nickname FROM user WHERE nickname = '{nickname}'") # SQL Injection 위험 지점
            existing_user_nickname = cursor.fetchone()

            if existing_user_nickname:
                flash('이미 존재하는 닉네임입니다.', category='error')
                return redirect(url_for('auth.signup'))
            
            # 비밀번호 해시화
            # Werkzeug 최신 버전에서 권장하는 'scrypt' 방식을 사용합니다.
            hashed_password = generate_password_hash(password, method='scrypt')


            # --- 사용자 정보 삽입 (Raw SQL) ---
            # **경고: 사용자 입력(email, nickname, hashed_password)을 직접 쿼리 문자열에 삽입하는 것은 SQL Injection 위험이 매우 높습니다.**
            # SQLite에서 문자열은 작은따옴표로 감싸야 합니다.
            insert_query = f"INSERT INTO user (id, email, nickname, password) VALUES ('{user_id}', '{email}', '{nickname}', '{hashed_password}')" # SQL Injection 위험 지점

            # 삽입 쿼리 실행
            cursor.execute(insert_query)
            # 변경사항 데이터베이스에 반영 (매우 중요!)
            conn.commit()

            # --- 삽입된 사용자를 다시 조회하여 Flask-Login에 전달 ---
            # Flask-Login의 login_user 함수는 UserMixin을 상속받은 객체를 기대합니다.
            # Raw SQL로 삽입한 후, 해당 사용자를 SQLAlchemy ORM으로 다시 조회하는 것이 가장 안전하고 편리합니다.
            # .models에서 User 클래스를 임포트했는지 확인하세요.
            from .models import User # models.py에서 User 클래스 임포트 (혹시 상단 임포트 누락 시)

            # 사용자 조회를 위해 SQLAlchemy ORM 사용 (권장 방식)
            new_user = User.query.get(user_id)

            if new_user:
                # 조회된 User 객체로 Flask-Login 로그인 처리
                login_user(new_user, remember=True)
                flash('회원가입 성공!', category='success')
                # 회원가입 및 로그인 성공 후 홈 페이지로 리다이렉트
                return redirect(url_for('views.home'))
            else:
                # 회원가입(Raw SQL)은 성공했지만, ORM 조회에 실패한 경우
                # 이런 경우는 드물지만, 오류 처리를 위해 추가
                flash('회원가입은 성공했지만 로그인 정보를 불러오는데 오류가 발생했습니다. 다시 로그인해 주세요.', category='warning')
                # 로그인 페이지로 리다이렉트하여 수동 로그인 유도
                return redirect(url_for('auth.login'))


        # --- 예외 처리 블록 ---
        # SQLite 데이터베이스 관련 오류 발생 시 처리
        except sqlite3.Error as e:
            # 데이터베이스 오류 발생 시 메시지를 더 상세하게 사용자에게 플래시
            flash(f'데이터베이스 오류가 발생했습니다: {e}', category='error')
            # 디버깅을 위해 터미널에도 오류 내용을 출력
            print(f"SQLite Error during signup: {e}")
            if conn:
                # 오류 발생 시 커밋되지 않은 변경사항 롤백 (데이터 일관성 유지)
                conn.rollback()

        # 기타 예상치 못한 오류 발생 시 처리
        except Exception as e:
            # 예상치 못한 오류 발생 시 메시지를 사용자에게 플래시
            flash(f'예상치 못한 오류가 발생했습니다: {e}', category='error')
            # 디버깅을 위해 터미널에도 오류 내용을 출력
            print(f"Unexpected Error during signup: {e}")

        # --- finally 블록 ---
        # try 또는 except 블록 실행 후 항상 실행되는 부분 (자원 해제)
        finally:
            # 커서 객체가 생성되었다면 닫습니다.
            if cursor:
                cursor.close()
            # 데이터베이스 연결 객체가 생성되었다면 닫습니다.
            if conn:
                conn.close()

    # GET 요청이거나 POST 처리 중 오류로 인해 리다이렉트되지 않은 경우
    # (예: 유효성 검사 실패, DB 오류 발생 후 except 블록에서 리다이렉트 안 한 경우 등)
    # 회원가입 페이지 템플릿을 다시 렌더링하여 폼과 플래시 메시지를 보여줍니다.
    return render_template("signup.html", user=current_user)

