"""
Dashboard routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Material, Item, Location, Batch, InventoryLevel
from sqlalchemy import func, case

bp = Blueprint('dashboard', __name__)


@bp.route('/dashboard')
@login_required
def index():
    """Main dashboard"""

    # Total materials and items
    total_materials = Material.query.filter_by(active=True).count()
    total_items = Item.query.filter_by(active=True).count()
    total_locations = Location.query.filter_by(active=True).count()

    # Total inventory value (FIFO)
    total_value = db.session.query(
        func.sum(Batch.quantity_available * Batch.cost_per_unit)
    ).filter(
        Batch.status == 'active',
        Batch.quantity_available > 0
    ).scalar() or 0

    # Total quantity
    total_quantity = db.session.query(
        func.sum(InventoryLevel.quantity)
    ).scalar() or 0

    # Low stock alerts - materials below reorder level
    low_stock_materials = db.session.query(
        Material,
        func.sum(InventoryLevel.quantity).label('total_qty')
    ).join(
        InventoryLevel, Material.id == InventoryLevel.material_id
    ).filter(
        Material.active == True
    ).group_by(
        Material.id
    ).having(
        func.sum(InventoryLevel.quantity) < Material.reorder_level
    ).all()

    # Low stock alerts - items below reorder level
    low_stock_items = db.session.query(
        Item,
        func.sum(InventoryLevel.quantity).label('total_qty')
    ).join(
        InventoryLevel, Item.id == InventoryLevel.item_id
    ).filter(
        Item.active == True
    ).group_by(
        Item.id
    ).having(
        func.sum(InventoryLevel.quantity) < Item.reorder_level
    ).all()

    low_stock_count = len(low_stock_materials) + len(low_stock_items)

    # Inventory by location
    inventory_by_location = db.session.query(
        Location.name,
        func.sum(InventoryLevel.quantity).label('total_qty'),
        func.sum(
            case(
                (InventoryLevel.material_id != None, 1),
                else_=0
            )
        ).label('material_count'),
        func.sum(
            case(
                (InventoryLevel.item_id != None, 1),
                else_=0
            )
        ).label('item_count')
    ).join(
        Location, InventoryLevel.location_id == Location.id
    ).filter(
        Location.active == True,
        InventoryLevel.quantity > 0
    ).group_by(
        Location.name
    ).all()

    # Recent batches (last 10)
    recent_batches = Batch.query.filter(
        Batch.status == 'active'
    ).order_by(
        Batch.received_date.desc()
    ).limit(10).all()

    return render_template('dashboard/index.html',
                          total_materials=total_materials,
                          total_items=total_items,
                          total_locations=total_locations,
                          total_value=total_value,
                          total_quantity=total_quantity,
                          low_stock_count=low_stock_count,
                          low_stock_materials=low_stock_materials,
                          low_stock_items=low_stock_items,
                          inventory_by_location=inventory_by_location,
                          recent_batches=recent_batches)
