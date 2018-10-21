from flask import render_template, current_app, session, jsonify

from info.models import User
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/')
def index():
    """
    主页面判断用户是否登录
    1.获取session信息
    2.查询用户信息
    3.校验用户信息
    4.渲染模板
    :return:
    """
    # 1.获取session信息
    user_id = session.get('user_id')

    # 2.查询用户信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 3.把用户信息转换为字典返回
    data = {
        'user': user.to_dict() if user else None
    }

    # 4.渲染模板
    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    """返回页面图标"""
    return current_app.send_static_file('news/favicon.ico')
