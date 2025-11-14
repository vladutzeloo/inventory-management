"""
Bin Management routes - Easy assignment of items to bins
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, InventoryLevel, Material, Item, Location, Bin

bp = Blueprint('bins', __name__)


@bp.route('/')
@login_required
def index():
    """Bin management dashboard - assign items to bins easily"""
    # Get location filter
    location_id = request.args.get('location_id', type=int)

    # Build query for inventory - get complete objects
    query = InventoryLevel.query.filter(InventoryLevel.quantity > 0)

    if location_id:
        query = query.filter(InventoryLevel.location_id == location_id)

    inventory_items = query.order_by(InventoryLevel.location_id).all()

    # Get all locations for the form
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('bins/index.html',
                          inventory_items=inventory_items,
                          locations=locations,
                          selected_location_id=location_id)


@bp.route('/assign', methods=['POST'])
@login_required
def assign():
    """Assign inventory to a bin"""
    try:
        inventory_id = int(request.form.get('inventory_id'))
        new_bin_id = request.form.get('new_bin_id')
        new_bin_id = int(new_bin_id) if new_bin_id and new_bin_id != '' else None

        inventory = InventoryLevel.query.get_or_404(inventory_id)

        # Validate bin belongs to same location
        if new_bin_id:
            bin_obj = Bin.query.get_or_404(new_bin_id)
            if bin_obj.location_id != inventory.location_id:
                flash('Bin must be in the same location as the inventory!', 'danger')
                return redirect(url_for('bins.index'))
            new_bin_name = bin_obj.bin_code
        else:
            new_bin_name = 'Location Level'

        old_bin = inventory.bin.bin_code if inventory.bin else 'Location Level'
        inventory.bin_id = new_bin_id
        db.session.commit()

        item_name = inventory.material.name if inventory.material else inventory.item.name

        flash(f'✓ Moved {item_name} from {old_bin} to {new_bin_name}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error assigning bin: {str(e)}', 'danger')

    return redirect(url_for('bins.index', location_id=request.form.get('location_id')))
