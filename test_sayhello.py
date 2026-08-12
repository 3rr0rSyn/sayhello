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
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(app is None)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('404 Error', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    def test_500_page(self):
        response = self.client.get('/500')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn('500 Error', data)
        self.assertIn('Go Back', data)

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
        self.assertIn('Your message have been sent to the world!', data)
        self.assertIn('Hello, world.', data)

    def test_form_validation(self):
        response = self.client.post('/', data=dict(
            name=' ',
            body='Hello, world.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This field is required.', data)

    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Created 20 fake messages.', result.output)
        self.assertEqual(Message.query.count(), 20)

    def test_forge_command_with_count(self):
        result = self.runner.invoke(forge, ['--count', '50'])
        self.assertIn('Created 50 fake messages.', result.output)
        self.assertEqual(Message.query.count(), 50)

    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(initdb, ['--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)


class AdminTestCase(unittest.TestCase):

    def setUp(self):
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
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

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
        self.assertIn('Message Admin', data)

    def test_admin_login_invalid(self):
        response = self.client.post('/admin/login', data=dict(password='wrong'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid password.', data)

    def test_admin_create_message(self):
        self.login()
        response = self.client.post('/admin/create', data=dict(name='Admin', body='Created in admin.'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Message created.', data)
        self.assertIn('Created in admin.', data)
        self.assertEqual(Message.query.count(), 1)

    def test_admin_edit_message(self):
        self.login()
        message = Message(name='Old', body='Old body')
        db.session.add(message)
        db.session.commit()

        response = self.client.post('/admin/edit/1', data=dict(name='New', body='New body.'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Message updated.', data)
        self.assertIn('New body.', data)

    def test_admin_delete_message(self):
        self.login()
        message = Message(name='ToDelete', body='Delete me.')
        db.session.add(message)
        db.session.commit()
        self.assertEqual(Message.query.count(), 1)

        response = self.client.post('/admin/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Message deleted.', data)
        self.assertEqual(Message.query.count(), 0)


if __name__ == '__main__':
    unittest.main()
