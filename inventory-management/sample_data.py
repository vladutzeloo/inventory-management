"""
Generate sample data for testing the Inventory Management System
"""
import os
import sys
from datetime import datetime, timedelta
from app import create_app
from models import (db, User, Material, Item, Location, Bin, Receipt, ReceiptItem,
                   Transfer, StockAdjustment, Scrap, Category, Provider, Client)
from fifo_utils import process_receipt, process_transfer, process_scrap, process_adjustment


def create_sample_data():
    """Create comprehensive sample data"""
    app = create_app('development')

    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        # ── Users ────────────────────────────────────────────────────────────
        print("Creating users...")
        admin = User(username='admin', full_name='System Administrator',
                     email='admin@example.com', active=True)
        admin.set_password('admin123')

        manager = User(username='manager', full_name='Warehouse Manager',
                       email='manager@example.com', active=True)
        manager.set_password('manager123')

        operator = User(username='operator', full_name='Warehouse Operator',
                        email='operator@example.com', active=True)
        operator.set_password('operator123')

        db.session.add_all([admin, manager, operator])
        db.session.commit()

        # ── Categories ───────────────────────────────────────────────────────
        print("Creating categories...")
        material_categories = [
            Category(name='Metals',       category_type='material', active=True),
            Category(name='Plastics',     category_type='material', active=True),
            Category(name='Electronics',  category_type='material', active=True),
            Category(name='Chemicals',    category_type='material', active=True),
            Category(name='Fasteners',    category_type='material', active=True),
        ]
        item_categories = [
            Category(name='Finished Goods', category_type='item', active=True),
            Category(name='Assemblies',     category_type='item', active=True),
            Category(name='Components',     category_type='item', active=True),
            Category(name='Spare Parts',    category_type='item', active=True),
        ]
        db.session.add_all(material_categories + item_categories)
        db.session.commit()

        cat_metals      = material_categories[0]
        cat_plastics    = material_categories[1]
        cat_electronics = material_categories[2]
        cat_chemicals   = material_categories[3]
        cat_fasteners   = material_categories[4]

        cat_finished    = item_categories[0]
        cat_assemblies  = item_categories[1]
        cat_components  = item_categories[2]
        cat_spares      = item_categories[3]

        # ── Providers ────────────────────────────────────────────────────────
        print("Creating providers...")
        providers = [
            Provider(name='ABC Steel Co.',        code='ABC-STEEL',  contact_person='John Smith',
                     email='john@abcsteel.com',   phone='+1-555-0101', active=True),
            Provider(name='XYZ Plastics Ltd.',    code='XYZ-PLAST',  contact_person='Maria Garcia',
                     email='maria@xyzplastics.com', phone='+1-555-0102', active=True),
            Provider(name='ElectroParts Inc.',    code='ELECTRO',    contact_person='David Lee',
                     email='david@electroparts.com', phone='+1-555-0103', active=True),
            Provider(name='FastFix Suppliers',    code='FASTFIX',    contact_person='Sarah Brown',
                     email='sarah@fastfix.com',   phone='+1-555-0104', active=True),
        ]
        db.session.add_all(providers)
        db.session.commit()

        prov_steel    = providers[0]
        prov_plastics = providers[1]
        prov_electro  = providers[2]
        prov_fastfix  = providers[3]

        # ── Clients ──────────────────────────────────────────────────────────
        print("Creating clients...")
        clients = [
            Client(name='TechCorp Industries',  code='TECHCORP',  contact_person='Alice Johnson',
                   email='alice@techcorp.com',  phone='+1-555-0201', active=True),
            Client(name='BuildRight LLC',       code='BUILDRIGHT', contact_person='Bob Wilson',
                   email='bob@buildright.com',  phone='+1-555-0202', active=True),
            Client(name='AutoParts Global',     code='AUTOPARTS',  contact_person='Carol Davis',
                   email='carol@autoparts.com', phone='+1-555-0203', active=True),
        ]
        db.session.add_all(clients)
        db.session.commit()

        cli_tech  = clients[0]
        cli_build = clients[1]
        cli_auto  = clients[2]

        # ── Locations ────────────────────────────────────────────────────────
        print("Creating locations...")
        warehouse_a = Location(code='WH-A',   name='Warehouse A - Raw Materials',
                               location_type='warehouse', zone='Zone A', active=True)
        warehouse_b = Location(code='WH-B',   name='Warehouse B - Finished Goods',
                               location_type='warehouse', zone='Zone B', active=True)
        shipping    = Location(code='SHIP-01', name='Shipping & Dispatch',
                               location_type='shipping',  zone='Dock', active=True)
        production  = Location(code='PROD-01', name='Production Floor',
                               location_type='production', zone='Factory', active=True)

        db.session.add_all([warehouse_a, warehouse_b, shipping, production])
        db.session.commit()

        # ── Bins ─────────────────────────────────────────────────────────────
        print("Creating bins...")
        bins_wh_a = [
            Bin(location_id=warehouse_a.id, bin_code='A-01', description='Aisle A, Row 1 – Sheet Metal', active=True),
            Bin(location_id=warehouse_a.id, bin_code='A-02', description='Aisle A, Row 2 – Rods & Tubes', active=True),
            Bin(location_id=warehouse_a.id, bin_code='B-01', description='Aisle B, Row 1 – Plastics',    active=True),
            Bin(location_id=warehouse_a.id, bin_code='B-02', description='Aisle B, Row 2 – Electronics', active=True),
            Bin(location_id=warehouse_a.id, bin_code='C-01', description='Aisle C, Row 1 – Fasteners',   active=True),
        ]
        bins_wh_b = [
            Bin(location_id=warehouse_b.id, bin_code='FG-01', description='Finished Goods – Shelf 1', active=True),
            Bin(location_id=warehouse_b.id, bin_code='FG-02', description='Finished Goods – Shelf 2', active=True),
            Bin(location_id=warehouse_b.id, bin_code='AS-01', description='Assemblies – Shelf 1',     active=True),
        ]
        db.session.add_all(bins_wh_a + bins_wh_b)
        db.session.commit()

        b_a01, b_a02, b_b01, b_b02, b_c01 = bins_wh_a
        b_fg01, b_fg02, b_as01            = bins_wh_b

        # ── Materials ────────────────────────────────────────────────────────
        print("Creating materials...")
        materials = [
            # Metals
            Material(name='Steel Sheet 1mm',     description='Cold-rolled steel sheet, 1 mm thickness',
                     category_id=cat_metals.id,  provider_id=prov_steel.id,
                     unit_of_measure='KG',        reorder_level=500, reorder_quantity=1000,
                     width=1000, length=2000, height=1,  active=True),
            Material(name='Steel Sheet 3mm',     description='Cold-rolled steel sheet, 3 mm thickness',
                     category_id=cat_metals.id,  provider_id=prov_steel.id,
                     unit_of_measure='KG',        reorder_level=400, reorder_quantity=800,
                     width=1000, length=2000, height=3,  active=True),
            Material(name='Aluminum Rod 10mm',   description='Extruded aluminum rod, 10 mm diameter',
                     category_id=cat_metals.id,  provider_id=prov_steel.id,
                     unit_of_measure='M',         reorder_level=200, reorder_quantity=500,
                     diameter=10, length=3000,    active=True),
            Material(name='Stainless Tube 25mm', description='Stainless steel tube, 25 mm OD',
                     category_id=cat_metals.id,  provider_id=prov_steel.id,
                     unit_of_measure='M',         reorder_level=150, reorder_quantity=300,
                     diameter=25, length=6000,    active=True),
            # Plastics
            Material(name='ABS Resin',           description='Acrylonitrile Butadiene Styrene pellets',
                     category_id=cat_plastics.id, provider_id=prov_plastics.id,
                     unit_of_measure='KG',        reorder_level=300, reorder_quantity=600,
                     active=True),
            Material(name='HDPE Sheet 5mm',      description='High-density polyethylene sheet, 5 mm',
                     category_id=cat_plastics.id, provider_id=prov_plastics.id,
                     unit_of_measure='KG',        reorder_level=200, reorder_quantity=400,
                     width=1200, length=2400, height=5, active=True),
            # Electronics
            Material(name='Copper Wire 2.5mm',   description='Single-core copper wire, 2.5 mm²',
                     category_id=cat_electronics.id, provider_id=prov_electro.id,
                     unit_of_measure='M',         reorder_level=1000, reorder_quantity=2000,
                     diameter=2.5,               active=True),
            Material(name='Resistor 10kΩ',       description='Through-hole resistor, 10 kΩ ¼ W',
                     category_id=cat_electronics.id, provider_id=prov_electro.id,
                     unit_of_measure='PCS',       reorder_level=5000, reorder_quantity=10000,
                     active=True),
            # Fasteners
            Material(name='Bolt M8x30',          description='Hex bolt M8 × 30 mm, grade 8.8',
                     category_id=cat_fasteners.id, provider_id=prov_fastfix.id,
                     unit_of_measure='PCS',       reorder_level=2000, reorder_quantity=5000,
                     diameter=8, length=30,       active=True),
            Material(name='Nut M8',              description='Hex nut M8, grade 8',
                     category_id=cat_fasteners.id, provider_id=prov_fastfix.id,
                     unit_of_measure='PCS',       reorder_level=2000, reorder_quantity=5000,
                     diameter=8,                  active=True),
        ]
        db.session.add_all(materials)
        db.session.commit()

        (m_steel1, m_steel3, m_alum, m_tube,
         m_abs, m_hdpe, m_wire, m_resistor,
         m_bolt, m_nut) = materials

        # ── Items ─────────────────────────────────────────────────────────────
        print("Creating items...")
        items = [
            Item(name='Widget A-100',       description='Standard widget model A-100',
                 category_id=cat_finished.id,   client_id=cli_tech.id,
                 unit_of_measure='PCS',          reorder_level=100, reorder_quantity=200,
                 width=80, length=120, height=40, active=True),
            Item(name='Widget B-200',       description='Advanced widget model B-200',
                 category_id=cat_finished.id,   client_id=cli_tech.id,
                 unit_of_measure='PCS',          reorder_level=50, reorder_quantity=100,
                 width=100, length=150, height=60, active=True),
            Item(name='Control Panel X1',   description='Industrial control panel, IP65',
                 category_id=cat_finished.id,   client_id=cli_build.id,
                 unit_of_measure='PCS',          reorder_level=20, reorder_quantity=40,
                 width=300, length=400, height=200, active=True),
            Item(name='Assembly Kit Pro',   description='Complete assembly kit – professional grade',
                 category_id=cat_assemblies.id, client_id=cli_auto.id,
                 unit_of_measure='SET',          reorder_level=30, reorder_quantity=60,
                 width=500, length=600, height=250, active=True),
            Item(name='Housing Cover A',    description='Injection-moulded plastic housing cover',
                 category_id=cat_components.id, client_id=cli_tech.id,
                 unit_of_measure='PCS',          reorder_level=200, reorder_quantity=400,
                 width=90, length=130, height=20, active=True),
            Item(name='Drive Shaft 200mm',  description='Precision drive shaft, 200 mm length',
                 category_id=cat_spares.id,     client_id=cli_auto.id,
                 unit_of_measure='PCS',          reorder_level=50, reorder_quantity=100,
                 diameter=25, length=200,        active=True),
        ]
        db.session.add_all(items)
        db.session.commit()

        (i_widget_a, i_widget_b, i_panel,
         i_kit, i_housing, i_shaft) = items

        # ── Receipts ─────────────────────────────────────────────────────────
        print("Creating receipts (3 months of history)...")

        def make_receipt(num, date, po, supplier, notes, user, receipt_items_data):
            """Helper: create receipt + items and process FIFO batches."""
            rcv = Receipt(receipt_number=num, receipt_date=date, po_number=po,
                          supplier_name=supplier, notes=notes, created_by=user)
            db.session.add(rcv)
            db.session.flush()
            for d in receipt_items_data:
                ri = ReceiptItem(receipt_id=rcv.id, **d)
                db.session.add(ri)
                db.session.flush()
                process_receipt(ri, created_by=user)
            db.session.commit()
            return rcv

        # Receipt 1 – bulk metals, 90 days ago
        make_receipt('RCV-2024-001', datetime.utcnow() - timedelta(days=90),
                     'PO-2024-001', 'ABC Steel Co.',
                     'Initial bulk purchase – sheet metal & rods', 'admin',
                     [
                         dict(material_id=m_steel1.id, location_id=warehouse_a.id, bin_id=b_a01.id,
                              quantity=2000, cost_per_unit=2.50, supplier_batch_number='STEEL-BATCH-001'),
                         dict(material_id=m_steel3.id, location_id=warehouse_a.id, bin_id=b_a01.id,
                              quantity=1500, cost_per_unit=3.20, supplier_batch_number='STEEL-BATCH-002'),
                         dict(material_id=m_alum.id,   location_id=warehouse_a.id, bin_id=b_a02.id,
                              quantity=800,  cost_per_unit=5.50, supplier_batch_number='ALU-BATCH-001'),
                     ])

        # Receipt 2 – plastics, 75 days ago
        make_receipt('RCV-2024-002', datetime.utcnow() - timedelta(days=75),
                     'PO-2024-002', 'XYZ Plastics Ltd.',
                     'Plastic materials – ABS resin and HDPE sheets', 'admin',
                     [
                         dict(material_id=m_abs.id,  location_id=warehouse_a.id, bin_id=b_b01.id,
                              quantity=1200, cost_per_unit=4.00, supplier_batch_number='ABS-BATCH-001'),
                         dict(material_id=m_hdpe.id, location_id=warehouse_a.id, bin_id=b_b01.id,
                              quantity=600,  cost_per_unit=3.50, supplier_batch_number='HDPE-BATCH-001'),
                     ])

        # Receipt 3 – electronics & fasteners, 60 days ago
        make_receipt('RCV-2024-003', datetime.utcnow() - timedelta(days=60),
                     'PO-2024-003', 'Mixed Suppliers',
                     'Electronics and fasteners replenishment', 'manager',
                     [
                         dict(material_id=m_wire.id,     location_id=warehouse_a.id, bin_id=b_b02.id,
                              quantity=5000,  cost_per_unit=1.20, supplier_batch_number='WIRE-BATCH-001'),
                         dict(material_id=m_resistor.id, location_id=warehouse_a.id, bin_id=b_b02.id,
                              quantity=20000, cost_per_unit=0.05, supplier_batch_number='RES-BATCH-001'),
                         dict(material_id=m_bolt.id,     location_id=warehouse_a.id, bin_id=b_c01.id,
                              quantity=10000, cost_per_unit=0.30, supplier_batch_number='BOLT-BATCH-001'),
                         dict(material_id=m_nut.id,      location_id=warehouse_a.id, bin_id=b_c01.id,
                              quantity=10000, cost_per_unit=0.15, supplier_batch_number='NUT-BATCH-001'),
                     ])

        # Receipt 4 – finished goods from external mfr, 45 days ago
        make_receipt('RCV-2024-004', datetime.utcnow() - timedelta(days=45),
                     'PO-2024-004', 'Assembly Factory Co.',
                     'Finished goods – initial stock from external manufacturer', 'manager',
                     [
                         dict(item_id=i_widget_a.id, location_id=warehouse_b.id, bin_id=b_fg01.id,
                              quantity=300, cost_per_unit=25.00, supplier_batch_number='WGT-A-BATCH-001'),
                         dict(item_id=i_widget_b.id, location_id=warehouse_b.id, bin_id=b_fg01.id,
                              quantity=150, cost_per_unit=38.00, supplier_batch_number='WGT-B-BATCH-001'),
                         dict(item_id=i_panel.id,    location_id=warehouse_b.id, bin_id=b_fg02.id,
                              quantity=40,  cost_per_unit=120.00, supplier_batch_number='PNL-BATCH-001'),
                         dict(item_id=i_housing.id,  location_id=warehouse_b.id, bin_id=b_fg02.id,
                              quantity=500, cost_per_unit=8.50,  supplier_batch_number='HSG-BATCH-001'),
                     ])

        # Receipt 5 – second steel order (price increase), 30 days ago
        make_receipt('RCV-2024-005', datetime.utcnow() - timedelta(days=30),
                     'PO-2024-005', 'ABC Steel Co.',
                     'Steel replenishment – new price', 'admin',
                     [
                         dict(material_id=m_steel1.id, location_id=warehouse_a.id, bin_id=b_a01.id,
                              quantity=1000, cost_per_unit=2.75, supplier_batch_number='STEEL-BATCH-003'),
                         dict(material_id=m_tube.id,   location_id=warehouse_a.id, bin_id=b_a02.id,
                              quantity=300,  cost_per_unit=12.00, supplier_batch_number='TUBE-BATCH-001'),
                     ])

        # Receipt 6 – assemblies & spare parts, 15 days ago
        make_receipt('RCV-2024-006', datetime.utcnow() - timedelta(days=15),
                     'PO-2024-006', 'Assembly Factory Co.',
                     'Assemblies and spare parts', 'manager',
                     [
                         dict(item_id=i_kit.id,   location_id=warehouse_b.id, bin_id=b_as01.id,
                              quantity=80,  cost_per_unit=95.00, supplier_batch_number='KIT-BATCH-001'),
                         dict(item_id=i_shaft.id, location_id=warehouse_b.id, bin_id=b_as01.id,
                              quantity=120, cost_per_unit=45.00, supplier_batch_number='SHAFT-BATCH-001'),
                     ])

        # ── Transfers ────────────────────────────────────────────────────────
        print("Creating transfers...")

        def make_transfer(num, date, material_id=None, item_id=None,
                          from_loc=None, from_bin=None, to_loc=None, to_bin=None,
                          qty=0, reason='', notes='', user='manager'):
            t = Transfer(transfer_number=num, transfer_date=date,
                         material_id=material_id, item_id=item_id,
                         from_location_id=from_loc, from_bin_id=from_bin,
                         to_location_id=to_loc,     to_bin_id=to_bin,
                         quantity=qty, reason=reason, notes=notes,
                         status='completed', created_by=user)
            db.session.add(t)
            db.session.flush()
            process_transfer(t, created_by=user)
            db.session.commit()
            return t

        make_transfer('TRF-001', datetime.utcnow() - timedelta(days=80),
                      material_id=m_steel1.id,
                      from_loc=warehouse_a.id, from_bin=b_a01.id,
                      to_loc=production.id,    to_bin=None,
                      qty=400, reason='Production requirement',
                      notes='Job order #JO-2024-001 – steel parts run')

        make_transfer('TRF-002', datetime.utcnow() - timedelta(days=70),
                      item_id=i_widget_a.id,
                      from_loc=warehouse_b.id, from_bin=b_fg01.id,
                      to_loc=shipping.id,      to_bin=None,
                      qty=80, reason='Customer order',
                      notes='TechCorp order #ORD-2024-010')

        make_transfer('TRF-003', datetime.utcnow() - timedelta(days=55),
                      material_id=m_abs.id,
                      from_loc=warehouse_a.id, from_bin=b_b01.id,
                      to_loc=production.id,    to_bin=None,
                      qty=300, reason='Production requirement',
                      notes='Plastic injection run – housing covers')

        make_transfer('TRF-004', datetime.utcnow() - timedelta(days=40),
                      item_id=i_widget_b.id,
                      from_loc=warehouse_b.id, from_bin=b_fg01.id,
                      to_loc=shipping.id,      to_bin=None,
                      qty=50, reason='Customer order',
                      notes='BuildRight order #ORD-2024-025')

        make_transfer('TRF-005', datetime.utcnow() - timedelta(days=25),
                      material_id=m_wire.id,
                      from_loc=warehouse_a.id, from_bin=b_b02.id,
                      to_loc=production.id,    to_bin=None,
                      qty=1500, reason='Production requirement',
                      notes='Wiring harness assembly')

        make_transfer('TRF-006', datetime.utcnow() - timedelta(days=10),
                      item_id=i_panel.id,
                      from_loc=warehouse_b.id, from_bin=b_fg02.id,
                      to_loc=shipping.id,      to_bin=None,
                      qty=15, reason='Customer order',
                      notes='AutoParts Global order #ORD-2024-042')

        # ── Stock Adjustments ─────────────────────────────────────────────────
        print("Creating stock adjustments...")

        def make_adjustment(num, date, material_id=None, item_id=None,
                            loc=None, bin_id=None, qty_change=0,
                            reason='', notes='', user='manager'):
            adj = StockAdjustment(
                adjustment_number=num, adjustment_date=date,
                material_id=material_id, item_id=item_id,
                location_id=loc, bin_id=bin_id,
                quantity_change=qty_change, reason=reason,
                notes=notes, created_by=user)
            db.session.add(adj)
            db.session.flush()
            process_adjustment(adj, created_by=user)
            db.session.commit()
            return adj

        make_adjustment('ADJ-001', datetime.utcnow() - timedelta(days=50),
                        material_id=m_abs.id, loc=warehouse_a.id, bin_id=b_b01.id,
                        qty_change=75, reason='Physical count correction',
                        notes='Cycle count found surplus – added 75 KG')

        make_adjustment('ADJ-002', datetime.utcnow() - timedelta(days=35),
                        item_id=i_housing.id, loc=warehouse_b.id, bin_id=b_fg02.id,
                        qty_change=-12, reason='quality_issue',
                        notes='12 units failed QC inspection – removed from stock')

        make_adjustment('ADJ-003', datetime.utcnow() - timedelta(days=20),
                        material_id=m_bolt.id, loc=warehouse_a.id, bin_id=b_c01.id,
                        qty_change=500, reason='Physical count correction',
                        notes='Miscounted on last cycle count, corrected')

        # ── Scrap Records ─────────────────────────────────────────────────────
        print("Creating scrap records...")

        def make_scrap(num, date, material_id=None, item_id=None,
                       loc=None, bin_id=None, qty=0,
                       reason='', notes='', user='operator'):
            s = Scrap(
                scrap_number=num, scrap_date=date,
                material_id=material_id, item_id=item_id,
                location_id=loc, bin_id=bin_id,
                quantity=qty, reason=reason, notes=notes, created_by=user)
            db.session.add(s)
            db.session.flush()
            process_scrap(s, created_by=user)
            db.session.commit()
            return s

        make_scrap('SCR-001', datetime.utcnow() - timedelta(days=65),
                   material_id=m_steel3.id, loc=warehouse_a.id, bin_id=b_a01.id,
                   qty=50, reason='damaged',
                   notes='Damaged during forklift incident – 50 KG written off')

        make_scrap('SCR-002', datetime.utcnow() - timedelta(days=45),
                   material_id=m_wire.id, loc=warehouse_a.id, bin_id=b_b02.id,
                   qty=200, reason='quality_issue',
                   notes='Batch failed insulation test – scrapped')

        make_scrap('SCR-003', datetime.utcnow() - timedelta(days=28),
                   item_id=i_widget_a.id, loc=warehouse_b.id, bin_id=b_fg01.id,
                   qty=5, reason='damaged',
                   notes='Water damage from roof leak – 5 units written off')

        make_scrap('SCR-004', datetime.utcnow() - timedelta(days=7),
                   material_id=m_hdpe.id, loc=warehouse_a.id, bin_id=b_b01.id,
                   qty=80, reason='expired',
                   notes='Material exceeded shelf life – disposed')

        # ── Summary ──────────────────────────────────────────────────────────
        print("\n" + "=" * 65)
        print("  Demo database created successfully!")
        print("=" * 65)
        print("\n  Login credentials:")
        print("    admin    / admin123")
        print("    manager  / manager123")
        print("    operator / operator123")
        print("\n  Locations:")
        print("    WH-A    – Warehouse A – Raw Materials  (5 bins)")
        print("    WH-B    – Warehouse B – Finished Goods (3 bins)")
        print("    SHIP-01 – Shipping & Dispatch")
        print("    PROD-01 – Production Floor")
        print("\n  Master data:")
        print("    Categories : 9  (5 material / 4 item)")
        print("    Providers  : 4")
        print("    Clients    : 3")
        print("    Materials  : 10  (with dimension data)")
        print("    Items      : 6   (with dimension data)")
        print("\n  Transactions (90-day history):")
        print("    Receipts   : 6")
        print("    Transfers  : 6")
        print("    Adjustments: 3")
        print("    Scrap      : 4")
        print("=" * 65)


if __name__ == '__main__':
    create_sample_data()
