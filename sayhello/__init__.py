# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import Flask
from flask_bootstrap import Bootstrap4
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

app = Flask('sayhello')
app.config.from_pyfile('settings.py')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

db = SQLAlchemy()
db.init_app(app)

bootstrap = Bootstrap4(app)
moment = Moment(app)

from sayhello import views, errors, commands
from sayhello.admin import admin_bp

app.register_blueprint(admin_bp)


def _create_tables():
    """Auto-create tables on the first request if they don't exist yet."""
    db.create_all()
    app.before_request_funcs[None].remove(_create_tables)


app.before_request(_create_tables)
