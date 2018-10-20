import logging

from redis import StrictRedis


class Config:
    """项目配置"""
    DEBUG = True

    # 密匙配置
    SECRET_KEY = 'ZTWF7PyXfNz9ZtHi4N3V3uFQVgw49kJ4ESPsIVBvjriYV3K/hZjOsZpkAv9kV8s9'

    # 配置数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:jinpeng@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # session保存配置
    SESSION_TYPE = 'redis'
    # 开启Session签名
    SESSION_SIGNER = True
    # 设置session需要过期
    SESSION_PERMANENT = False
    # 设置session过期时间
    PERMANENT_SESSION_LIFETIME = 86400 *2

    # 设置日志等级
    LOG_LEVEL= logging.DEBUG


class DevelopmentConfig(Config):
    """开发环境"""
    pass


class ProductionConfig(Config):
    """线上环境"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    """测试环境"""
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig

}
