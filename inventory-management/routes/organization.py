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


@bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """Delete category with protection"""
    category = Category.query.get_or_404(id)

    # Check if category is in use
    materials_count = len(category.materials)
    items_count = len(category.items)

    if materials_count > 0 or items_count > 0:
        flash(f'Cannot delete category "{category.name}" - it is linked to {materials_count} material(s) and {items_count} item(s). Please unlink them first.', 'danger')
        return redirect(url_for('organization.categories'))

    try:
        db.session.delete(category)
        db.session.commit()
        flash(f'Category "{category.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('organization.categories'))


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


@bp.route('/clients/<int:id>/delete', methods=['POST'])
@login_required
def delete_client(id):
    """Delete client with protection"""
    client = Client.query.get_or_404(id)

    # Check if client is in use
    items_count = len(client.items)

    if items_count > 0:
        flash(f'Cannot delete client "{client.name}" - it is linked to {items_count} item(s). Please unlink them first.', 'danger')
        return redirect(url_for('organization.clients'))

    try:
        db.session.delete(client)
        db.session.commit()
        flash(f'Client "{client.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting client: {str(e)}', 'danger')

    return redirect(url_for('organization.clients'))


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


@bp.route('/providers/<int:id>/delete', methods=['POST'])
@login_required
def delete_provider(id):
    """Delete provider with protection"""
    provider = Provider.query.get_or_404(id)

    # Check if provider is in use
    materials_count = len(provider.materials)

    if materials_count > 0:
        flash(f'Cannot delete provider "{provider.name}" - it is linked to {materials_count} material(s). Please unlink them first.', 'danger')
        return redirect(url_for('organization.providers'))

    try:
        db.session.delete(provider)
        db.session.commit()
        flash(f'Provider "{provider.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting provider: {str(e)}', 'danger')

    return redirect(url_for('organization.providers'))
