from flask_migrate import Migrate, MigrateCommand
# 需要将表模型导入manage
from info import create_app, db, models
from flask_script import Manager

# 通过指定配置的名字创建app
# 创建app应用,当前环境为开发环境
app = create_app('development')
manager = Manager(app)

# 将app与db关联
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@manager.option('-u', '-username', dest="username")
@manager.option('-p', '-password', dest="password")
def createsuperuser(username, password):
    """通过命令行执行函数,创建管理员用户"""
    if not all([username, password]):
        raise Exception('参数错误')

    from info.models import User
    user = User()
    user.nick_name = username
    user.mobile = username
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
        print("管理员用户添加成功")
        print("当前用户名:%s,密码:%s" % (username, password))
    except Exception as e:
        db.session.rollback()
        print(e)


if __name__ == '__main__':
    print(app.url_map)
    manager.run()


