import random
import re
from datetime import datetime

from flask import request, abort, make_response, current_app, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu


@passport_blu.route('/logout', methods=['get'])
def logout():
    """
    退出登录
    1.删除session中的用户信息
    2.返回数据
    :return:
    """
    session.pop('user_id', None)
    session.pop('nick_name', None)
    session.pop('mobile', None)
    session.pop('is_admin', None)
    return jsonify(errno=RET.OK, errmsg='退出成功')


@passport_blu.route('/login', methods=['post'])
def login():
    """
    1.获取参数
    2.校验参数
    3.根据手机号查询用户信息
    4.保存用户登录信息
    5.返回数据
    :return:
    """
    # 1.获取参数
    params_dict = request.json
    mobile = params_dict.get('mobile', None)
    password = params_dict.get('password', None)

    # 2.校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if not re.match(r'1[35678]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 3. 查询用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户失败')

    # 4.校验用户
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 5.校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='密码错误')

    # 6.保存登录信息
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 7.更新用户的最后一次登录时间
    user.last_login = datetime.now()

    # 8.返回数据
    return jsonify(errno=RET.OK, errmsg='登录成功')


@passport_blu.route('/register', methods=["post"])
def register():
    """
    用户注册逻辑
    1.获取参数
    2.校验参数
    3.从redis中获取真实的短信验证码内容
    4.将输入的验证码与与redis取出的进行比较
    5.初始化User模型
    6.向数据库添加信息
    7.返回数据
    :return:
    """
    # 1.获取参数
    params_dict = request.json
    mobile = params_dict.get('mobile')
    sms_code = params_dict.get('sms_code')
    password = params_dict.get('password')

    # 2.校验参数
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if not re.match(r'1[35678]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 3.从redis中获取真实的短信验证码内容
    try:
        real_sms_code = redis_store.get('SMS_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码已过期')

    # 4.将输入的验证码与与redis取出的进行比较
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户失败')

    # 4.校验用户
    if user:
        return jsonify(errno=RET.DATAERR, errmsg='用户已注册')

    # 5.初始化User模型
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 5.1记录用户的最后一次登录时间
    user.last_login = datetime.now()
    user.password = password

    # 6.向数据库添加信息
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    # 7.保存用户信息到session
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 8.返回数据
    return jsonify(errno=RET.OK, errmsg='注册成功')


@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """
    发送短信的逻辑
    1. 获取参数:手机号,图片验证码内容,图片验证码的编号
    2. 校验参数(参数是否服务规则,是否有值)
    3. 先从redis中取出真实的验证码内容
    4. 与用户输入的验证码内容进行对比,如果对比不一致,那么返回验证码输入有误
    5. 如果一致,生成短信验证码的内容(随机数据)
    6. 发送短信验证码
    7. 将短信验证码保存到redis中
    8. 告知发送结果
    :return:
    """
    # 1. 获取参数:手机号,图片验证码的内容,图片验证码的编号
    params_dict = request.json

    mobile = params_dict.get('mobile')
    image_code = params_dict.get('image_code')
    image_code_id = params_dict.get('image_code_id')

    # 2. 校验参数
    # 2.1 判断参数是否有值
    if not all([mobile, image_code, image_code_id]):
        # 返回参数格式{'errno': '4100', 'errmsg': '参数有误'}
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')
    # 2.2 校验手机是否合法
    if not re.match(r'1[35678]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 3. 从redis中取出真是的验证码内容
    try:
        real_image_code = redis_store.get('ImageCodeId_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询失败')

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')

    # 4. 与用户的验证码内容进行对比,如果对比不一致, 那么返回验证码输入有误
    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码输入有误')

    # 5. 如果一致,随机生成6为短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.debug("短信验证码内容是:%s" % sms_code)

    # 6. 发送短信验证码
    # result = CCP().send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg='短信发送失败')
    # 7. 保存验证码内容到redis
    try:
        redis_store.setex('SMS_'+mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据保存失败')

    # 8.告知发送结果
    return jsonify(errno=RET.OK, errmsg='发送成功')


@passport_blu.route('/image_code')
def get_image_code():
    """
    返回图片验证码
    1. 获取参数
    2. 校验参数
    3. 生成验证码
    4. 将验证码内容保存到redis
    5. 设置返回数据格式
    6. 返回图片验证码
    """
    # 1.获取参数
    image_code_id = request.args.get('imageCodeId', None)

    # 2.校验参数
    if not image_code_id:
        abort(403)

    # 3. 生成验证码
    name, text, image = captcha.generate_captcha()

    # 4.将验证码内容保存到redis
    try:
        redis_store.setex('ImageCodeId_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5.设置返回数据格式
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response
