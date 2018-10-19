from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db

# 通过指定配置的名字创建app
app = create_app('development')
manager = Manager(app)
# 将app与db关联
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command(MigrateCommand)


if __name__ == '__main__':
    manager.run()
