"""
Authentication routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models import db, User

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.active:
                flash('Your account is inactive. Please contact administrator.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user, remember=True)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
