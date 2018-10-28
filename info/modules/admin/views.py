from . import admin_blu
from flask import render_template, request, g, current_app, session, redirect, url_for

from info.models import User
from info.utils.common import user_login_data


@admin_blu.route('/index')
@user_login_data
def admin_index():
    user = g.user
    return render_template('admin/index.html', data={'user': user.to_dict()})


@admin_blu.route('/login', methods=["POST", "GET"])
def admin_login():
    """管理员登录"""
    if request.method == "GET":
        # 如果管理员已经登录,那么不需要登录,直接跳转到后台主页
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))

        return render_template('admin/login.html')

    # 获取参数
    username = request.form.get('username')
    password = request.form.get('password')

    # 校验参数
    if not all([username, password]):
        return render_template('admin/login.html', errormsg="参数错误")

    # 查询用户
    try:
        user = User.query.filter(User.is_admin == True, User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errormsg="查询错误")
    if not user:
        return render_template('admin/login.html', errormsg="用户不存在")

    if not user.check_password(password):
        return render_template('admin/login.html', errormsg="密码错误")

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    session['is_admin'] = user.is_admin

    return redirect(url_for('admin.admin_index'))
