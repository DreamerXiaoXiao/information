from flask import render_template, current_app, session, jsonify, request, g
from sqlalchemy import and_

from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data, news_order_data
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/news_list')
def news_list():
    """
    新闻查询
    1.获取参数
    2.校验参数
    3.查询新闻
    4.返回响应
    :param news_id:
    :return:
    """

    # 1.获取参数
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')

    # 2.检验参数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 3.查询新闻
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻查询错误')
    news_list_model = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    # 4.遍历数据
    news_dict_li = []
    for news in news_list_model:
        news_dict_li.append(news.to_basic_dict())

    # 6.将数据保存到data中
    data = {
        'news_dict_li': news_dict_li,
        'total_page': total_page,
        'current_page': current_page
    }
    return jsonify(errno=RET.OK, errmsg='查询成功', data=data)


@index_blu.route('/')
@user_login_data
@news_order_data
def index():
    """
    主页面判断用户是否登录
    1.获取session信息
    2.查询用户信息
    3.校验用户信息
    4.渲染模板
    :return:
    """
    # 1.查询用户信息
    user = g.user

    # 2.查询新闻数据
    news_dict_li = g.news_dict_li

    # 3.查询新闻分类
    categories = []
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    category_list = []

    for category in categories:
        category_list.append(category.to_dict())

    # 4.把以上数据封装为为字典返回
    data = {
        'user': user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
        'category_list': category_list
    }

    # 5.渲染模板
    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    """返回页面图标"""
    return current_app.send_static_file('news/favicon.ico')
