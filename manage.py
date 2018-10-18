from flask import Flask
from flask_script import Manager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_migrate import Migrate, MigrateCommand
from config import Config
from info import app, db


manager = Manager(app)
# 将app与db关联
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command(MigrateCommand)


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    manager.run()
