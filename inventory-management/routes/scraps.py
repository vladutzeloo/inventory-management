"""
Scrap tracking routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Scrap, Material, Item, Location, Bin, InventoryLevel
from fifo_utils import process_scrap
from datetime import datetime

bp = Blueprint('scraps', __name__)


def generate_scrap_number():
    """Generate unique scrap number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    last_scrap = Scrap.query.order_by(Scrap.id.desc()).first()
    sequence = (last_scrap.id + 1) if last_scrap else 1
    return f"SCR-{timestamp}-{sequence:04d}"


@bp.route('/')
@login_required
def index():
    """List all scraps with advanced filtering"""
    page = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from', '', type=str)
    date_to = request.args.get('date_to', '', type=str)
    location_id = request.args.get('location_id', '', type=str)
    material_item_search = request.args.get('material_item_search', '', type=str)
    reason = request.args.get('reason', '', type=str)

    query = Scrap.query

    # Date range filter
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Scrap.scrap_date >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Include the entire end date
            from datetime import timedelta
            date_to_obj = date_to_obj + timedelta(days=1)
            query = query.filter(Scrap.scrap_date < date_to_obj)
        except ValueError:
            pass

    # Location filter
    if location_id:
        query = query.filter(Scrap.location_id == int(location_id))

    # Material/Item filter
    if material_item_search:
        query = query.outerjoin(Material, Scrap.material_id == Material.id).outerjoin(Item, Scrap.item_id == Item.id).filter(
            (Material.name.ilike(f'%{material_item_search}%')) |
            (Item.name.ilike(f'%{material_item_search}%'))
        )

    # Reason filter
    if reason:
        query = query.filter(Scrap.reason == reason)

    # Apply distinct to avoid duplicates when joining
    query = query.distinct()

    pagination = query.order_by(Scrap.scrap_date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    # Load locations for filter dropdown
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('scraps/index.html',
                          scraps=pagination.items,
                          pagination=pagination,
                          date_from=date_from,
                          date_to=date_to,
                          location_id=location_id,
                          material_item_search=material_item_search,
                          reason=reason,
                          locations=locations)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new scrap record"""
    if request.method == 'POST':
        try:
            item_type = request.form.get('item_type')
            item_id = int(request.form.get('item_id'))
            location_id = int(request.form.get('location_id'))
            bin_id = request.form.get('bin_id')
            bin_id = int(bin_id) if bin_id and bin_id != '' else None
            quantity = float(request.form.get('quantity'))

            # Validate quantity available
            inventory_query = InventoryLevel.query.filter_by(
                location_id=location_id,
                bin_id=bin_id
            )

            if item_type == 'material':
                inventory_query = inventory_query.filter_by(material_id=item_id)
            else:
                inventory_query = inventory_query.filter_by(item_id=item_id)

            inventory = inventory_query.first()

            if not inventory or inventory.quantity < quantity:
                available = inventory.quantity if inventory else 0
                flash(f'Insufficient quantity. Available: {available}, Requested: {quantity}', 'danger')
                return redirect(url_for('scraps.new'))

            # Create scrap
            scrap = Scrap(
                scrap_number=generate_scrap_number(),
                scrap_date=datetime.strptime(request.form['scrap_date'], '%Y-%m-%d'),
                material_id=item_id if item_type == 'material' else None,
                item_id=item_id if item_type == 'item' else None,
                location_id=location_id,
                bin_id=bin_id,
                quantity=quantity,
                reason=request.form['reason'],
                notes=request.form.get('notes', '').strip(),
                created_by=current_user.username
            )

            db.session.add(scrap)
            db.session.flush()

            # Process scrap with FIFO
            process_scrap(scrap, created_by=current_user.username)

            db.session.commit()

            flash(f'Scrap record "{scrap.scrap_number}" created successfully!', 'success')
            return redirect(url_for('scraps.view', id=scrap.id))

        except ValueError as e:
            db.session.rollback()
            flash(f'Scrap error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating scrap record: {str(e)}', 'danger')

    # Load materials, items, and locations for form
    materials = Material.query.filter_by(active=True).order_by(Material.name).all()
    items = Item.query.filter_by(active=True).order_by(Item.name).all()
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    # Scrap reasons
    scrap_reasons = [
        'damaged',
        'expired',
        'quality_issue',
        'contaminated',
        'obsolete',
        'production_defect',
        'handling_damage',
        'other'
    ]

    return render_template('scraps/new.html',
                          materials=materials,
                          items=items,
                          locations=locations,
                          scrap_reasons=scrap_reasons,
                          today=datetime.utcnow().strftime('%Y-%m-%d'))


@bp.route('/<int:id>')
@login_required
def view(id):
    """View scrap details"""
    scrap = Scrap.query.get_or_404(id)
    scrap_batches = scrap.scrap_batches.all()

    return render_template('scraps/view.html',
                          scrap=scrap,
                          scrap_batches=scrap_batches)
