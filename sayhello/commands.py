# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import click

from sayhello import app, db
from sayhello.models import Message


@app.cli.command()
@click.option('--drop', is_flag=True, help='先删除再创建。')
def initdb(drop):
    """Initialize the database."""
    if drop:
        click.confirm('此操作将删除数据库，是否继续？', abort=True)
        db.drop_all()
        click.echo('已删除表。')
    db.create_all()
    click.echo('数据库已初始化。')


@app.cli.command()
@click.option('--count', default=40, help='留言数量，默认 40。')
def forge(count):
    """Generate fake messages."""
    from faker import Faker

    db.drop_all()
    db.create_all()

    fake = Faker()
    click.echo('生成中...')

    for i in range(count):
        message = Message(
            name=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(message)

    db.session.commit()
    click.echo('已生成 %d 条测试留言。' % count)
