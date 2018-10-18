from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config


# 初始化扩展的对象，然后再去调用 init_app 方法去初始化
db = SQLAlchemy()
redis_store = None  # type : StrictRedis


def create_app(config_name):
    """通过指定的名字创建配置"""
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 初始化数据库
    db.init_app(app)
    # 初始化redis存储对象
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT)
    # 开启CSRF项目波爱护,只做服务器的验证
    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)
    return app
