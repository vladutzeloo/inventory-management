"""
Dashboard routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Material, Item, Location, Batch, InventoryLevel, Receipt, Transfer, Scrap, ScrapBatch
from sqlalchemy import func, case
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)


@bp.route('/dashboard')
@login_required
def index():
    """Main dashboard with actionable insights"""

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

    # Scrap value and count
    scrap_value = db.session.query(
        func.sum(ScrapBatch.quantity_scrapped * ScrapBatch.cost_per_unit)
    ).scalar() or 0

    scrap_parts_count = db.session.query(
        func.count(Scrap.id)
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

    # Activity Trends - Last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    activity_data = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        receipts_count = Receipt.query.filter(
            func.date(Receipt.receipt_date) == date.date()
        ).count()

        transfers_count = Transfer.query.filter(
            func.date(Transfer.transfer_date) == date.date()
        ).count()

        scraps_count = Scrap.query.filter(
            func.date(Scrap.scrap_date) == date.date()
        ).count()

        activity_data.append({
            'date': date_str,
            'receipts': receipts_count,
            'transfers': transfers_count,
            'scraps': scraps_count
        })

    # Stock Health Status
    critical_materials = db.session.query(
        Material
    ).outerjoin(
        InventoryLevel, Material.id == InventoryLevel.material_id
    ).filter(
        Material.active == True
    ).group_by(
        Material.id
    ).having(
        func.coalesce(func.sum(InventoryLevel.quantity), 0) == 0
    ).count()

    critical_items = db.session.query(
        Item
    ).outerjoin(
        InventoryLevel, Item.id == InventoryLevel.item_id
    ).filter(
        Item.active == True
    ).group_by(
        Item.id
    ).having(
        func.coalesce(func.sum(InventoryLevel.quantity), 0) == 0
    ).count()

    low_materials = len(low_stock_materials)
    low_items = len(low_stock_items)

    stock_health = {
        'critical': critical_materials + critical_items,
        'low': low_materials + low_items,
        'normal': (total_materials - critical_materials - low_materials) + (total_items - critical_items - low_items)
    }

    return render_template('dashboard/index.html',
                          total_materials=total_materials,
                          total_items=total_items,
                          total_locations=total_locations,
                          total_value=total_value,
                          total_quantity=total_quantity,
                          scrap_value=scrap_value,
                          scrap_parts_count=scrap_parts_count,
                          low_stock_count=low_stock_count,
                          low_stock_materials=low_stock_materials,
                          low_stock_items=low_stock_items,
                          inventory_by_location=inventory_by_location,
                          recent_batches=recent_batches,
                          activity_data=activity_data,
                          stock_health=stock_health)
