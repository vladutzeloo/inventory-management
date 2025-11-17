"""
Excel Import routes - Bulk stock imports
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Material, Item, Location, Bin, InventoryLevel, Batch, Category, Provider, Client
from datetime import datetime
from werkzeug.utils import secure_filename
import os

bp = Blueprint('imports', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@login_required
def index():
    """Show import page"""
    return render_template('imports/index.html')


@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Process Excel file upload"""
    if 'file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('imports.index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('imports.index'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload .xlsx or .xls file', 'danger')
        return redirect(url_for('imports.index'))

    try:
        # Try importing openpyxl
        try:
            import openpyxl
        except ImportError:
            flash('Excel import requires openpyxl library. Please install it: pip install openpyxl', 'danger')
            return redirect(url_for('imports.index'))

        # Read Excel file
        workbook = openpyxl.load_workbook(file, read_only=True)
        sheet = workbook.active

        results = {
            'created_materials': 0,
            'created_items': 0,
            'created_categories': 0,
            'created_providers': 0,
            'created_clients': 0,
            'created_bins': 0,
            'updated_stock': 0,
            'errors': []
        }

        # Skip header row
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                if not row or all(cell is None for cell in row):
                    continue  # Skip empty rows

                # Expected columns: Type, Name, Category, Provider/Client, Location, Bin, Quantity, UOM, Cost
                item_type = str(row[0]).strip().lower() if row[0] else None
                name = str(row[1]).strip() if row[1] else None
                category_name = str(row[2]).strip() if row[2] else None
                org_name = str(row[3]).strip() if row[3] else None  # Provider for materials, Client for items
                location_code = str(row[4]).strip().upper() if row[4] else None
                bin_code = str(row[5]).strip().upper() if row[5] else None
                quantity = float(row[6]) if row[6] else 0
                uom = str(row[7]).strip() if row[7] else 'PCS'
                cost = float(row[8]) if row[8] else 0

                if not item_type or not name or not location_code:
                    results['errors'].append(f'Row {row_num}: Missing required fields (Type, Name, or Location)')
                    continue

                # Get or create category
                category = None
                if category_name:
                    category = Category.query.filter_by(name=category_name, category_type=item_type).first()
                    if not category:
                        category = Category(name=category_name, category_type=item_type, active=True)
                        db.session.add(category)
                        db.session.flush()
                        results['created_categories'] += 1

                # Get or create location
                location = Location.query.filter_by(code=location_code).first()
                if not location:
                    results['errors'].append(f'Row {row_num}: Location {location_code} not found')
                    continue

                # Get or create bin
                bin_obj = None
                if bin_code:
                    bin_obj = Bin.query.filter_by(location_id=location.id, bin_code=bin_code).first()
                    if not bin_obj:
                        bin_obj = Bin(location_id=location.id, bin_code=bin_code, active=True)
                        db.session.add(bin_obj)
                        db.session.flush()
                        results['created_bins'] += 1

                # Process material or item
                if item_type == 'material':
                    # Get or create provider
                    provider = None
                    if org_name:
                        provider = Provider.query.filter_by(name=org_name).first()
                        if not provider:
                            provider = Provider(
                                name=org_name,
                                code=org_name[:10].upper().replace(' ', '_'),
                                active=True
                            )
                            db.session.add(provider)
                            db.session.flush()
                            results['created_providers'] += 1

                    # Get or create material
                    material = Material.query.filter_by(name=name).first()
                    if not material:
                        material = Material(
                            name=name,
                            unit_of_measure=uom,
                            category_id=category.id if category else None,
                            provider_id=provider.id if provider else None,
                            active=True
                        )
                        db.session.add(material)
                        db.session.flush()
                        results['created_materials'] += 1

                    # Create batch
                    batch = Batch(
                        material_id=material.id,
                        location_id=location.id,
                        bin_id=bin_obj.id if bin_obj else None,
                        quantity_received=quantity,
                        quantity_available=quantity,
                        cost_per_unit=cost,
                        received_date=datetime.utcnow(),
                        status='active'
                    )
                    db.session.add(batch)

                    # Update inventory level
                    inv = InventoryLevel.query.filter_by(
                        material_id=material.id,
                        location_id=location.id,
                        bin_id=bin_obj.id if bin_obj else None
                    ).first()
                    if inv:
                        inv.quantity += quantity
                    else:
                        inv = InventoryLevel(
                            material_id=material.id,
                            location_id=location.id,
                            bin_id=bin_obj.id if bin_obj else None,
                            quantity=quantity
                        )
                        db.session.add(inv)
                    results['updated_stock'] += 1

                elif item_type == 'item':
                    # Get or create client
                    client = None
                    if org_name:
                        client = Client.query.filter_by(name=org_name).first()
                        if not client:
                            client = Client(
                                name=org_name,
                                code=org_name[:10].upper().replace(' ', '_'),
                                active=True
                            )
                            db.session.add(client)
                            db.session.flush()
                            results['created_clients'] += 1

                    # Get or create item
                    item = Item.query.filter_by(name=name).first()
                    if not item:
                        item = Item(
                            name=name,
                            unit_of_measure=uom,
                            category_id=category.id if category else None,
                            client_id=client.id if client else None,
                            active=True
                        )
                        db.session.add(item)
                        db.session.flush()
                        results['created_items'] += 1

                    # Create batch
                    batch = Batch(
                        item_id=item.id,
                        location_id=location.id,
                        bin_id=bin_obj.id if bin_obj else None,
                        quantity_received=quantity,
                        quantity_available=quantity,
                        cost_per_unit=cost,
                        received_date=datetime.utcnow(),
                        status='active'
                    )
                    db.session.add(batch)

                    # Update inventory level
                    inv = InventoryLevel.query.filter_by(
                        item_id=item.id,
                        location_id=location.id,
                        bin_id=bin_obj.id if bin_obj else None
                    ).first()
                    if inv:
                        inv.quantity += quantity
                    else:
                        inv = InventoryLevel(
                            item_id=item.id,
                            location_id=location.id,
                            bin_id=bin_obj.id if bin_obj else None,
                            quantity=quantity
                        )
                        db.session.add(inv)
                    results['updated_stock'] += 1

                else:
                    results['errors'].append(f'Row {row_num}: Invalid type "{item_type}". Must be "material" or "item"')

            except Exception as e:
                results['errors'].append(f'Row {row_num}: {str(e)}')

        # Commit all changes
        db.session.commit()

        # Show results
        flash(f'Import completed! Materials: {results["created_materials"]}, Items: {results["created_items"]}, Stock updated: {results["updated_stock"]}', 'success')
        if results['created_categories']:
            flash(f'Created {results["created_categories"]} new categories', 'info')
        if results['created_providers']:
            flash(f'Created {results["created_providers"]} new providers', 'info')
        if results['created_clients']:
            flash(f'Created {results["created_clients"]} new clients', 'info')
        if results['created_bins']:
            flash(f'Created {results["created_bins"]} new bins', 'info')
        for error in results['errors'][:5]:  # Show first 5 errors
            flash(f'Error: {error}', 'warning')

    except Exception as e:
        db.session.rollback()
        flash(f'Import failed: {str(e)}', 'danger')

    return redirect(url_for('imports.index'))
