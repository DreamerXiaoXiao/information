"""后台管理模块"""
from flask import Blueprint, session, request, redirect, url_for

admin_blu = Blueprint('admin', __name__, url_prefix='/admin')

from . import views


@admin_blu.before_request
def before_request():
    """在管理员页面,每次访问之间判断是否是管理员"""
    is_admin = session.get('is_admin')
    if not is_admin and not request.url.endswith('/admin/login'):
        # 返回主页
        return redirect(url_for('index.index'))
