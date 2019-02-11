from datetime import datetime, timedelta

from info import constants, db
from info.utils import image_storage
from info.utils.response_code import RET
from . import admin_blu
from flask import render_template, request, g, current_app, session, redirect, url_for, jsonify, abort

from info.models import User, News, Category
from info.utils.common import user_login_data


@admin_blu.route('/news_type', methods=["POST", "GET"])
def news_type():
    """
    新闻分类
    :return:
    """
    # 查询新闻所有分类
    if request.method == "GET":
        categories = []
        try:
            categories = Category.query.filter(Category.id != 1).all()
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        category_dict_li = []
        for category in categories:
            category_dict_li.append(category.to_dict())
        data = {
            'categories': category_dict_li
        }
        return render_template('admin/news_type.html', data=data)

    # 增加/修改分类
    category_id = request.json.get('id')
    category_name = request.json.get('name')
    if not category_name:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if category_id:
        try:
            category_id = int(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        try:
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
        if not category:
            return jsonify(errno=RET.NODATA, errmsg='没有数据')
        category.name = category_name
    else:
        c = Category()
        c.name = category_name
        try:
            db.session.add(c)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg='OK')


@admin_blu.route('/news_edit_detail',  methods=["POST", "GET"])
def news_edit_detail():
    """
    新闻编辑详情页
    :return:
    """
    if request.method == "GET":
        news_id = request.args.get("news_id")
        if not news_id:
            abort(404)
        news = None
        try:
            news_id = int(news_id)
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)

        if not news:
            abort(404)

        # 查询新闻所有分类
        categories = []
        try:
            categories = Category.query.filter(Category.id != 1).all()
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        category_dict_li = []
        for category in categories:
            category_dict = category.to_dict()
            if category.id == news.category_id:
                category_dict['is_select'] = True
            category_dict_li.append(category_dict)

        data = {
            'news': news.to_dict(),
            'categories': category_dict_li
        }
        return render_template('admin/news_edit_detail.html',data=data)

    # 新闻编辑功能实现
    news_id = request.form.get('news_id')
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image_url = request.files.get('index_image_url')
    content = request.form.get('content')
    if not all([news_id, title, category_id, digest, index_image_url, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        images_data = index_image_url.read()
        key = image_storage.storage(images_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='图片上传失败')

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')

    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.content = content
    return jsonify(errno=RET.OK, errmsg='OK')


@admin_blu.route('/news_edit')
def news_edit():
    """
    新闻版式编辑
    :return:
    """
    title = request.args.get('title', '')
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    total_page = 1
    current_page = 1
    try:
        filters = [News.status == 0]
        if title:
            filters.append(News.title.contains(title))
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,
                                                                                          constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                          False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_list_li = []
    for news in news_list:
        news_list_li.append(news.to_basic_dict())

    data = {
        'news_list': news_list_li,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('admin/news_edit.html', data=data)


@admin_blu.route('/news_review_action', methods=["POST"])
def news_review_action():
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ('accept', 'reject'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻没有查询到')

    if action == "accept":
        # 审核通过
        news.status = 0
    else:
        # 审核不通过
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.NODATA, errmsg='请输入拒绝原因')
        news.status = -1

    return jsonify(errno=RET.OK, errmsg='OK')


@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    """
    新闻审核详情
    :return:
    """
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return render_template('admin/news_review_detail.html', data={'errmsg': '没有查询到当前数据'})

    data = {
        'news': news.to_dict()
    }

    return render_template('admin/news_review_detail.html', data=data)


@admin_blu.route('/news_review')
def news_review():
    """
    新闻审核
    :return:
    """
    title = request.args.get('title', '')
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    total_page = 1
    current_page = 1
    try:
        filters = [News.status != 0]
        if title:
            filters.append(News.title.contains(title))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_list_li = []
    for news in news_list:
        news_list_li.append(news.to_review_dict())

    data = {
        'news_list': news_list_li,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('admin/news_review.html', data=data)


@admin_blu.route('/user_list')
def user_list():
    """
    查询所有用户信息
    :return:
    """
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    users = []
    total_page = 1
    current_page = 1

    try:
        paginate = User.query.filter(User.is_admin==False).order_by(User.create_time.desc()).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []
    for user in users:
        user_dict_li.append(user.to_admin_dict())

    data = {
        'users': user_dict_li,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('admin/user_list.html', data=data)


@admin_blu.route('/user_count')
def user_count():
    """
    用户统计
    :return:
    """
    # 查询总用户数
    total_count = 1
    try:
        total_count = User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询本月用户数
    mon_count = 1
    now = datetime.now()
    mon_date = datetime(now.year, now.month, 1)
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time>mon_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询当天用户数
    day_count = 1
    today_date = datetime(now.year, now.month, now.day)
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > today_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 当月用户活跃数
    active_counts = []
    # 当前用户每一天
    active_days = []
    for i in range(0, 31):
        begin_date = today_date - timedelta(days=i)
        end_date = today_date + timedelta(days=1) - timedelta(days=i)
        active_day = 0
        try:
            active_day = User.query.filter(User.is_admin == False,
                                          User.last_login > begin_date,
                                          User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        active_counts.append(active_day)
        active_days.append(begin_date.strftime("%Y-%m-%d"))

    active_days.reverse()
    active_counts.reverse()
    data = {
        'total_count': total_count,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_counts': active_counts,
        'active_days': active_days,
    }

    return render_template('admin/user_count.html', data=data)


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
