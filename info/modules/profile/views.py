from flask import render_template, g, request, redirect, jsonify, current_app, url_for, abort

from info import constants, db
from info.models import Category, News, User
from info.utils import image_storage
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import profile_blu


@profile_blu.route('/other_news_list')
def other_news_list():
    """
    显示其他用户的新闻详情
    :return:
    """
    other_id = request.args.get('user_id')
    page = request.args.get('page', 1)
    if not other_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    if not other:
        return jsonify(errno=RET.NODATA, errmsg='未查询到数据')
    try:
        paginate = other.news_list.paginate(page, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    news_dict_li = []
    for news_dict in news_list:
        news_dict_li.append(news_dict.to_basic_dict())
    data = {
        'news_list': news_dict_li,
        'current_page': current_page,
        'total_page': total_page
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@profile_blu.route('/user_other')
@user_login_data
def user_other():
    """
    显示其他用户的详情
    :return:
    """
    user = g.user
    if not user:
        abort(404)
    user_id = request.args.get('user_id')
    if not user_id:
        abort(404)
    other = None
    try:
        user_id = int(user_id)
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    is_followed = False
    # 判断当前登录用户是否关注过该用户
    is_followed = False
    if user and other.followers.filter(User.id == user.id).count() > 0:
        is_followed = True

    # 组织数据，并返回
    data = {
        'user': user.to_dict() if user else None,
        "other": other.to_dict(),
        "is_followed": is_followed
    }
    return render_template('news/other.html', data=data)


@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    """
    用户关注
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户没有登录')
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
        paginate = user.followed.paginate(page,constants.USER_FOLLOWED_MAX_COUNT, False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 显示用户是否被关注

    user_dict_li = []
    for user_followed in users:
        user_dict_li.append(user_followed.to_dict())

    data = {
        'user': user.to_dict() if user else None,
        'users': user_dict_li,
        'total_page': total_page,
        'current_page': current_page
    }
    return render_template('news/user_follow.html', data=data)


@profile_blu.route('/news_list')
@user_login_data
def user_news_list():
    """
        # 1.显示发布新闻
        # 2.返回响应
        :return:
        """
    user = g.user
    if not user:
        return redirect('/')

    # 1.获取参数
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
        paginate = News.query.filter(News.user_id == user.id).\
            order_by(News.create_time.desc()).\
            paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_review_dict())

    data = {
        'news_list': news_dict_li,
        'total_page': total_page,
        'current_page': current_page,
    }

    return render_template('news/user_news_list.html', data=data)


@profile_blu.route('/news_release', methods=['POST', 'GET'])
@user_login_data
def news_release():
    """
    发布新闻
    get
    1.显示前段信息
    :return:
    """
    if request.method == 'GET':
        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        category_dict_li = []
        for category in categories:
            category_dict_li.append(category.to_dict())

        category_dict_li.pop(0)
        data = {
            'categories': category_dict_li
        }
        return render_template('news/user_news_release.html', data=data)

    # 获取参数
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image = request.files.get('index_image')
    content = request.form.get('content')

    # 校验参数
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 上传新闻图片
    try:
        index_image_content = index_image.read()
        key = image_storage.storage(index_image_content)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='新闻图片上传错误')

    # 初始化新闻模型
    news = News()
    news.title = title
    news.category_id = category_id
    news.source = '个人发布'
    news.content = content
    news.user_id = g.user.id
    news.digest = digest
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key

    # 标记当前新闻的状态
    news.status = 1  # 审核状态
    # 保存到数据库

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据保存失败')

    return jsonify(errno=RET.OK, errmsg='新闻发布成功')


@profile_blu.route('/collection')
@user_login_data
def user_collection():
    """
    # 1.查询用户收藏新闻
    # 2.返回响应
    :return:
    """
    user = g.user
    if not user:
        return redirect('/')

    # 1.获取参数
    page = request.args.get('page', 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    collections = []
    total_page = 1
    current_page = 1
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        collections = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)

    collection_news_li = []
    for news in collections:
        collection_news_li.append(news.to_basic_dict())

    data = {
        'collections': collections,
        'total_page': total_page,
        'current_page': current_page
    }

    return render_template('news/user_collection.html', data=data)


@profile_blu.route('/pass_info', methods=['GET', "POST"])
@user_login_data
def pass_info():
    """
    # 1.获取参数
    # 2.校验参数
    # 3.修改密码
    # 4.返回响应
    :return:
    """
    # 1.如果用户不存在,重定向到主页
    user = g.user
    if not user:
        return redirect('/')

    if request.method == "GET":
        return render_template('news/user_pass_info.html')

    # 2.获取参数
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    new_password2 = request.json.get('new_password2')

    # 3.校验参数
    if not all([old_password, new_password, new_password2]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if new_password != new_password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不一致')

    # 4.修改密码
    if not user.check_password(old_password):
        return jsonify(errno=RET.PARAMERR, errmsg='原密码错误')

    user.password = new_password
    # 5.返回响应
    return jsonify(errno=RET.OK, errmsg='密码修改成功')


@profile_blu.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """
    用户头像上传
    # 1.如果用户不存在,重定向到主页
    # 2.获取参数
    # 3.校验参数
    # 4.更新用户信息
    :return:
    """
    # 1.如果用户不存在,重定向到主页
    user = g.user
    if not user:
        return redirect('/')
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user": user.to_dict() if user else None})

    # 2.获取参数
    try:
        avatar = request.files.get('avatar').read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 3.校验参数
    if not avatar:
        return jsonify(errno=RET.NODATA, errmsg='没有数据')

    try:
        key = image_storage.storage(avatar)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='图片上传失败')

    # 4.添加用户头像信息
    user.avatar_url = key
    data = {
        'avatar_url': constants.QINIU_DOMIN_PREFIX + key
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


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
    return jsonify(errno=RET.OK, errmsg='修改成功')


@profile_blu.route('/user_info')
@user_login_data
def user_info():
    # 如果用户不存在,直接重定向主页
    user = g.user
    if not user:
        return redirect('/')
    return render_template('news/user.html', data={'user': user.to_dict()})

