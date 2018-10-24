from flask import render_template, session, current_app, jsonify

from info import constants
from info.models import User, News
from info.utils.response_code import RET
from . import news_blu


@news_blu.route('/news_detail/<int:news_id>')
def news_detail(news_id):
    """
    新闻详情页
    :param news_id:
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

    # 3.查询新闻数据
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻查询错误')

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 5.把以上数据封装为为字典返回
    data = {
        'user': user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
    }

    # 6.渲染模板
    return render_template('news/detail.html', data=data)


