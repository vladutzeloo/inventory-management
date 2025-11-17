"""
Transfer routes - Stock movements between locations with FIFO
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Transfer, Material, Item, Location, Bin, InventoryLevel
from fifo_utils import process_transfer
from datetime import datetime

bp = Blueprint('transfers', __name__)


def generate_transfer_number():
    """Generate unique transfer number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    last_transfer = Transfer.query.order_by(Transfer.id.desc()).first()
    sequence = (last_transfer.id + 1) if last_transfer else 1
    return f"TRF-{timestamp}-{sequence:04d}"


@bp.route('/')
@login_required
def index():
    """List all transfers with advanced filtering"""
    page = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from', '', type=str)
    date_to = request.args.get('date_to', '', type=str)
    from_location_id = request.args.get('from_location_id', '', type=str)
    to_location_id = request.args.get('to_location_id', '', type=str)
    material_item_search = request.args.get('material_item_search', '', type=str)
    status = request.args.get('status', '', type=str)
    reason = request.args.get('reason', '', type=str)

    query = Transfer.query

    # Date range filter
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Transfer.transfer_date >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Include the entire end date
            from datetime import timedelta
            date_to_obj = date_to_obj + timedelta(days=1)
            query = query.filter(Transfer.transfer_date < date_to_obj)
        except ValueError:
            pass

    # From Location filter
    if from_location_id:
        query = query.filter(Transfer.from_location_id == int(from_location_id))

    # To Location filter
    if to_location_id:
        query = query.filter(Transfer.to_location_id == int(to_location_id))

    # Material/Item filter
    if material_item_search:
        query = query.outerjoin(Material, Transfer.material_id == Material.id).outerjoin(Item, Transfer.item_id == Item.id).filter(
            (Material.name.ilike(f'%{material_item_search}%')) |
            (Item.name.ilike(f'%{material_item_search}%'))
        )

    # Status filter
    if status:
        query = query.filter(Transfer.status == status)

    # Reason filter
    if reason:
        query = query.filter(Transfer.reason.ilike(f'%{reason}%'))

    # Apply distinct to avoid duplicates when joining
    query = query.distinct()

    pagination = query.order_by(Transfer.transfer_date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    # Load locations for filter dropdown
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('transfers/index.html',
                          transfers=pagination.items,
                          pagination=pagination,
                          date_from=date_from,
                          date_to=date_to,
                          from_location_id=from_location_id,
                          to_location_id=to_location_id,
                          material_item_search=material_item_search,
                          status=status,
                          reason=reason,
                          locations=locations)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new transfer"""
    if request.method == 'POST':
        try:
            item_type = request.form.get('item_type')
            item_id = int(request.form.get('item_id'))
            from_location_id = int(request.form.get('from_location_id'))
            to_location_id = int(request.form.get('to_location_id'))
            quantity = float(request.form.get('quantity'))

            # Validate quantity available at location level (sum of all bins)
            inventory_query = InventoryLevel.query.filter_by(
                location_id=from_location_id
            )

            if item_type == 'material':
                inventory_query = inventory_query.filter_by(material_id=item_id)
            else:
                inventory_query = inventory_query.filter_by(item_id=item_id)

            # Sum up quantities from all bins at this location
            total_available = sum(inv.quantity for inv in inventory_query.all())

            if total_available < quantity:
                flash(f'Insufficient quantity. Available: {total_available}, Requested: {quantity}', 'danger')
                return redirect(url_for('transfers.new'))

            # Create transfer without bin information
            transfer = Transfer(
                transfer_number=generate_transfer_number(),
                transfer_date=datetime.strptime(request.form['transfer_date'], '%Y-%m-%d'),
                material_id=item_id if item_type == 'material' else None,
                item_id=item_id if item_type == 'item' else None,
                from_location_id=from_location_id,
                from_bin_id=None,  # No bin tracking in transfers
                to_location_id=to_location_id,
                to_bin_id=None,  # No bin tracking in transfers
                quantity=quantity,
                reason=request.form.get('reason', '').strip(),
                internal_order_number=request.form.get('internal_order_number', '').strip(),
                notes=request.form.get('notes', '').strip(),
                status='completed',
                created_by=current_user.username
            )

            db.session.add(transfer)
            db.session.flush()

            # Process transfer with FIFO
            process_transfer(transfer, created_by=current_user.username)

            db.session.commit()

            flash(f'Transfer "{transfer.transfer_number}" created successfully!', 'success')
            return redirect(url_for('transfers.view', id=transfer.id))

        except ValueError as e:
            db.session.rollback()
            flash(f'Transfer error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating transfer: {str(e)}', 'danger')

    # Load materials, items, and locations for form
    materials = Material.query.filter_by(active=True).order_by(Material.name).all()
    items = Item.query.filter_by(active=True).order_by(Item.name).all()
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('transfers/new.html',
                          materials=materials,
                          items=items,
                          locations=locations,
                          today=datetime.utcnow().strftime('%Y-%m-%d'))


@bp.route('/<int:id>')
@login_required
def view(id):
    """View transfer details"""
    transfer = Transfer.query.get_or_404(id)
    transfer_batches = transfer.transfer_batches.all()

    return render_template('transfers/view.html',
                          transfer=transfer,
                          transfer_batches=transfer_batches)
