from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from review.info import create_app, db, models


# 通过指定配置名字创建app
app = create_app('development')
manager = Manager(app)
# 将app与db关联
Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()

