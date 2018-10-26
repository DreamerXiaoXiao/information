from flask import render_template, g, request, redirect, jsonify

from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import profile_blu


@profile_blu.route('pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    user = g.user
    if not user:
        return redirect('/')
    if request.method == "GET":
        return render_template('news/user_pic_info.html')


@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    """
    用户基本信息显示/修改
    # 1.如果用户不存在,重定向到主页
    # 2.获取参数
    # 3.校验参数
    # 4.更新用户信息
    :return:
    """
    # 1.如果用户不存在, 重定向到主页
    user = g.user
    if not user:
        return redirect('/')
    # 不同的请求方式，做不同的事情
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user": user.to_dict() if user else None})

    # 2.获取参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')

    # 3.校验参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 4.更新用户信息
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    return jsonify(errno=RET.OK, errmsg='OK')


@profile_blu.route('/user_info')
@user_login_data
def user_info():
    # 如果用户不存在,直接重定向主页
    user = g.user
    if not user:
        return redirect('/')
    return render_template('news/user.html', data={'user': user})

