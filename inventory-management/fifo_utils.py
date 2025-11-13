"""
FIFO Batch Management Utilities
Handles batch creation, consumption, and inventory updates
"""
from datetime import datetime
from models import (db, Batch, InventoryLevel, TransferBatch, ScrapBatch,
                   InventoryTransaction)


def generate_batch_number():
    """Generate unique batch number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    # Get last batch to ensure uniqueness
    last_batch = Batch.query.order_by(Batch.id.desc()).first()
    sequence = (last_batch.id + 1) if last_batch else 1
    return f"BATCH-{timestamp}-{sequence:04d}"


def create_batch(material_id=None, item_id=None, location_id=None, bin_id=None,
                quantity=0, cost_per_unit=0, supplier_batch_number=None,
                po_number=None, received_date=None):
    """
    Create a new FIFO batch

    Args:
        material_id: Material ID (mutually exclusive with item_id)
        item_id: Item ID (mutually exclusive with material_id)
        location_id: Location ID
        bin_id: Bin ID (optional)
        quantity: Quantity received
        cost_per_unit: Cost per unit
        supplier_batch_number: Supplier's batch number
        po_number: Purchase order reference
        received_date: Date received (defaults to now)

    Returns:
        Batch object
    """
    if not received_date:
        received_date = datetime.utcnow()

    batch = Batch(
        batch_number=generate_batch_number(),
        material_id=material_id,
        item_id=item_id,
        location_id=location_id,
        bin_id=bin_id,
        quantity_original=quantity,
        quantity_available=quantity,
        received_date=received_date,
        cost_per_unit=cost_per_unit,
        supplier_batch_number=supplier_batch_number,
        po_number=po_number,
        status='active'
    )

    db.session.add(batch)
    return batch


def get_available_batches(material_id=None, item_id=None, location_id=None, bin_id=None):
    """
    Get available batches ordered by FIFO (oldest first)

    Args:
        material_id: Filter by material
        item_id: Filter by item
        location_id: Filter by location
        bin_id: Filter by bin

    Returns:
        List of Batch objects ordered by received_date (oldest first)
    """
    query = Batch.query.filter(
        Batch.status == 'active',
        Batch.quantity_available > 0
    )

    if material_id:
        query = query.filter(Batch.material_id == material_id)
    if item_id:
        query = query.filter(Batch.item_id == item_id)
    if location_id:
        query = query.filter(Batch.location_id == location_id)
    if bin_id:
        query = query.filter(Batch.bin_id == bin_id)

    # FIFO: Order by received_date ascending (oldest first)
    return query.order_by(Batch.received_date.asc(), Batch.id.asc()).all()


def consume_batches_fifo(material_id=None, item_id=None, location_id=None,
                         bin_id=None, quantity_needed=0, consumption_type='transfer',
                         reference_id=None):
    """
    Consume batches using FIFO logic (oldest first)

    Args:
        material_id: Material to consume
        item_id: Item to consume
        location_id: Location to consume from
        bin_id: Bin to consume from
        quantity_needed: Total quantity to consume
        consumption_type: Type of consumption (transfer, scrap)
        reference_id: ID of the consuming document (Transfer, Scrap, etc.)

    Returns:
        List of tuples: [(batch, quantity_consumed, cost_per_unit), ...]

    Raises:
        ValueError: If insufficient quantity available
    """
    batches = get_available_batches(material_id, item_id, location_id, bin_id)

    # Check if we have enough quantity
    total_available = sum(b.quantity_available for b in batches)
    if total_available < quantity_needed:
        raise ValueError(
            f"Insufficient quantity available. Needed: {quantity_needed}, "
            f"Available: {total_available}"
        )

    consumed_batches = []
    remaining_needed = quantity_needed

    for batch in batches:
        if remaining_needed <= 0:
            break

        # Calculate how much to consume from this batch
        quantity_from_batch = min(batch.quantity_available, remaining_needed)

        # Update batch quantity
        batch.quantity_available -= quantity_from_batch

        # Mark batch as depleted if fully consumed
        if batch.quantity_available <= 0:
            batch.status = 'depleted'

        # Record consumption
        consumed_batches.append((batch, quantity_from_batch, batch.cost_per_unit))
        remaining_needed -= quantity_from_batch

    return consumed_batches


def update_inventory_level(material_id=None, item_id=None, location_id=None,
                           bin_id=None, quantity_change=0):
    """
    Update inventory level for a material/item at a location

    Args:
        material_id: Material ID
        item_id: Item ID
        location_id: Location ID
        bin_id: Bin ID
        quantity_change: Change in quantity (positive or negative)
    """
    # Find or create inventory level
    inventory_level = InventoryLevel.query.filter_by(
        material_id=material_id,
        item_id=item_id,
        location_id=location_id,
        bin_id=bin_id
    ).first()

    if not inventory_level:
        inventory_level = InventoryLevel(
            material_id=material_id,
            item_id=item_id,
            location_id=location_id,
            bin_id=bin_id,
            quantity=0
        )
        db.session.add(inventory_level)

    # Update quantity
    inventory_level.quantity += quantity_change
    inventory_level.updated_at = datetime.utcnow()

    return inventory_level


def create_inventory_transaction(transaction_type, material_id=None, item_id=None,
                                location_id=None, bin_id=None, quantity_change=0,
                                reference_type=None, reference_id=None, created_by=None):
    """
    Create an inventory transaction record for audit trail

    Args:
        transaction_type: Type of transaction (receipt, transfer, adjustment, scrap)
        material_id: Material ID
        item_id: Item ID
        location_id: Location ID
        bin_id: Bin ID
        quantity_change: Change in quantity
        reference_type: Type of reference document
        reference_id: ID of reference document
        created_by: Username of creator
    """
    transaction = InventoryTransaction(
        transaction_type=transaction_type,
        transaction_date=datetime.utcnow(),
        material_id=material_id,
        item_id=item_id,
        location_id=location_id,
        bin_id=bin_id,
        quantity_change=quantity_change,
        reference_type=reference_type,
        reference_id=reference_id,
        created_by=created_by
    )

    db.session.add(transaction)
    return transaction


def process_receipt(receipt_item, created_by=None):
    """
    Process a receipt item: create batch, update inventory, create transaction

    Args:
        receipt_item: ReceiptItem object
        created_by: Username

    Returns:
        Batch object
    """
    # Create batch
    batch = create_batch(
        material_id=receipt_item.material_id,
        item_id=receipt_item.item_id,
        location_id=receipt_item.location_id,
        bin_id=receipt_item.bin_id,
        quantity=receipt_item.quantity,
        cost_per_unit=receipt_item.cost_per_unit,
        supplier_batch_number=receipt_item.supplier_batch_number,
        po_number=receipt_item.receipt.po_number if receipt_item.receipt else None
    )

    # Link batch to receipt item
    receipt_item.batch_id = batch.id

    # Update inventory level
    update_inventory_level(
        material_id=receipt_item.material_id,
        item_id=receipt_item.item_id,
        location_id=receipt_item.location_id,
        bin_id=receipt_item.bin_id,
        quantity_change=receipt_item.quantity
    )

    # Create transaction record
    create_inventory_transaction(
        transaction_type='receipt',
        material_id=receipt_item.material_id,
        item_id=receipt_item.item_id,
        location_id=receipt_item.location_id,
        bin_id=receipt_item.bin_id,
        quantity_change=receipt_item.quantity,
        reference_type='receipt',
        reference_id=receipt_item.receipt_id,
        created_by=created_by
    )

    return batch


def process_transfer(transfer, created_by=None):
    """
    Process a transfer: consume FIFO batches from source, create new batches at destination

    Args:
        transfer: Transfer object
        created_by: Username

    Returns:
        List of new batches created at destination
    """
    # Consume batches from source location using FIFO
    consumed_batches = consume_batches_fifo(
        material_id=transfer.material_id,
        item_id=transfer.item_id,
        location_id=transfer.from_location_id,
        bin_id=transfer.from_bin_id,
        quantity_needed=transfer.quantity,
        consumption_type='transfer',
        reference_id=transfer.id
    )

    # Record batch consumption in TransferBatch
    for batch, qty_consumed, cost in consumed_batches:
        transfer_batch = TransferBatch(
            transfer_id=transfer.id,
            batch_id=batch.id,
            quantity_transferred=qty_consumed,
            cost_per_unit=cost
        )
        db.session.add(transfer_batch)

    # Update inventory at source (decrease)
    update_inventory_level(
        material_id=transfer.material_id,
        item_id=transfer.item_id,
        location_id=transfer.from_location_id,
        bin_id=transfer.from_bin_id,
        quantity_change=-transfer.quantity
    )

    # Create transaction for source
    create_inventory_transaction(
        transaction_type='transfer_out',
        material_id=transfer.material_id,
        item_id=transfer.item_id,
        location_id=transfer.from_location_id,
        bin_id=transfer.from_bin_id,
        quantity_change=-transfer.quantity,
        reference_type='transfer',
        reference_id=transfer.id,
        created_by=created_by
    )

    # Create new batches at destination (maintain FIFO tracking)
    new_batches = []
    for batch, qty_consumed, cost in consumed_batches:
        new_batch = create_batch(
            material_id=transfer.material_id,
            item_id=transfer.item_id,
            location_id=transfer.to_location_id,
            bin_id=transfer.to_bin_id,
            quantity=qty_consumed,
            cost_per_unit=cost,
            supplier_batch_number=batch.supplier_batch_number,
            po_number=batch.po_number,
            received_date=batch.received_date  # Maintain original received date for FIFO
        )
        new_batches.append(new_batch)

    # Update inventory at destination (increase)
    update_inventory_level(
        material_id=transfer.material_id,
        item_id=transfer.item_id,
        location_id=transfer.to_location_id,
        bin_id=transfer.to_bin_id,
        quantity_change=transfer.quantity
    )

    # Create transaction for destination
    create_inventory_transaction(
        transaction_type='transfer_in',
        material_id=transfer.material_id,
        item_id=transfer.item_id,
        location_id=transfer.to_location_id,
        bin_id=transfer.to_bin_id,
        quantity_change=transfer.quantity,
        reference_type='transfer',
        reference_id=transfer.id,
        created_by=created_by
    )

    return new_batches


def process_scrap(scrap, created_by=None):
    """
    Process scrap: consume FIFO batches and update inventory

    Args:
        scrap: Scrap object
        created_by: Username
    """
    # Consume batches using FIFO
    consumed_batches = consume_batches_fifo(
        material_id=scrap.material_id,
        item_id=scrap.item_id,
        location_id=scrap.location_id,
        bin_id=scrap.bin_id,
        quantity_needed=scrap.quantity,
        consumption_type='scrap',
        reference_id=scrap.id
    )

    # Record batch consumption in ScrapBatch
    for batch, qty_consumed, cost in consumed_batches:
        scrap_batch = ScrapBatch(
            scrap_id=scrap.id,
            batch_id=batch.id,
            quantity_scrapped=qty_consumed,
            cost_per_unit=cost
        )
        db.session.add(scrap_batch)

    # Update inventory level (decrease)
    update_inventory_level(
        material_id=scrap.material_id,
        item_id=scrap.item_id,
        location_id=scrap.location_id,
        bin_id=scrap.bin_id,
        quantity_change=-scrap.quantity
    )

    # Create transaction record
    create_inventory_transaction(
        transaction_type='scrap',
        material_id=scrap.material_id,
        item_id=scrap.item_id,
        location_id=scrap.location_id,
        bin_id=scrap.bin_id,
        quantity_change=-scrap.quantity,
        reference_type='scrap',
        reference_id=scrap.id,
        created_by=created_by
    )


def process_adjustment(adjustment, created_by=None):
    """
    Process stock adjustment: update inventory level
    Note: Adjustments don't consume batches, they adjust totals

    Args:
        adjustment: StockAdjustment object
        created_by: Username
    """
    # Update inventory level
    update_inventory_level(
        material_id=adjustment.material_id,
        item_id=adjustment.item_id,
        location_id=adjustment.location_id,
        bin_id=adjustment.bin_id,
        quantity_change=adjustment.quantity_change
    )

    # Create transaction record
    create_inventory_transaction(
        transaction_type='adjustment',
        material_id=adjustment.material_id,
        item_id=adjustment.item_id,
        location_id=adjustment.location_id,
        bin_id=adjustment.bin_id,
        quantity_change=adjustment.quantity_change,
        reference_type='adjustment',
        reference_id=adjustment.id,
        created_by=created_by
    )


def get_inventory_valuation(material_id=None, item_id=None, location_id=None):
    """
    Calculate inventory valuation using FIFO costs

    Args:
        material_id: Filter by material
        item_id: Filter by item
        location_id: Filter by location

    Returns:
        dict with total_quantity and total_value
    """
    query = Batch.query.filter(
        Batch.status == 'active',
        Batch.quantity_available > 0
    )

    if material_id:
        query = query.filter(Batch.material_id == material_id)
    if item_id:
        query = query.filter(Batch.item_id == item_id)
    if location_id:
        query = query.filter(Batch.location_id == location_id)

    batches = query.all()

    total_quantity = sum(b.quantity_available for b in batches)
    total_value = sum(b.quantity_available * b.cost_per_unit for b in batches)

    return {
        'total_quantity': total_quantity,
        'total_value': total_value,
        'average_cost': total_value / total_quantity if total_quantity > 0 else 0
    }
