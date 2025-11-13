"""
Generate sample data for testing the Inventory Management System
"""
import os
import sys
from datetime import datetime, timedelta
from app import create_app
from models import (db, User, Material, Item, Location, Bin, Receipt, ReceiptItem,
                   Transfer, StockAdjustment, Scrap)
from fifo_utils import process_receipt, process_transfer, process_scrap, process_adjustment


def create_sample_data():
    """Create comprehensive sample data"""
    app = create_app('development')

    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        # Create Users
        print("Creating users...")
        admin = User(username='admin', full_name='Administrator', email='admin@example.com', active=True)
        admin.set_password('admin123')
        db.session.add(admin)

        manager = User(username='manager', full_name='Warehouse Manager', email='manager@example.com', active=True)
        manager.set_password('manager123')
        db.session.add(manager)

        db.session.commit()

        # Create Locations
        print("Creating locations...")
        warehouse = Location(code='WH-01', name='Main Warehouse', location_type='warehouse', active=True)
        shipping = Location(code='SHIP-01', name='Shipping Area', location_type='shipping', active=True)
        production = Location(code='PROD-01', name='Production Area', location_type='production', active=True)

        db.session.add_all([warehouse, shipping, production])
        db.session.commit()

        # Create Bins for Warehouse
        print("Creating bins...")
        bins = [
            Bin(location_id=warehouse.id, bin_code='A-01', description='Aisle A, Row 1', active=True),
            Bin(location_id=warehouse.id, bin_code='A-02', description='Aisle A, Row 2', active=True),
            Bin(location_id=warehouse.id, bin_code='B-01', description='Aisle B, Row 1', active=True),
            Bin(location_id=warehouse.id, bin_code='B-02', description='Aisle B, Row 2', active=True),
        ]
        db.session.add_all(bins)
        db.session.commit()

        # Create Materials
        print("Creating materials...")
        materials = [
            Material(name='Steel Sheet 1mm', description='Cold rolled steel sheet, 1mm thickness',
                    category='Metals', unit_of_measure='KG', reorder_level=500, reorder_quantity=1000, active=True),
            Material(name='Steel Sheet 2mm', description='Cold rolled steel sheet, 2mm thickness',
                    category='Metals', unit_of_measure='KG', reorder_level=500, reorder_quantity=1000, active=True),
            Material(name='Aluminum Rod 10mm', description='Aluminum rod, 10mm diameter',
                    category='Metals', unit_of_measure='M', reorder_level=200, reorder_quantity=500, active=True),
            Material(name='Plastic Resin ABS', description='ABS plastic resin',
                    category='Plastics', unit_of_measure='KG', reorder_level=300, reorder_quantity=600, active=True),
            Material(name='Copper Wire 2.5mm', description='Copper electrical wire',
                    category='Electronics', unit_of_measure='M', reorder_level=1000, reorder_quantity=2000, active=True),
            Material(name='Stainless Steel 304', description='Stainless steel grade 304',
                    category='Metals', unit_of_measure='KG', reorder_level=400, reorder_quantity=800, active=True),
        ]
        db.session.add_all(materials)
        db.session.commit()

        # Create Items
        print("Creating items...")
        items = [
            Item(name='Widget A-100', description='Standard widget model A-100',
                category='Finished Goods', unit_of_measure='PCS', reorder_level=100, reorder_quantity=200, active=True),
            Item(name='Widget B-200', description='Advanced widget model B-200',
                category='Finished Goods', unit_of_measure='PCS', reorder_level=50, reorder_quantity=100, active=True),
            Item(name='Assembly Complete X1', description='Complete assembly X1',
                category='Assemblies', unit_of_measure='PCS', reorder_level=25, reorder_quantity=50, active=True),
            Item(name='Component Housing', description='Plastic housing component',
                category='Components', unit_of_measure='PCS', reorder_level=200, reorder_quantity=400, active=True),
        ]
        db.session.add_all(items)
        db.session.commit()

        # Create Receipts
        print("Creating receipts...")
        receipt1 = Receipt(
            receipt_number='RCV-001',
            receipt_date=datetime.utcnow() - timedelta(days=30),
            po_number='PO-2024-001',
            supplier_name='Steel Supplier Inc.',
            notes='Initial stock receipt',
            created_by='admin'
        )
        db.session.add(receipt1)
        db.session.flush()

        # Receipt items for materials
        receipt_items = [
            ReceiptItem(receipt_id=receipt1.id, material_id=materials[0].id, location_id=warehouse.id,
                       bin_id=bins[0].id, quantity=1000, cost_per_unit=2.5, supplier_batch_number='STEEL-2024-001'),
            ReceiptItem(receipt_id=receipt1.id, material_id=materials[1].id, location_id=warehouse.id,
                       bin_id=bins[0].id, quantity=800, cost_per_unit=3.0, supplier_batch_number='STEEL-2024-002'),
            ReceiptItem(receipt_id=receipt1.id, material_id=materials[2].id, location_id=warehouse.id,
                       bin_id=bins[1].id, quantity=500, cost_per_unit=5.5, supplier_batch_number='ALU-2024-001'),
        ]

        for ri in receipt_items:
            db.session.add(ri)
            db.session.flush()
            process_receipt(ri, created_by='admin')

        # Second receipt
        receipt2 = Receipt(
            receipt_number='RCV-002',
            receipt_date=datetime.utcnow() - timedelta(days=20),
            po_number='PO-2024-002',
            supplier_name='Plastics World Ltd.',
            notes='Plastic materials',
            created_by='admin'
        )
        db.session.add(receipt2)
        db.session.flush()

        receipt_items2 = [
            ReceiptItem(receipt_id=receipt2.id, material_id=materials[3].id, location_id=warehouse.id,
                       bin_id=bins[2].id, quantity=600, cost_per_unit=4.0, supplier_batch_number='PLASTIC-2024-001'),
            ReceiptItem(receipt_id=receipt2.id, material_id=materials[4].id, location_id=warehouse.id,
                       bin_id=bins[2].id, quantity=2500, cost_per_unit=1.2, supplier_batch_number='WIRE-2024-001'),
        ]

        for ri in receipt_items2:
            db.session.add(ri)
            db.session.flush()
            process_receipt(ri, created_by='admin')

        # Third receipt - finished goods
        receipt3 = Receipt(
            receipt_number='RCV-003',
            receipt_date=datetime.utcnow() - timedelta(days=15),
            po_number='PO-2024-003',
            supplier_name='Assembly Factory Co.',
            notes='Finished goods from external manufacturer',
            created_by='manager'
        )
        db.session.add(receipt3)
        db.session.flush()

        receipt_items3 = [
            ReceiptItem(receipt_id=receipt3.id, item_id=items[0].id, location_id=warehouse.id,
                       bin_id=bins[3].id, quantity=150, cost_per_unit=25.0, supplier_batch_number='WIDGET-A-001'),
            ReceiptItem(receipt_id=receipt3.id, item_id=items[1].id, location_id=warehouse.id,
                       bin_id=bins[3].id, quantity=80, cost_per_unit=35.0, supplier_batch_number='WIDGET-B-001'),
        ]

        for ri in receipt_items3:
            db.session.add(ri)
            db.session.flush()
            process_receipt(ri, created_by='manager')

        db.session.commit()

        # Create Transfers
        print("Creating transfers...")
        transfer1 = Transfer(
            transfer_number='TRF-001',
            transfer_date=datetime.utcnow() - timedelta(days=10),
            material_id=materials[0].id,
            from_location_id=warehouse.id,
            from_bin_id=bins[0].id,
            to_location_id=production.id,
            to_bin_id=None,
            quantity=200,
            reason='Production requirement',
            notes='Transfer to production for job #123',
            status='completed',
            created_by='manager'
        )
        db.session.add(transfer1)
        db.session.flush()
        process_transfer(transfer1, created_by='manager')

        transfer2 = Transfer(
            transfer_number='TRF-002',
            transfer_date=datetime.utcnow() - timedelta(days=8),
            item_id=items[0].id,
            from_location_id=warehouse.id,
            from_bin_id=bins[3].id,
            to_location_id=shipping.id,
            to_bin_id=None,
            quantity=50,
            reason='Customer order',
            notes='Order #456',
            status='completed',
            created_by='manager'
        )
        db.session.add(transfer2)
        db.session.flush()
        process_transfer(transfer2, created_by='manager')

        db.session.commit()

        # Create Stock Adjustments
        print("Creating stock adjustments...")
        adjustment1 = StockAdjustment(
            adjustment_number='ADJ-001',
            adjustment_date=datetime.utcnow() - timedelta(days=5),
            material_id=materials[3].id,
            location_id=warehouse.id,
            bin_id=bins[2].id,
            quantity_change=50,
            reason='Physical count correction',
            notes='Found additional inventory during cycle count',
            created_by='manager'
        )
        db.session.add(adjustment1)
        db.session.flush()
        process_adjustment(adjustment1, created_by='manager')

        db.session.commit()

        # Create Scrap Records
        print("Creating scrap records...")
        scrap1 = Scrap(
            scrap_number='SCR-001',
            scrap_date=datetime.utcnow() - timedelta(days=3),
            material_id=materials[1].id,
            location_id=warehouse.id,
            bin_id=bins[0].id,
            quantity=25,
            reason='damaged',
            notes='Damaged during handling',
            created_by='admin'
        )
        db.session.add(scrap1)
        db.session.flush()
        process_scrap(scrap1, created_by='admin')

        db.session.commit()

        print("\n" + "="*60)
        print("Sample data created successfully!")
        print("="*60)
        print("\nLogin credentials:")
        print("  Admin: admin / admin123")
        print("  Manager: manager / manager123")
        print("\nLocations created:")
        print("  - WH-01: Main Warehouse (with 4 bins)")
        print("  - SHIP-01: Shipping Area")
        print("  - PROD-01: Production Area")
        print("\nMaterials created: 6")
        print("Items created: 4")
        print("Receipts created: 3")
        print("Transfers created: 2")
        print("Adjustments created: 1")
        print("Scrap records created: 1")
        print("\nDatabase: inventory-management/data/inventory.db")
        print("="*60)


if __name__ == '__main__':
    create_sample_data()
