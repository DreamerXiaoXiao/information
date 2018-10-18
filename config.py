from redis import StrictRedis


class Config:
    """项目配置"""
    DEBUG = True  # 开启项目调试

    SECRET_KEY = 'pN8FlXKknxQ7TY8sG8orEtNxrXVSBoafL12HOY/RfxRbU7Wp/khAAd/qnnzCwvtC'

    # 配置数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:jinpeng@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # Session保存配置
    SESSION_TYPE = 'redis'
    # 开启session签名
    SESSION_USE_SIGNER = True
    # 制定Session保存的redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 *2