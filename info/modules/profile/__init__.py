"""用户信息管理模块"""
from flask import Blueprint

profile_blu = Blueprint('profile', __name__, url_prefix='/user')


from . import views