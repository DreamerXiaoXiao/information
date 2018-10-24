"""新闻模块"""
from flask import Blueprint


news_blu = Blueprint('news', __name__, url_prefix='/news')


from . import views