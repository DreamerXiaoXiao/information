import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis

from config import config


# 初始化扩展对象，然后再去调用 init_app 方法去初始化

db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def setup_log(config_name):
    """设置日志信息"""

    # 1.设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级

    # 2.创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)

    # 3.创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 4.为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 5.为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """返回app"""

    # 1.设置日志
    setup_log(config_name)
    # 2.创建app
    app = Flask(__name__)
    # 3.加载配置
    config_object = config[config_name]
    app.config.from_object(config_object)

    # 4.加载各种扩展
    # 4.1初始化数据库
    db.init_app(app)

    # 4.2开启CSRF项目保护,只做服务器的验证
    CSRFProtect(app)

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    # 4.3设置session保存到指定位置
    Session(app)

    # 5初始化全局变量
    # 5.1初始化redis存储对象
    global redis_store
    redis_store = StrictRedis(host=config_object.REDIS_HOST,
                              port=config_object.REDIS_PORT,
                              decode_responses=True)

    # 注册过滤器
    # 主页排行过滤器
    from info.utils.common import do_index_class, do_index_active
    app.add_template_filter(do_index_class, 'index_class')
    app.add_template_filter(do_index_active, 'index_active')

    # 6.注册蓝图
    # 6.1主页蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    # 6.2 登录与注册蓝图
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    # 6.3 新闻蓝图
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    # 6.3 用户信息管理蓝图
    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)

    # 7.返回app对象
    return app

