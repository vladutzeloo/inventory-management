"""
Inventory Management System - Database Models
FIFO Batch Tracking with Multi-Location Support
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Material(db.Model):
    """Raw materials and components master data"""
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # Metals, Plastics, Electronics, etc.
    unit_of_measure = db.Column(db.String(20), nullable=False)  # kg, pcs, m, L, etc.
    reorder_level = db.Column(db.Float, default=0)
    reorder_quantity = db.Column(db.Float, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_levels = db.relationship('InventoryLevel', backref='material', lazy='dynamic',
                                      foreign_keys='InventoryLevel.material_id')
    batches = db.relationship('Batch', backref='material', lazy='dynamic',
                            foreign_keys='Batch.material_id')

    def __repr__(self):
        return f'<Material {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'unit_of_measure': self.unit_of_measure,
            'reorder_level': self.reorder_level,
            'reorder_quantity': self.reorder_quantity,
            'active': self.active
        }


class Item(db.Model):
    """Finished goods and products master data"""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    unit_of_measure = db.Column(db.String(20), nullable=False)
    reorder_level = db.Column(db.Float, default=0)
    reorder_quantity = db.Column(db.Float, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_levels = db.relationship('InventoryLevel', backref='item', lazy='dynamic',
                                      foreign_keys='InventoryLevel.item_id')
    batches = db.relationship('Batch', backref='item', lazy='dynamic',
                            foreign_keys='Batch.item_id')

    def __repr__(self):
        return f'<Item {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'unit_of_measure': self.unit_of_measure,
            'reorder_level': self.reorder_level,
            'reorder_quantity': self.reorder_quantity,
            'active': self.active
        }


class Location(db.Model):
    """Storage locations (Warehouse, Shipping, Production)"""
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    location_type = db.Column(db.String(50), nullable=False)  # warehouse, shipping, production
    zone = db.Column(db.String(100))  # Optional grouping
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bins = db.relationship('Bin', backref='location', lazy='dynamic')
    inventory_levels = db.relationship('InventoryLevel', backref='location', lazy='dynamic')
    batches = db.relationship('Batch', backref='location', lazy='dynamic')

    def __repr__(self):
        return f'<Location {self.code} - {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'location_type': self.location_type,
            'zone': self.zone,
            'active': self.active
        }


class Bin(db.Model):
    """Bin locations within warehouses"""
    __tablename__ = 'bins'

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    bin_code = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: bin_code per location
    __table_args__ = (db.UniqueConstraint('location_id', 'bin_code', name='uq_location_bin'),)

    def __repr__(self):
        return f'<Bin {self.bin_code}>'

    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'bin_code': self.bin_code,
            'description': self.description,
            'active': self.active
        }


class InventoryLevel(db.Model):
    """Current stock levels per location/bin"""
    __tablename__ = 'inventory_levels'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)
    quantity = db.Column(db.Float, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Either material_id or item_id must be set
    __table_args__ = (
        db.CheckConstraint('(material_id IS NOT NULL AND item_id IS NULL) OR (material_id IS NULL AND item_id IS NOT NULL)',
                          name='check_material_or_item'),
        db.UniqueConstraint('material_id', 'item_id', 'location_id', 'bin_id',
                           name='uq_inventory_level'),
    )

    def __repr__(self):
        item_name = self.material.name if self.material else self.item.name
        return f'<InventoryLevel {item_name} @ {self.location.code}: {self.quantity}>'

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'item_id': self.item_id,
            'location_id': self.location_id,
            'bin_id': self.bin_id,
            'quantity': self.quantity,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Batch(db.Model):
    """FIFO batch tracking for materials and items"""
    __tablename__ = 'batches'

    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)

    quantity_original = db.Column(db.Float, nullable=False)
    quantity_available = db.Column(db.Float, nullable=False)

    received_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    cost_per_unit = db.Column(db.Float, nullable=False)
    supplier_batch_number = db.Column(db.String(100))
    po_number = db.Column(db.String(100))  # External ERP reference

    status = db.Column(db.String(20), default='active')  # active, depleted, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Either material_id or item_id must be set
    __table_args__ = (
        db.CheckConstraint('(material_id IS NOT NULL AND item_id IS NULL) OR (material_id IS NULL AND item_id IS NOT NULL)',
                          name='check_batch_material_or_item'),
    )

    # Relationships
    transfer_batches = db.relationship('TransferBatch', backref='batch', lazy='dynamic')
    scrap_batches = db.relationship('ScrapBatch', backref='batch', lazy='dynamic')

    def __repr__(self):
        return f'<Batch {self.batch_number}: {self.quantity_available}/{self.quantity_original}>'

    def to_dict(self):
        return {
            'id': self.id,
            'batch_number': self.batch_number,
            'material_id': self.material_id,
            'item_id': self.item_id,
            'location_id': self.location_id,
            'bin_id': self.bin_id,
            'quantity_original': self.quantity_original,
            'quantity_available': self.quantity_available,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'cost_per_unit': self.cost_per_unit,
            'supplier_batch_number': self.supplier_batch_number,
            'po_number': self.po_number,
            'status': self.status
        }


class Receipt(db.Model):
    """Incoming inventory receipts"""
    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    receipt_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    po_number = db.Column(db.String(100))  # External ERP reference
    supplier_name = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('ReceiptItem', backref='receipt', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Receipt {self.receipt_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'receipt_number': self.receipt_number,
            'receipt_date': self.receipt_date.isoformat() if self.receipt_date else None,
            'po_number': self.po_number,
            'supplier_name': self.supplier_name,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReceiptItem(db.Model):
    """Line items in receipts"""
    __tablename__ = 'receipt_items'

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)

    quantity = db.Column(db.Float, nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=False)
    supplier_batch_number = db.Column(db.String(100))
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=True)  # Created batch

    # Either material_id or item_id must be set
    __table_args__ = (
        db.CheckConstraint('(material_id IS NOT NULL AND item_id IS NULL) OR (material_id IS NULL AND item_id IS NOT NULL)',
                          name='check_receipt_material_or_item'),
    )

    # Relationships
    material = db.relationship('Material', foreign_keys=[material_id])
    item = db.relationship('Item', foreign_keys=[item_id])
    location = db.relationship('Location', foreign_keys=[location_id])
    bin = db.relationship('Bin', foreign_keys=[bin_id])
    batch = db.relationship('Batch', foreign_keys=[batch_id])

    def __repr__(self):
        item_name = self.material.name if self.material else self.item.name
        return f'<ReceiptItem {item_name}: {self.quantity}>'


class Transfer(db.Model):
    """Stock transfers between locations"""
    __tablename__ = 'transfers'

    id = db.Column(db.Integer, primary_key=True)
    transfer_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    transfer_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)

    from_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    from_bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)
    to_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    to_bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)

    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')  # pending, completed

    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Either material_id or item_id must be set
    __table_args__ = (
        db.CheckConstraint('(material_id IS NOT NULL AND item_id IS NULL) OR (material_id IS NULL AND item_id IS NOT NULL)',
                          name='check_transfer_material_or_item'),
    )

    # Relationships
    material = db.relationship('Material', foreign_keys=[material_id])
    item = db.relationship('Item', foreign_keys=[item_id])
    from_location = db.relationship('Location', foreign_keys=[from_location_id])
    from_bin = db.relationship('Bin', foreign_keys=[from_bin_id])
    to_location = db.relationship('Location', foreign_keys=[to_location_id])
    to_bin = db.relationship('Bin', foreign_keys=[to_bin_id])

    transfer_batches = db.relationship('TransferBatch', backref='transfer', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Transfer {self.transfer_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'transfer_number': self.transfer_number,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'material_id': self.material_id,
            'item_id': self.item_id,
            'from_location_id': self.from_location_id,
            'from_bin_id': self.from_bin_id,
            'to_location_id': self.to_location_id,
            'to_bin_id': self.to_bin_id,
            'quantity': self.quantity,
            'reason': self.reason,
            'status': self.status,
            'created_by': self.created_by
        }


class TransferBatch(db.Model):
    """FIFO batch consumption for transfers"""
    __tablename__ = 'transfer_batches'

    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('transfers.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    quantity_transferred = db.Column(db.Float, nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=False)  # From batch at time of transfer

    def __repr__(self):
        return f'<TransferBatch {self.transfer_id}: Batch {self.batch_id}, Qty {self.quantity_transferred}>'


class StockAdjustment(db.Model):
    """Manual stock adjustments"""
    __tablename__ = 'stock_adjustments'

    id = db.Column(db.Integer, primary_key=True)
    adjustment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    adjustment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)

    quantity_change = db.Column(db.Float, nullable=False)  # Positive or negative
    reason = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text)

    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Either material_id or item_id must be set
    __table_args__ = (
        db.CheckConstraint('(material_id IS NOT NULL AND item_id IS NULL) OR (material_id IS NULL AND item_id IS NOT NULL)',
                          name='check_adjustment_material_or_item'),
    )

    # Relationships
    material = db.relationship('Material', foreign_keys=[material_id])
    item = db.relationship('Item', foreign_keys=[item_id])
    location = db.relationship('Location', foreign_keys=[location_id])
    bin = db.relationship('Bin', foreign_keys=[bin_id])

    def __repr__(self):
        return f'<StockAdjustment {self.adjustment_number}: {self.quantity_change}>'


class Scrap(db.Model):
    """Scrap and damage tracking"""
    __tablename__ = 'scraps'

    id = db.Column(db.Integer, primary_key=True)
    scrap_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    scrap_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)

    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(100), nullable=False)  # damaged, expired, quality_issue, etc.
    notes = db.Column(db.Text)

    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Either material_id or item_id must be set
    __table_args__ = (
        db.CheckConstraint('(material_id IS NOT NULL AND item_id IS NULL) OR (material_id IS NULL AND item_id IS NOT NULL)',
                          name='check_scrap_material_or_item'),
    )

    # Relationships
    material = db.relationship('Material', foreign_keys=[material_id])
    item = db.relationship('Item', foreign_keys=[item_id])
    location = db.relationship('Location', foreign_keys=[location_id])
    bin = db.relationship('Bin', foreign_keys=[bin_id])

    scrap_batches = db.relationship('ScrapBatch', backref='scrap', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Scrap {self.scrap_number}>'


class ScrapBatch(db.Model):
    """FIFO batch consumption for scrap"""
    __tablename__ = 'scrap_batches'

    id = db.Column(db.Integer, primary_key=True)
    scrap_id = db.Column(db.Integer, db.ForeignKey('scraps.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    quantity_scrapped = db.Column(db.Float, nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=False)  # From batch at time of scrap

    def __repr__(self):
        return f'<ScrapBatch {self.scrap_id}: Batch {self.batch_id}, Qty {self.quantity_scrapped}>'


class InventoryTransaction(db.Model):
    """Audit trail for all inventory movements"""
    __tablename__ = 'inventory_transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False, index=True)  # receipt, transfer, adjustment, scrap
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)

    quantity_change = db.Column(db.Float, nullable=False)  # Positive or negative
    reference_type = db.Column(db.String(50))  # receipt, transfer, adjustment, scrap
    reference_id = db.Column(db.Integer)  # ID of the source document

    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    material = db.relationship('Material', foreign_keys=[material_id])
    item = db.relationship('Item', foreign_keys=[item_id])
    location = db.relationship('Location', foreign_keys=[location_id])
    bin = db.relationship('Bin', foreign_keys=[bin_id])

    def __repr__(self):
        return f'<InventoryTransaction {self.transaction_type}: {self.quantity_change}>'


class User(UserMixin, db.Model):
    """User management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'active': self.active
        }
