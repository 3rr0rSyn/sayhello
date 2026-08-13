# -*- coding: utf-8 -*-
"""
    Simple admin backend for managing messages.
"""
from functools import wraps

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from sayhello import db
from sayhello.forms import AdminMessageForm, LoginForm
from sayhello.models import Message

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def login_required(view):
    """Decorator that requires admin login."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login', next=request.url))
        return view(**kwargs)
    return wrapped_view


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.index'))

    form = LoginForm()
    if form.validate_on_submit():
        if form.password.data == current_app.config.get('ADMIN_PASSWORD'):
            session['admin_logged_in'] = True
            next_url = request.args.get('next') or url_for('admin.index')
            return redirect(next_url)
        flash('密码错误。')

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
def logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))


@admin_bp.route('/')
@login_required
def index():
    """List all messages in admin panel with pagination and search."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()
    per_page = 10

    query = Message.query.order_by(Message.timestamp.desc())
    if q:
        # Use SQLAlchemy's parameterized ilike to avoid SQL injection.
        pattern = '%{}%'.format(q)
        query = query.filter(
            db.or_(
                Message.name.ilike(pattern),
                Message.body.ilike(pattern)
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    messages = pagination.items
    return render_template('admin/index.html', messages=messages, pagination=pagination, q=q)


@admin_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new message."""
    form = AdminMessageForm()
    if form.validate_on_submit():
        message = Message(name=form.name.data, body=form.body.data)
        db.session.add(message)
        db.session.commit()
        flash('留言已创建。')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit.html', form=form, message=None)


def _get_message_or_404(id):
    """Fetch a message by id or return 404."""
    message = db.session.get(Message, id)
    if message is None:
        abort(404)
    return message


@admin_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing message."""
    message = _get_message_or_404(id)
    form = AdminMessageForm(obj=message)
    if form.validate_on_submit():
        form.populate_obj(message)
        db.session.commit()
        flash('留言已更新。')
        return redirect(url_for('admin.index'))
    return render_template('admin/edit.html', form=form, message=message)


@admin_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a message."""
    message = _get_message_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('留言已删除。')
    return redirect(url_for('admin.index'))
