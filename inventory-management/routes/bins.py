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
    # Get filter parameters
    location_id = request.args.get('location_id', type=int)
    search = request.args.get('search', '', type=str)
    active_filter = request.args.get('active', '', type=str)
    page = request.args.get('page', 1, type=int)

    # Build query for inventory - get complete objects
    query = InventoryLevel.query.filter(InventoryLevel.quantity > 0)

    if location_id:
        query = query.filter(InventoryLevel.location_id == location_id)

    # Search filter (by bin code)
    if search:
        # Join with Bin table to search by bin_code
        query = query.join(Bin, InventoryLevel.bin_id == Bin.id, isouter=True).filter(
            Bin.bin_code.ilike(f'%{search}%')
        )

    # Active/Inactive filter (for bins)
    if active_filter == 'active':
        query = query.join(Bin, InventoryLevel.bin_id == Bin.id, isouter=False).filter(Bin.active == True)
    elif active_filter == 'inactive':
        query = query.join(Bin, InventoryLevel.bin_id == Bin.id, isouter=False).filter(Bin.active == False)

    # Pagination
    pagination = query.order_by(InventoryLevel.location_id).paginate(
        page=page, per_page=50, error_out=False
    )
    inventory_items = pagination.items

    # Get all locations for the form
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('bins/index.html',
                          inventory_items=inventory_items,
                          locations=locations,
                          selected_location_id=location_id,
                          pagination=pagination,
                          search=search,
                          active_filter=active_filter)


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

    # Preserve filter parameters on redirect
    return redirect(url_for('bins.index',
                           location_id=request.form.get('location_id'),
                           search=request.form.get('search'),
                           active=request.form.get('active')))
