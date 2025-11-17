"""
User management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User
from functools import wraps

bp = Blueprint('users', __name__, url_prefix='/users')


def admin_required(f):
    """Decorator to require admin user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll check if the user is 'admin'
        # In a more sophisticated system, you'd have a role-based system
        if current_user.username != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
@admin_required
def index():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/index.html', users=users)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    """Add a new user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()

        # Validation
        if not username:
            flash('Username is required.', 'danger')
            return redirect(url_for('users.add'))

        if not password:
            flash('Password is required.', 'danger')
            return redirect(url_for('users.add'))

        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('users.add'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f'Username "{username}" already exists.', 'danger')
            return redirect(url_for('users.add'))

        # Create new user
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(f'User "{username}" created successfully.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/add.html')


@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()

        # Update user details
        user.full_name = full_name
        user.email = email

        # Update password if provided
        if password:
            if password != password_confirm:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('users.edit', user_id=user_id))
            user.set_password(password)

        db.session.commit()
        flash(f'User "{user.username}" updated successfully.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/edit.html', user=user)


@bp.route('/<int:user_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)

    # Prevent disabling the admin user
    if user.username == 'admin':
        flash('Cannot disable the admin user.', 'danger')
        return redirect(url_for('users.index'))

    user.active = not user.active
    db.session.commit()

    status = 'activated' if user.active else 'deactivated'
    flash(f'User "{user.username}" {status} successfully.', 'success')
    return redirect(url_for('users.index'))


@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)

    # Prevent deleting the admin user
    if user.username == 'admin':
        flash('Cannot delete the admin user.', 'danger')
        return redirect(url_for('users.index'))

    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('users.index'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'User "{username}" deleted successfully.', 'success')
    return redirect(url_for('users.index'))
