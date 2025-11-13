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
    """List all adjustments"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = StockAdjustment.query

    if search:
        query = query.filter(StockAdjustment.adjustment_number.ilike(f'%{search}%'))

    pagination = query.order_by(StockAdjustment.adjustment_date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    return render_template('adjustments/index.html',
                          adjustments=pagination.items,
                          pagination=pagination,
                          search=search)


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
