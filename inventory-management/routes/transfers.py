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
    """List all transfers"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Transfer.query

    if search:
        query = query.filter(Transfer.transfer_number.ilike(f'%{search}%'))

    pagination = query.order_by(Transfer.transfer_date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    return render_template('transfers/index.html',
                          transfers=pagination.items,
                          pagination=pagination,
                          search=search)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new transfer"""
    if request.method == 'POST':
        try:
            item_type = request.form.get('item_type')
            item_id = int(request.form.get('item_id'))
            from_location_id = int(request.form.get('from_location_id'))
            from_bin_id = request.form.get('from_bin_id')
            from_bin_id = int(from_bin_id) if from_bin_id and from_bin_id != '' else None
            to_location_id = int(request.form.get('to_location_id'))
            to_bin_id = request.form.get('to_bin_id')
            to_bin_id = int(to_bin_id) if to_bin_id and to_bin_id != '' else None
            quantity = float(request.form.get('quantity'))

            # Validate quantity available
            inventory_query = InventoryLevel.query.filter_by(
                location_id=from_location_id,
                bin_id=from_bin_id
            )

            if item_type == 'material':
                inventory_query = inventory_query.filter_by(material_id=item_id)
            else:
                inventory_query = inventory_query.filter_by(item_id=item_id)

            inventory = inventory_query.first()

            if not inventory or inventory.quantity < quantity:
                available = inventory.quantity if inventory else 0
                flash(f'Insufficient quantity. Available: {available}, Requested: {quantity}', 'danger')
                return redirect(url_for('transfers.new'))

            # Create transfer
            transfer = Transfer(
                transfer_number=generate_transfer_number(),
                transfer_date=datetime.strptime(request.form['transfer_date'], '%Y-%m-%d'),
                material_id=item_id if item_type == 'material' else None,
                item_id=item_id if item_type == 'item' else None,
                from_location_id=from_location_id,
                from_bin_id=from_bin_id,
                to_location_id=to_location_id,
                to_bin_id=to_bin_id,
                quantity=quantity,
                reason=request.form.get('reason', '').strip(),
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
