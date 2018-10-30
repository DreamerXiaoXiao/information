
from flask import render_template, current_app, jsonify, g, abort, request

from info import db
from info.models import News, Comment, CommentLike, User
from info.utils.common import user_login_data, news_order_data
from info.utils.response_code import RET
from . import news_blu


@news_blu.route('/user_followed', methods=["POST"])
@user_login_data
def user_followed():
    """
    取消/添加用户关注
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='未查询到用户信息')

    user_id = request.json.get('user_id')
    action = request.json.get('action')
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    if action not in ('follow', 'unfollow'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        followed_user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    if not followed_user:
        return jsonify(errno=RET.NODATA, errmsg='未关注当前用户')

    if action == 'follow':
        # 关注当前用户
        if followed_user not in user.followed:
            user.followed.append(followed_user)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg='当前用户已关注')
    else:
        if followed_user in user.followed:
            user.followed.remove(followed_user)
        else:
            return jsonify(errno=RET.NODATA, errmsg='当前用户未关注')

    return jsonify(errno=RET.OK, errmsg='OK')


@news_blu.route('/comment_like', methods=['post'])
@user_login_data
def set_comment_like():
    """
    添加/取消用户点赞
    # 1.判断用户是否登录
    # 2.获取参数
    # 3.校验参数
    # 4.初始化评论点赞模型
    # 5.判断是点赞请求/取消点赞请求,更新点赞数量
    # 6.返回数据
    :return:
    """
    # 1.判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户没有登录')
    # 2.获取参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    # 3.校验参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ['add', 'remove']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 4.查询当前评论是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='评论查询错误')

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg='评论不存在')

    # 5.判断是点赞请求/取消点赞请求,更新点赞数量
    comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user.id).first()
    if action == 'add':
        if not comment_like:
            comment_like_model = CommentLike()
            comment_like_model.comment_id = comment_id
            comment_like_model.user_id = user.id
            db.session.add(comment_like_model)
            # 增加评论点赞数量
            comment.like_count += 1
    else:
        if comment_like:
            db.session.delete(comment_like)
            # 减少评论点赞
            comment.like_count -= 1

    # 6.返回数据
    return jsonify(errno=RET.OK, errmsg='OK')


@news_blu.route('/news_comment', methods=['post'])
@user_login_data
def news_comment():
    """
    添加新闻评论
    1.校验用户是否登录
    2.获取参数
    3.校验参数
    4.查询当前新闻
    5.初始化评论模型
    6.返回数据
    :return:
    """
    # 1.校验用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    # 2.获取参数
    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    if not all([news_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据错误')

    # 3.查询新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询错误')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='数据不存在')

    # 4.初始化评论模型
    comment = Comment()
    comment.news_id = news_id
    comment.user_id = user.id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    # 5.保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='评论保存出错')
    # 6.返回数据
    return jsonify(errno=RET.OK, errmsg='OK', data=comment.to_dict())


@news_blu.route('/news_collect', methods=['post'])
@user_login_data
def news_collect():
    """
    新闻收藏功能
    1.用户是否登录
    2.获取参数
    3.校验参数
    4.查询新闻是否被收藏
    :return:
    """
    # 1.用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    # 2.获取参数
    news_id = request.json.get('news_id')
    news_action = request.json.get('action')

    # 3.校验参数
    if not all([news_id, news_action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if news_action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据类型错误')

    # 4.查询新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询错误')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='数据不存在')

    # 5.查看新闻是否在用户收藏列表中
    if news_action == 'collect':
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
    return jsonify(errno=RET.OK, errmsg='OK')


@news_blu.route('/news_detail/<int:news_id>')
@user_login_data
@news_order_data
def news_detail(news_id):
    """
    新闻详情页
    :param news_id:
    :return:
    """
    # 1.查询出user
    user = g.user

    # 2.查询排行新闻数据
    news_dict_li = g.news_dict_li

    # 3.查询新闻详细的数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)  # 新闻不存在,抛出404

    # 新闻存在,更新新闻点击次数
    news.clicks += 1

    # 4.用户收藏逻辑
    is_collected = False
    if user and news in user.collection_news:
        is_collected = True

    # 5.查询当前新闻的全部评论
    comments = None
    try:
        comments = Comment.query.order_by(Comment.create_time.desc()).filter(Comment.news_id==news_id)
    except Exception as e:
        current_app.logger.error(e)

    # 6.显示点赞信息
    comment_like_ids = []
    if user:
        try:
            # 6.1获取当前新闻下所有的评论的id
            comment_ids = [comment.id for comment in comments]
            # 6.2获取当前下登录用户已点赞的id
            if len(comment_ids)>0:
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids), CommentLike.user_id==user.id).all()
                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)
    comment_dict_li = []
    for comment in comments:
        comment_dict = comment.to_dict()
        if comment.id in comment_like_ids and user:
            comment_dict['is_like'] = True
        else:
            comment_dict['is_like'] = False
        comment_dict_li.append(comment_dict)

    # 显示用户是否被关注
    is_followed = False
    if user and news.user in user.followed:
        is_followed = True

    # 7.把以上数据封装为为字典返回
    data = {
        'user': user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
        'news': news.to_dict(),
        'is_collected': is_collected,
        'is_followed': is_followed,
        'comments': comment_dict_li
    }

    # 7.渲染模板
    return render_template('news/detail.html', data=data)


