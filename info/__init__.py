from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from config import config

app = Flask(__name__)
# 加载配置
app.config.from_object(config['development'])
# 初始化数据库
db = SQLAlchemy(app)
# 初始化redis存储对象
redis_store = StrictRedis(host=config['development'].REDIS_HOST, port=config['development'].REDIS_PORT)
# 开启CSRF项目波爱护,只做服务器的验证
CSRFProtect(app)
# 设置session保存指定位置
Session(app)