"""自定义公共的工具类"""
import functools

from flask import session, current_app, g, jsonify

from info import constants
from info.models import User, News
from info.utils.response_code import RET

"""过滤器器工具类"""


def do_index_class(index):
    """主页排行过滤器"""
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


def do_index_active(index):
    """新闻分类工具过滤器"""
    if index == 1:
        return 'active'
    else:
        return ''


"""装饰器"""


def user_login_data(f):
    """校验用户登录"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 1.获取session信息
        user_id = session.get('user_id')

        # 2.查询用户信息
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args, **kwargs)
    return wrapper


def news_order_data(f):
    """新闻排行"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 查询新闻数据
        news_list = []
        try:
            news_list = News.query.filter(News.status == 0).order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
        except Exception as e:
            current_app.logger.error(e)

        news_dict_li = []
        for news in news_list:
            news_dict_li.append(news.to_basic_dict())
        g.news_dict_li = news_dict_li
        return f(*args, **kwargs)
    return wrapper
