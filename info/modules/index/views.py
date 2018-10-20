from flask import render_template, current_app

from . import index_blu


@index_blu.route('/')
def index():
    """返回主页页面"""
    return render_template('news/index.html')


@index_blu.route('/favicon.ico')
def favicon():
    """返回页面图标"""
    return current_app.send_static_file('news/favicon.ico')