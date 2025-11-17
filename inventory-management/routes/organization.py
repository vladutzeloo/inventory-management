"""
Organization routes - Categories, Clients, and Providers management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Category, Client, Provider

bp = Blueprint('organization', __name__)


# ==================== CATEGORIES ====================

@bp.route('/categories')
@login_required
def categories():
    """List all categories"""
    categories = Category.query.order_by(Category.category_type, Category.name).all()
    return render_template('organization/categories.html', categories=categories)


@bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    """Create new category"""
    if request.method == 'POST':
        try:
            category = Category(
                name=request.form['name'].strip(),
                description=request.form.get('description', '').strip(),
                category_type=request.form['category_type'],
                active=True
            )
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{category.name}" created successfully!', 'success')
            return redirect(url_for('organization.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating category: {str(e)}', 'danger')

    return render_template('organization/category_form.html', category=None)


@bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Edit category"""
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        try:
            category.name = request.form['name'].strip()
            category.description = request.form.get('description', '').strip()
            category.category_type = request.form['category_type']
            category.active = 'active' in request.form

            db.session.commit()
            flash(f'Category "{category.name}" updated successfully!', 'success')
            return redirect(url_for('organization.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating category: {str(e)}', 'danger')

    return render_template('organization/category_form.html', category=category)


# ==================== CLIENTS ====================

@bp.route('/clients')
@login_required
def clients():
    """List all clients"""
    clients = Client.query.order_by(Client.name).all()
    return render_template('organization/clients.html', clients=clients)


@bp.route('/clients/new', methods=['GET', 'POST'])
@login_required
def new_client():
    """Create new client"""
    if request.method == 'POST':
        try:
            client = Client(
                name=request.form['name'].strip(),
                code=request.form['code'].strip().upper(),
                contact_person=request.form.get('contact_person', '').strip(),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                address=request.form.get('address', '').strip(),
                active=True
            )
            db.session.add(client)
            db.session.commit()
            flash(f'Client "{client.name}" created successfully!', 'success')
            return redirect(url_for('organization.clients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating client: {str(e)}', 'danger')

    return render_template('organization/client_form.html', client=None)


@bp.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    """Edit client"""
    client = Client.query.get_or_404(id)

    if request.method == 'POST':
        try:
            client.name = request.form['name'].strip()
            client.code = request.form['code'].strip().upper()
            client.contact_person = request.form.get('contact_person', '').strip()
            client.email = request.form.get('email', '').strip()
            client.phone = request.form.get('phone', '').strip()
            client.address = request.form.get('address', '').strip()
            client.active = 'active' in request.form

            db.session.commit()
            flash(f'Client "{client.name}" updated successfully!', 'success')
            return redirect(url_for('organization.clients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating client: {str(e)}', 'danger')

    return render_template('organization/client_form.html', client=client)


# ==================== PROVIDERS ====================

@bp.route('/providers')
@login_required
def providers():
    """List all providers"""
    providers = Provider.query.order_by(Provider.name).all()
    return render_template('organization/providers.html', providers=providers)


@bp.route('/providers/new', methods=['GET', 'POST'])
@login_required
def new_provider():
    """Create new provider"""
    if request.method == 'POST':
        try:
            provider = Provider(
                name=request.form['name'].strip(),
                code=request.form['code'].strip().upper(),
                contact_person=request.form.get('contact_person', '').strip(),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                address=request.form.get('address', '').strip(),
                active=True
            )
            db.session.add(provider)
            db.session.commit()
            flash(f'Provider "{provider.name}" created successfully!', 'success')
            return redirect(url_for('organization.providers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating provider: {str(e)}', 'danger')

    return render_template('organization/provider_form.html', provider=None)


@bp.route('/providers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_provider(id):
    """Edit provider"""
    provider = Provider.query.get_or_404(id)

    if request.method == 'POST':
        try:
            provider.name = request.form['name'].strip()
            provider.code = request.form['code'].strip().upper()
            provider.contact_person = request.form.get('contact_person', '').strip()
            provider.email = request.form.get('email', '').strip()
            provider.phone = request.form.get('phone', '').strip()
            provider.address = request.form.get('address', '').strip()
            provider.active = 'active' in request.form

            db.session.commit()
            flash(f'Provider "{provider.name}" updated successfully!', 'success')
            return redirect(url_for('organization.providers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating provider: {str(e)}', 'danger')

    return render_template('organization/provider_form.html', provider=provider)
