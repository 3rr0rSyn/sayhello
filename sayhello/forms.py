# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class HelloForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(message='该字段为必填项'), Length(1, 20, message='长度须在 1 到 20 个字符之间')])
    body = TextAreaField('留言', validators=[DataRequired(message='该字段为必填项'), Length(1, 200, message='长度须在 1 到 200 个字符之间')])
    submit = SubmitField('发送')


class AdminMessageForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(message='该字段为必填项'), Length(1, 20, message='长度须在 1 到 20 个字符之间')])
    body = TextAreaField('留言', validators=[DataRequired(message='该字段为必填项'), Length(1, 200, message='长度须在 1 到 200 个字符之间')])
    submit = SubmitField('保存')


class LoginForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired(message='该字段为必填项')])
    submit = SubmitField('登录')
