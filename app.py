from website import create_app
from flask import Flask, render_template, request, redirect, url_for
from website import database  #경로 수정
from website import db, create_app

app = create_app()

if __name__ == '__main__':
    app.run()