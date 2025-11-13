# Inventory Management System

A comprehensive inventory management system with **FIFO batch tracking**, multi-location support, and full traceability. Built with Flask, SQLAlchemy, and Bootstrap.

## Features

### Core Functionality
- ✅ **FIFO Batch Tracking** - Track every receipt as a batch with received date, cost, and supplier information
- ✅ **Multi-Location Inventory** - Warehouse (with bins), Shipping Area, Production Area
- ✅ **Direct Receipts** - Receive inventory with PO number reference (no PO management in system)
- ✅ **Transfers** - Move stock between locations with automatic FIFO consumption
- ✅ **Stock Adjustments** - Manual adjustments with full audit trail
- ✅ **Scrap Tracking** - Track damaged/defective items with FIFO consumption

### Master Data Management
- **Materials** - Raw materials and components with categories and reorder levels
- **Items** - Finished goods and products (name-based, not SKU)
- **Locations** - Warehouse, Shipping, Production with bin support
- **Excel Import/Export** - Bulk import/export for materials and items

### Reporting & Analytics
- **Stock by Location** - Current inventory levels across all locations
- **Inventory Valuation** - FIFO-based inventory valuation
- **Low Stock Alerts** - Automatic alerts for items below reorder level
- **Transaction History** - Complete audit trail of all inventory movements
- **Excel Export** - Export all reports to Excel

### Dashboard
- Real-time inventory metrics
- Low stock alerts
- Inventory by location
- Recent batch receipts

## Technology Stack

- **Backend**: Flask 3.0.3, SQLAlchemy 2.0.35
- **Database**: SQLite (production-ready for small-medium deployments)
- **Frontend**: Bootstrap 5, jQuery
- **Authentication**: Flask-Login
- **Excel**: openpyxl

## Installation

### Prerequisites
- Python 3.11 or higher
- pip

### Setup

1. **Clone or extract the project**
```bash
cd inventory-management
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize database and create sample data**
```bash
python sample_data.py
```

5. **Run the application**
```bash
python app.py
```

The application will be available at: `http://localhost:5001`

## Default Login

- **Username**: admin
- **Password**: admin123

Alternative user:
- **Username**: manager
- **Password**: manager123

## Quick Start Guide

### 1. Set Up Locations
- Navigate to **Master Data > Locations**
- The system comes with 3 pre-configured locations:
  - **WH-01**: Main Warehouse (with bins A-01, A-02, B-01, B-02)
  - **SHIP-01**: Shipping Area
  - **PROD-01**: Production Area
- Add more locations or bins as needed

### 2. Add Materials and Items
- **Master Data > Materials**: Add raw materials/components
- **Master Data > Items**: Add finished goods/products
- Use **Import** to bulk load from Excel (template provided)
- Set reorder levels for low stock alerts

### 3. Receive Inventory
- **Operations > Receipts > New Receipt**
- Enter PO number (reference to external ERP)
- Add materials/items with:
  - Quantity
  - Cost per unit
  - Supplier batch number (optional)
  - Location and bin
- System automatically creates FIFO batches

### 4. Transfer Inventory
- **Operations > Transfers > New Transfer**
- Select material/item, source location/bin, destination
- System automatically consumes oldest batches (FIFO)
- Common scenarios:
  - Warehouse → Production (for manufacturing)
  - Warehouse → Shipping (for customer orders)
  - Production → Warehouse (finished goods)

### 5. Stock Adjustments
- **Operations > Adjustments > New Adjustment**
- Use for physical count corrections
- Positive or negative adjustments
- Requires reason and notes for audit

### 6. Record Scrap
- **Operations > Scrap > New Scrap**
- Record damaged, expired, or defective items
- System consumes oldest batches (FIFO)
- Select from predefined reasons:
  - damaged, expired, quality_issue, contaminated, obsolete, etc.

### 7. View Reports
- **Reports > Stock by Location**: Current stock levels
- **Reports > Inventory Valuation**: Total inventory value (FIFO costs)
- **Reports > Low Stock Alerts**: Items below reorder level
- **Reports > Transaction History**: Complete audit trail
- All reports can be exported to Excel

## System Architecture

### FIFO Batch Tracking
Every receipt creates a batch with:
- Unique batch number (auto-generated)
- Received date (for FIFO ordering)
- Cost per unit (for accurate valuation)
- Supplier batch number
- PO reference
- Quantity original and available

When consuming inventory (transfers, scrap), the system:
1. Finds all available batches for the material/item at the location
2. Orders by received date (oldest first)
3. Consumes from oldest batches first
4. Maintains batch linkage for full traceability

### Database Schema
- **Material/Item**: Master data (name-based)
- **Location/Bin**: Storage locations
- **Batch**: FIFO batch tracking
- **InventoryLevel**: Current stock per location/bin
- **Receipt/ReceiptItem**: Incoming inventory
- **Transfer**: Stock movements with FIFO
- **StockAdjustment**: Manual adjustments
- **Scrap**: Damage/defect tracking with FIFO
- **InventoryTransaction**: Complete audit trail

## Excel Import/Export

### Materials Import
1. Download template from **Materials > Import > Download Template**
2. Fill in: Name, Description, Category, Unit of Measure, Reorder Level, Reorder Quantity, Active
3. Upload via **Materials > Import**

### Items Import
Same process as materials.

### Reports Export
All reports have an "Export to Excel" button for easy data sharing.

## Integration with External ERP

This system is designed to work alongside your existing ERP:

**What this system handles:**
- Physical inventory tracking across locations
- FIFO batch management
- Stock movements and transfers
- Inventory valuation
- Low stock alerts

**What your ERP handles:**
- Purchase order creation and management
- Sales orders
- Customer/supplier management
- Financial accounting
- Production planning

**Integration points:**
- **PO Number**: Reference only (stored with receipts)
- **Excel Export**: Share inventory data with other systems
- **API**: Can be extended to provide REST API

## Configuration

### Database
Edit `config.py` to change database location or use PostgreSQL/MySQL:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/inventory'
```

### Application Settings
- **SECRET_KEY**: Change in production
- **ITEMS_PER_PAGE**: Pagination (default: 50)
- **MAX_CONTENT_LENGTH**: File upload limit (default: 16MB)

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=sqlite:///data/inventory.db
```

### Security Checklist
- [ ] Change SECRET_KEY
- [ ] Use strong passwords
- [ ] Enable HTTPS
- [ ] Set up regular database backups
- [ ] Configure firewall rules
- [ ] Review user permissions

## Maintenance

### Database Backup
```bash
cp data/inventory.db data/inventory_backup_$(date +%Y%m%d).db
```

### Clear Sample Data
```bash
rm data/inventory.db
python app.py  # Creates fresh database with admin user only
```

### View Database
Use any SQLite viewer:
```bash
sqlite3 data/inventory.db
```

## Troubleshooting

### Database Errors
- Delete `data/inventory.db` and run `sample_data.py` again
- Check file permissions on `data/` directory

### Import Errors
- Ensure Excel file has correct headers
- Check for duplicate names (materials/items must be unique)
- Verify numeric fields (reorder levels, quantities)

### FIFO Errors
- Ensure sufficient quantity available at source location
- Check batch status (active vs depleted)
- Verify location/bin matches

## Customization

### Adding New Location Types
Edit `models.py` and add to `location_type` choices.

### Adding Scrap Reasons
Edit `routes/scraps.py` and add to `scrap_reasons` list.

### Custom Reports
Create new routes in `routes/reports.py` following existing patterns.

## Support & Documentation

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: See code comments for detailed implementation
- **Database Schema**: See `models.py` for complete schema

## License

Proprietary - All rights reserved

## Version

**v1.0.0** - Initial release with full FIFO batch tracking

---

**Built for**: Secondary inventory management module to complement existing ERP systems
**Focus**: FIFO batch tracking, multi-location inventory, full traceability
