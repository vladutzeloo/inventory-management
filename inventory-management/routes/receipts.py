"""
Receipts routes - Incoming inventory with FIFO batch creation
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Receipt, ReceiptItem, Material, Item, Location, Bin
from fifo_utils import process_receipt
from datetime import datetime

bp = Blueprint('receipts', __name__)


def generate_receipt_number():
    """Generate unique receipt number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    last_receipt = Receipt.query.order_by(Receipt.id.desc()).first()
    sequence = (last_receipt.id + 1) if last_receipt else 1
    return f"RCV-{timestamp}-{sequence:04d}"


@bp.route('/')
@login_required
def index():
    """List all receipts"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Receipt.query

    if search:
        query = query.filter(
            (Receipt.receipt_number.ilike(f'%{search}%')) |
            (Receipt.po_number.ilike(f'%{search}%')) |
            (Receipt.supplier_name.ilike(f'%{search}%'))
        )

    pagination = query.order_by(Receipt.receipt_date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    return render_template('receipts/index.html',
                          receipts=pagination.items,
                          pagination=pagination,
                          search=search)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new receipt"""
    if request.method == 'POST':
        try:
            # Create receipt
            receipt = Receipt(
                receipt_number=generate_receipt_number(),
                receipt_date=datetime.strptime(request.form['receipt_date'], '%Y-%m-%d'),
                po_number=request.form.get('po_number', '').strip(),
                supplier_name=request.form.get('supplier_name', '').strip(),
                notes=request.form.get('notes', '').strip(),
                created_by=current_user.username
            )

            db.session.add(receipt)
            db.session.flush()  # Get receipt ID

            # Process receipt items
            item_count = int(request.form.get('item_count', 0))

            for i in range(item_count):
                item_type = request.form.get(f'item_type_{i}')
                item_id = request.form.get(f'item_id_{i}')
                quantity = float(request.form.get(f'quantity_{i}', 0))
                cost_per_unit = float(request.form.get(f'cost_per_unit_{i}', 0))
                supplier_batch = request.form.get(f'supplier_batch_{i}', '').strip()
                location_id = int(request.form.get(f'location_id_{i}'))
                bin_id = request.form.get(f'bin_id_{i}')
                bin_id = int(bin_id) if bin_id and bin_id != '' else None

                if not item_id or quantity <= 0:
                    continue

                # Create receipt item
                receipt_item = ReceiptItem(
                    receipt_id=receipt.id,
                    material_id=int(item_id) if item_type == 'material' else None,
                    item_id=int(item_id) if item_type == 'item' else None,
                    location_id=location_id,
                    bin_id=bin_id,
                    quantity=quantity,
                    cost_per_unit=cost_per_unit,
                    supplier_batch_number=supplier_batch
                )

                db.session.add(receipt_item)
                db.session.flush()

                # Process receipt: create batch, update inventory
                process_receipt(receipt_item, created_by=current_user.username)

            db.session.commit()

            flash(f'Receipt "{receipt.receipt_number}" created successfully!', 'success')
            return redirect(url_for('receipts.view', id=receipt.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating receipt: {str(e)}', 'danger')

    # Load materials, items, and locations for form
    materials = Material.query.filter_by(active=True).order_by(Material.name).all()
    items = Item.query.filter_by(active=True).order_by(Item.name).all()
    locations = Location.query.filter_by(active=True).order_by(Location.code).all()

    return render_template('receipts/new.html',
                          materials=materials,
                          items=items,
                          locations=locations,
                          today=datetime.utcnow().strftime('%Y-%m-%d'))


@bp.route('/<int:id>')
@login_required
def view(id):
    """View receipt details"""
    receipt = Receipt.query.get_or_404(id)
    receipt_items = ReceiptItem.query.filter_by(receipt_id=id).all()

    return render_template('receipts/view.html',
                          receipt=receipt,
                          receipt_items=receipt_items)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete receipt - reverses all inventory transactions"""
    receipt = Receipt.query.get_or_404(id)

    try:
        from models import Batch, InventoryLevel, InventoryTransaction

        # Check if batches from this receipt have been consumed
        for item in receipt.items:
            if item.batch:
                # Check if batch has been consumed
                if item.batch.quantity_available < item.batch.quantity_original:
                    flash(f'Cannot delete receipt - batch {item.batch.batch_number} has been partially consumed. '
                          f'({item.batch.quantity_original - item.batch.quantity_available} units used)', 'danger')
                    return redirect(url_for('receipts.index'))

        # Reverse all transactions for this receipt
        for item in receipt.items:
            # Get the batch associated with this receipt item
            if item.batch:
                batch = item.batch

                # Reverse inventory level
                inv_level = InventoryLevel.query.filter_by(
                    material_id=batch.material_id,
                    item_id=batch.item_id,
                    location_id=batch.location_id,
                    bin_id=batch.bin_id
                ).first()

                if inv_level:
                    inv_level.quantity -= batch.quantity_available
                    if inv_level.quantity <= 0:
                        db.session.delete(inv_level)

                # Mark related inventory transactions as reversed
                InventoryTransaction.query.filter_by(
                    batch_id=batch.id
                ).delete()

                # Delete the batch
                db.session.delete(batch)

            # Delete the receipt item
            db.session.delete(item)

        # Delete the receipt
        db.session.delete(receipt)
        db.session.commit()

        flash(f'Receipt "{receipt.receipt_number}" deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting receipt: {str(e)}', 'danger')

    return redirect(url_for('receipts.index'))
