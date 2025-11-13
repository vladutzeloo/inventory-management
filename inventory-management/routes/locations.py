"""
Locations and bins management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Location, Bin, InventoryLevel
from sqlalchemy import func

bp = Blueprint('locations', __name__)


@bp.route('/')
@login_required
def index():
    """List all locations"""
    locations = Location.query.order_by(Location.location_type, Location.code).all()

    # Get inventory count for each location
    locations_with_inventory = []
    for location in locations:
        inventory_count = db.session.query(func.count(InventoryLevel.id)).filter(
            InventoryLevel.location_id == location.id,
            InventoryLevel.quantity > 0
        ).scalar() or 0

        total_qty = db.session.query(func.sum(InventoryLevel.quantity)).filter(
            InventoryLevel.location_id == location.id
        ).scalar() or 0

        bin_count = Bin.query.filter_by(location_id=location.id, active=True).count()

        locations_with_inventory.append((location, inventory_count, total_qty, bin_count))

    return render_template('locations/index.html',
                          locations=locations_with_inventory)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new location"""
    if request.method == 'POST':
        try:
            location = Location(
                code=request.form['code'].strip().upper(),
                name=request.form['name'].strip(),
                location_type=request.form['location_type'],
                zone=request.form.get('zone', '').strip(),
                active=request.form.get('active') == 'on'
            )

            db.session.add(location)
            db.session.commit()

            flash(f'Location "{location.code}" created successfully!', 'success')
            return redirect(url_for('locations.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating location: {str(e)}', 'danger')

    return render_template('locations/new.html')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit location"""
    location = Location.query.get_or_404(id)

    if request.method == 'POST':
        try:
            location.code = request.form['code'].strip().upper()
            location.name = request.form['name'].strip()
            location.location_type = request.form['location_type']
            location.zone = request.form.get('zone', '').strip()
            location.active = request.form.get('active') == 'on'

            db.session.commit()

            flash(f'Location "{location.code}" updated successfully!', 'success')
            return redirect(url_for('locations.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating location: {str(e)}', 'danger')

    return render_template('locations/edit.html', location=location)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete location"""
    location = Location.query.get_or_404(id)

    # Check if location has inventory
    has_inventory = InventoryLevel.query.filter_by(location_id=id).first() is not None

    if has_inventory:
        flash(f'Cannot delete location "{location.code}" - it has inventory records.', 'danger')
        return redirect(url_for('locations.index'))

    try:
        # Delete associated bins first
        Bin.query.filter_by(location_id=id).delete()
        db.session.delete(location)
        db.session.commit()
        flash(f'Location "{location.code}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting location: {str(e)}', 'danger')

    return redirect(url_for('locations.index'))


@bp.route('/<int:id>/bins')
@login_required
def bins(id):
    """View bins for a location"""
    location = Location.query.get_or_404(id)
    bins = Bin.query.filter_by(location_id=id).order_by(Bin.bin_code).all()

    # Get inventory count for each bin
    bins_with_inventory = []
    for bin in bins:
        inventory_count = db.session.query(func.count(InventoryLevel.id)).filter(
            InventoryLevel.bin_id == bin.id,
            InventoryLevel.quantity > 0
        ).scalar() or 0

        total_qty = db.session.query(func.sum(InventoryLevel.quantity)).filter(
            InventoryLevel.bin_id == bin.id
        ).scalar() or 0

        bins_with_inventory.append((bin, inventory_count, total_qty))

    return render_template('locations/bins.html',
                          location=location,
                          bins=bins_with_inventory)


@bp.route('/<int:id>/bins/new', methods=['GET', 'POST'])
@login_required
def new_bin(id):
    """Create new bin for location"""
    location = Location.query.get_or_404(id)

    if request.method == 'POST':
        try:
            bin = Bin(
                location_id=id,
                bin_code=request.form['bin_code'].strip().upper(),
                description=request.form.get('description', '').strip(),
                active=request.form.get('active') == 'on'
            )

            db.session.add(bin)
            db.session.commit()

            flash(f'Bin "{bin.bin_code}" created successfully!', 'success')
            return redirect(url_for('locations.bins', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bin: {str(e)}', 'danger')

    return render_template('locations/new_bin.html', location=location)


@bp.route('/bins/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bin(id):
    """Edit bin"""
    bin = Bin.query.get_or_404(id)
    location = bin.location

    if request.method == 'POST':
        try:
            bin.bin_code = request.form['bin_code'].strip().upper()
            bin.description = request.form.get('description', '').strip()
            bin.active = request.form.get('active') == 'on'

            db.session.commit()

            flash(f'Bin "{bin.bin_code}" updated successfully!', 'success')
            return redirect(url_for('locations.bins', id=location.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating bin: {str(e)}', 'danger')

    return render_template('locations/edit_bin.html', bin=bin, location=location)


@bp.route('/bins/<int:id>/delete', methods=['POST'])
@login_required
def delete_bin(id):
    """Delete bin"""
    bin = Bin.query.get_or_404(id)
    location_id = bin.location_id

    # Check if bin has inventory
    has_inventory = InventoryLevel.query.filter_by(bin_id=id).first() is not None

    if has_inventory:
        flash(f'Cannot delete bin "{bin.bin_code}" - it has inventory records.', 'danger')
        return redirect(url_for('locations.bins', id=location_id))

    try:
        db.session.delete(bin)
        db.session.commit()
        flash(f'Bin "{bin.bin_code}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting bin: {str(e)}', 'danger')

    return redirect(url_for('locations.bins', id=location_id))


@bp.route('/api/bins/<int:location_id>')
@login_required
def api_bins(location_id):
    """API endpoint to get bins for a location"""
    bins = Bin.query.filter_by(location_id=location_id, active=True).order_by(Bin.bin_code).all()
    return jsonify([{'id': b.id, 'bin_code': b.bin_code, 'description': b.description} for b in bins])
