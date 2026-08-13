# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import unittest

from flask import abort

from sayhello import app, db
from sayhello.models import Message
from sayhello.commands import forge, initdb


# Register a test-only route before the app handles its first request.
@app.route('/500')
def internal_server_error_for_test():
    abort(500)


class SayHelloTestCase(unittest.TestCase):

    def setUp(self):
        import os
        # Make sure the default dev database does not pollute tests.
        if os.path.exists('data.db'):
            os.remove('data.db')
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )

        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        import os
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()
        # Remove any leftover on-disk test database so the next run starts clean.
        if os.path.exists('data.db'):
            os.remove('data.db')

    def test_app_exist(self):
        self.assertFalse(app is None)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('404 错误', data)
        self.assertIn('返回首页', data)
        self.assertEqual(response.status_code, 404)

    def test_500_page(self):
        response = self.client.get('/500')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn('500 错误', data)
        self.assertIn('返回首页', data)

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Say Hello', data)

    def test_create_message(self):
        response = self.client.post('/', data=dict(
            name='Peter',
            body='Hello, world.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('你的留言已发送给全世界！', data)
        self.assertIn('Hello, world.', data)

    def test_form_validation(self):
        response = self.client.post('/', data=dict(
            name=' ',
            body='Hello, world.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('该字段为必填项', data)

    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('已生成 40 条测试留言。', result.output)
        self.assertEqual(Message.query.count(), 40)

    def test_forge_command_with_count(self):
        result = self.runner.invoke(forge, ['--count', '50'])
        self.assertIn('已生成 50 条测试留言。', result.output)
        self.assertEqual(Message.query.count(), 50)

    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('数据库已初始化。', result.output)

    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(initdb, ['--drop'], input='y\n')
        self.assertIn('此操作将删除数据库，是否继续？', result.output)
        self.assertIn('已删除表。', result.output)


class AdminTestCase(unittest.TestCase):

    def setUp(self):
        import os
        # Make sure the default dev database does not pollute tests.
        if os.path.exists('data.db'):
            os.remove('data.db')
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            ADMIN_PASSWORD='testpass'
        )
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        import os
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()
        # Remove any leftover on-disk test database so the next run starts clean.
        if os.path.exists('data.db'):
            os.remove('data.db')

    def login(self):
        return self.client.post('/admin/login', data=dict(password='testpass'), follow_redirects=True)

    def test_admin_login_required(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login', response.location)

    def test_admin_login(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('留言管理', data)

    def test_admin_login_invalid(self):
        response = self.client.post('/admin/login', data=dict(password='wrong'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('密码错误。', data)

    def test_admin_create_message(self):
        self.login()
        response = self.client.post('/admin/create', data=dict(name='Admin', body='Created in admin.'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('留言已创建。', data)
        self.assertIn('Created in admin.', data)
        self.assertEqual(Message.query.count(), 1)

    def test_admin_edit_message(self):
        self.login()
        message = Message(name='Old', body='Old body')
        db.session.add(message)
        db.session.commit()

        response = self.client.post('/admin/edit/1', data=dict(name='New', body='New body.'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('留言已更新。', data)
        self.assertIn('New body.', data)

    def test_admin_delete_message(self):
        self.login()
        message = Message(name='ToDelete', body='Delete me.')
        db.session.add(message)
        db.session.commit()
        self.assertEqual(Message.query.count(), 1)

        response = self.client.post('/admin/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('留言已删除。', data)
        self.assertEqual(Message.query.count(), 0)

    def test_admin_pagination(self):
        self.login()
        for i in range(15):
            db.session.add(Message(name='User %d' % i, body='Body %d' % i))
        db.session.commit()

        response = self.client.get('/admin/?page=1')
        data = response.get_data(as_text=True)
        self.assertIn('共 15 条留言', data)
        self.assertIn('page=2', data)
        messages_page_1 = Message.query.order_by(Message.timestamp.desc()).limit(10).all()
        self.assertEqual(len(messages_page_1), 10)

        response = self.client.get('/admin/?page=2')
        data = response.get_data(as_text=True)
        self.assertIn('共 15 条留言', data)
        messages_page_2 = Message.query.order_by(Message.timestamp.desc()).offset(10).limit(10).all()
        self.assertEqual(len(messages_page_2), 5)

    def test_admin_search(self):
        self.login()
        db.session.add(Message(name='Alice', body='Hello world'))
        db.session.add(Message(name='Bob', body='Goodbye world'))
        db.session.add(Message(name='Charlie', body='Nothing here'))
        db.session.commit()

        response = self.client.get('/admin/?q=world')
        data = response.get_data(as_text=True)
        self.assertIn('Alice', data)
        self.assertIn('Bob', data)
        self.assertNotIn('Charlie', data)

        response = self.client.get('/admin/?q=Alice')
        data = response.get_data(as_text=True)
        self.assertIn('Alice', data)
        self.assertNotIn('Bob', data)


if __name__ == '__main__':
    unittest.main()
