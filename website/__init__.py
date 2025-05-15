from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
import psycopg2

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    # static 디렉토리 경로 수동 설정 (프로젝트 루트 기준의 static 폴더)
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    # static_folder 명시적으로 지정
    app = Flask(__name__, static_folder=static_dir)
    
    app.config['SECRET_KEY'] = 'qwrtqet qwr'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sounds_5iho_user:Q74BalcS5PpgEHbSecrDiucqbtyn9TqL@dpg-d0fg21a4d50c73erp500-a.virginia-postgres.render.com/sounds_5iho'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    #create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)  # id를 int로 변환

    return app


def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            db.create_all()
            print('✅ create database')


