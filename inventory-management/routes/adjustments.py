"""
Stock adjustments routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, StockAdjustment, Material, Item, Location, Bin
from fifo_utils import process_adjustment
from datetime import datetime

bp = Blueprint('adjustments', __name__)


def generate_adjustment_number():
    """Generate unique adjustment number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    last_adjustment = StockAdjustment.query.order_by(StockAdjustment.id.desc()).first()
    sequence = (last_adjustment.id + 1) if last_adjustment else 1
    return f"ADJ-{timestamp}-{sequence:04d}"


@bp.route('/')
@login_required
def index():
    """List all adjustments with advanced filtering"""
    page = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from', '', type=str)
    date_to = request.args.get('date_to', '', type=str)
    location_id = request.args.get('location_id', '', type=str)
    material_item_search = request.args.get('material_item_search', '', type=str)
    type_filter = request.args.get('type', '', type=str)
    reason = request.args.get('reason', '', type=str)

    query = StockAdjustment.query

    # Date range filter
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(StockAdjustment.adjustment_date >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Include the entire end date
            from datetime import timedelta
            date_to_obj = date_to_obj + timedelta(days=1)
            query = query.filter(StockAdjustment.adjustment_date < date_to_obj)
        except ValueError:
            pass

    # Location filter
    if location_id:
        query = query.filter(StockAdjustment.location_id == int(location_id))

    # Material/Item filter
    if material_item_search:
        query = query.outerjoin(Material, StockAdjustment.material_id == Material.id).outerjoin(Item, StockAdjustment.item_id == Item.id).filter(
            (Material.name.ilike(f'%{material_item_search}%')) |
            (Item.name.ilike(f'%{material_item_search}%'))
        )

    # Type filter (positive/negative)
    if type_filter:
        if type_filter == 'positive':
            query = query.filter(StockAdjustment.quantity_change > 0)
        elif type_filter == 'negative':
            query = query.filter(StockAdjustment.quantity_change < 0)

    # Reason filter
    if reason:
        query = query.filter(StockAdjustment.reason.ilike(f'%{reason}%'))

    # Apply distinct to avoid duplicates when joining
    query = query.distinct()

    pagination = query.order_by(StockAdjustment.adjustment_date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    # Load locations for filter dropdown
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('adjustments/index.html',
                          adjustments=pagination.items,
                          pagination=pagination,
                          date_from=date_from,
                          date_to=date_to,
                          location_id=location_id,
                          material_item_search=material_item_search,
                          type=type_filter,
                          reason=reason,
                          locations=locations)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new stock adjustment"""
    if request.method == 'POST':
        try:
            item_type = request.form.get('item_type')
            item_id = int(request.form.get('item_id'))
            location_id = int(request.form.get('location_id'))
            bin_id = request.form.get('bin_id')
            bin_id = int(bin_id) if bin_id and bin_id != '' else None
            quantity_change = float(request.form.get('quantity_change'))

            # Create adjustment
            adjustment = StockAdjustment(
                adjustment_number=generate_adjustment_number(),
                adjustment_date=datetime.strptime(request.form['adjustment_date'], '%Y-%m-%d'),
                material_id=item_id if item_type == 'material' else None,
                item_id=item_id if item_type == 'item' else None,
                location_id=location_id,
                bin_id=bin_id,
                quantity_change=quantity_change,
                reason=request.form['reason'].strip(),
                notes=request.form.get('notes', '').strip(),
                created_by=current_user.username
            )

            db.session.add(adjustment)
            db.session.flush()

            # Process adjustment
            process_adjustment(adjustment, created_by=current_user.username)

            db.session.commit()

            flash(f'Adjustment "{adjustment.adjustment_number}" created successfully!', 'success')
            return redirect(url_for('adjustments.view', id=adjustment.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating adjustment: {str(e)}', 'danger')

    # Load materials, items, and locations for form
    materials = Material.query.filter_by(active=True).order_by(Material.name).all()
    items = Item.query.filter_by(active=True).order_by(Item.name).all()
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('adjustments/new.html',
                          materials=materials,
                          items=items,
                          locations=locations,
                          today=datetime.utcnow().strftime('%Y-%m-%d'))


@bp.route('/<int:id>')
@login_required
def view(id):
    """View adjustment details"""
    adjustment = StockAdjustment.query.get_or_404(id)
    return render_template('adjustments/view.html', adjustment=adjustment)
