#coding:utf-8

import os
import click
import sys
from app import create_app,db
from app.models import Role, User, Post, Follow, Permission
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True,include='app/*')
    COV.start()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,
                Permission=Permission,Post=Post,Follow=Follow)

manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)


# @manager.command
# def test():
#     '''
#     run the unit test.
#     '''
#     import unittest
#     tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
@click.option('--coverage/--no-coverage',default=False,
              help='Run tests under code coverage.')
def test(coverage=True):
    '''
    使用coverage 代码覆盖工具进行单元测试
    run the unit tests.
    '''
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.start()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir,'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

if __name__ == '__main__':
    manager.run()