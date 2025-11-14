"""
Bin Management routes - Easy assignment of items to bins
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, InventoryLevel, Material, Item, Location, Bin
from sqlalchemy import func

bp = Blueprint('bins', __name__)


@bp.route('/')
@login_required
def index():
    """Bin management dashboard - assign items to bins easily"""
    # Get location filter
    location_id = request.args.get('location_id', type=int)

    # Build query for inventory with bins
    query = db.session.query(
        InventoryLevel,
        Material.name.label('material_name'),
        Item.name.label('item_name'),
        Location.code.label('location_code'),
        Location.name.label('location_name'),
        Bin.bin_code.label('bin_code')
    ).outerjoin(Material, InventoryLevel.material_id == Material.id)\
     .outerjoin(Item, InventoryLevel.item_id == Item.id)\
     .join(Location, InventoryLevel.location_id == Location.id)\
     .outerjoin(Bin, InventoryLevel.bin_id == Bin.id)\
     .filter(InventoryLevel.quantity > 0)

    if location_id:
        query = query.filter(InventoryLevel.location_id == location_id)

    inventory_data = query.order_by(Location.code, Material.name, Item.name).all()

    # Get all locations and bins for the form
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('bins/index.html',
                          inventory_data=inventory_data,
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

        old_bin = inventory.bin.bin_code if inventory.bin else 'Location Level'
        inventory.bin_id = new_bin_id
        db.session.commit()

        item_name = inventory.material.name if inventory.material else inventory.item.name
        new_bin_name = bin_obj.bin_code if new_bin_id else 'Location Level'

        flash(f'✓ Moved {item_name} from {old_bin} to {new_bin_name}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error assigning bin: {str(e)}', 'danger')

    return redirect(url_for('bins.index', location_id=request.form.get('location_id')))


@bp.route('/api/inventory/<int:location_id>')
@login_required
def api_inventory(location_id):
    """API endpoint to get inventory for a location"""
    inventory = db.session.query(
        InventoryLevel,
        Material.name.label('material_name'),
        Item.name.label('item_name')
    ).outerjoin(Material, InventoryLevel.material_id == Material.id)\
     .outerjoin(Item, InventoryLevel.item_id == Item.id)\
     .filter(InventoryLevel.location_id == location_id)\
     .filter(InventoryLevel.quantity > 0)\
     .all()

    result = []
    for inv, mat_name, item_name in inventory:
        result.append({
            'id': inv.id,
            'name': mat_name or item_name,
            'quantity': float(inv.quantity),
            'current_bin_id': inv.bin_id,
            'current_bin': inv.bin.bin_code if inv.bin else 'Location Level'
        })

    return jsonify(result)
