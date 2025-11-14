# Inventory Management System

A professional, production-ready inventory management system with FIFO batch tracking, multi-location support, and warehouse-optimized UX.

## Features

### Core Functionality
- **FIFO Batch Tracking** - Automatic first-in-first-out inventory management
- **Multi-Location Support** - Warehouse, shipping, and production locations with bin-level tracking
- **Materials & Items Management** - Comprehensive master data management
- **Operations**
  - Receipts with multi-line support
  - Location transfers with automatic FIFO consumption
  - Stock adjustments with full audit trail
  - Scrap tracking
- **Comprehensive Reporting**
  - Stock by location
  - Inventory valuation (FIFO-based)
  - Low stock alerts
  - Transaction history
  - Excel export for all reports

### Warehouse Worker Optimizations ✨ NEW
- **Large Touch-Friendly Buttons** - Easy to use on tablets and touch screens
- **Barcode Scanner Support** - Automatic detection and processing of barcode input
- **Keyboard Shortcuts** - Quick navigation without mouse
  - `N` - New item, `R` - Receipt, `T` - Transfer, `A` - Adjustment, `S` - Scrap
  - `/` - Search, `?` - Show shortcuts help
- **Visual Feedback** - Clear success/error animations
- **Confirmation Dialogs** - Prevent accidental deletions
- **Auto-focus** - Automatically focus first input field
- **Enter Key Navigation** - Quick form completion

### Security & Production Features ✨ NEW
- **CSRF Protection** - All forms protected against cross-site request forgery
- **Environment-based Configuration** - Secure secret management with .env files
- **Comprehensive Logging** - Rotating log files for debugging and audit
- **Health Check Endpoint** - `/health` for monitoring and load balancers
- **Docker Support** - Production-ready containerization
- **Automatic Backups** - Built-in backup strategies

### Technical Improvements ✨ NEW
- **Numeric Precision** - Fixed float precision issues for monetary values
- **Receipt Deletion** - Properly implemented transaction reversal
- **User Authentication** - Secure password hashing with Flask-Login
- **Responsive Design** - Works on desktop, tablet, and mobile

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and navigate
cd inventory-management

# Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY

# Deploy
./deploy.sh
# Select option 1 (Docker)
```

Access at: http://localhost:5001

### Option 2: Manual Installation

```bash
cd inventory-management/inventory-management

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example ../.env
# Edit ../.env and set SECRET_KEY

# Run
python app.py
```

Access at: http://localhost:5001

### Default Credentials
- Username: `admin`
- Password: `admin123`

**⚠️ Change the password immediately after first login!**

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions including:
- Docker deployment
- Nginx reverse proxy setup
- SSL/TLS configuration
- Database options (SQLite, PostgreSQL, MySQL)
- Security hardening
- Backup strategies
- Monitoring and health checks

## Project Structure

```
inventory-management/
├── inventory-management/           # Main application directory
│   ├── app.py                     # Application entry point
│   ├── config.py                  # Configuration
│   ├── models.py                  # Database models
│   ├── fifo_utils.py             # FIFO batch management
│   ├── routes/                    # Blueprint routes
│   │   ├── auth.py               # Authentication
│   │   ├── dashboard.py          # Dashboard
│   │   ├── materials.py          # Materials management
│   │   ├── items.py              # Items management
│   │   ├── locations.py          # Locations management
│   │   ├── receipts.py           # Receipt processing
│   │   ├── transfers.py          # Transfer operations
│   │   ├── adjustments.py        # Stock adjustments
│   │   ├── scraps.py             # Scrap tracking
│   │   └── reports.py            # Reporting
│   ├── templates/                 # HTML templates
│   ├── static/                    # Static assets
│   │   ├── css/
│   │   │   └── style.css         # Enhanced warehouse-friendly CSS
│   │   └── js/
│   │       └── warehouse.js      # Warehouse UX enhancements
│   └── requirements.txt           # Python dependencies
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose configuration
├── deploy.sh                      # Deployment script
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── DEPLOYMENT.md                  # Production deployment guide
└── README.md                      # This file
```

## Technology Stack

- **Backend**: Flask 3.0.3, SQLAlchemy 2.0.35
- **Database**: SQLite (default), PostgreSQL, MySQL supported
- **Frontend**: Bootstrap 5, jQuery
- **Authentication**: Flask-Login with password hashing
- **Security**: Flask-WTF CSRF protection
- **Production Server**: Gunicorn
- **Containerization**: Docker & Docker Compose

## Features in Detail

### FIFO Batch Tracking
- Automatic batch creation on receipts
- Oldest batches consumed first
- Complete batch traceability
- Cost tracking per batch

### Multi-Location Inventory
- Warehouse locations
- Shipping locations
- Production locations
- Bin-level tracking within locations

### Audit Trail
- Every transaction logged
- User tracking for all operations
- Transaction history reports
- Batch consumption tracking

### Excel Integration
- Import materials from Excel
- Export all reports to Excel
- Material templates for easy import

### Warehouse-Optimized UX
- Designed for workers who are not tech-savvy
- Large, touch-friendly interface
- Barcode scanner integration
- Keyboard shortcuts for power users
- Clear visual feedback
- Automatic field navigation

## Screenshots

*(Add screenshots here)*

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- `SECRET_KEY` - Flask secret key (REQUIRED)
- `DATABASE_URL` - Database connection string
- `FLASK_ENV` - development/production
- `WTF_CSRF_ENABLED` - Enable CSRF protection
- `LOG_LEVEL` - Logging level
- And more...

### Database Migration

To change database type:

1. Update `DATABASE_URL` in `.env`
2. Restart the application
3. Database will be created automatically

## Development

### Running Tests
```bash
# (Tests to be implemented)
pytest
```

### Database Schema Changes
```bash
# After modifying models.py
python
>>> from app import create_app
>>> app = create_app()
>>> app.app_context().push()
>>> from models import db
>>> db.create_all()
```

### Adding New Features

1. Create blueprint in `routes/`
2. Add templates in `templates/`
3. Register blueprint in `app.py`
4. Update navigation in `templates/base.html`

## Backup and Recovery

### Backup
```bash
# Manual backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/

# Automated daily backup (see DEPLOYMENT.md)
```

### Recovery
```bash
tar -xzf backup-YYYYMMDD.tar.gz
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find and kill process on port 5001
lsof -i :5001
kill -9 <PID>
```

**Database locked:**
```bash
# Ensure only one instance is running
# SQLite doesn't support multiple writers
```

**Permission errors:**
```bash
chmod 755 data/ logs/ uploads/
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting tips.

## Security Notes

- Always change default admin password
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Keep database backups secure
- Regular security updates
- Monitor logs for suspicious activity

## License

*(Add your license here)*

## Support

For issues or questions:
- Check the logs: `logs/app.log`
- Review [DEPLOYMENT.md](DEPLOYMENT.md)
- Contact system administrator

## Recent Updates

### Version 1.1.0 (Latest)

**Bug Fixes:**
- ✅ Fixed receipt deletion functionality with proper transaction reversal
- ✅ Fixed float precision issues for monetary values (now using Numeric)
- ✅ Added comprehensive logging for debugging

**New Features:**
- ✅ Warehouse worker optimizations (large buttons, barcode support, keyboard shortcuts)
- ✅ CSRF protection for all forms
- ✅ Health check endpoint for monitoring
- ✅ Docker containerization support
- ✅ Environment-based configuration
- ✅ Automated deployment scripts

**Security Improvements:**
- ✅ Secret key management via environment variables
- ✅ CSRF protection enabled
- ✅ Secure password hashing
- ✅ Non-root Docker container

**UX Improvements:**
- ✅ Touch-friendly interface for warehouse workers
- ✅ Barcode scanner automatic detection
- ✅ Keyboard shortcuts for quick navigation
- ✅ Confirmation dialogs for destructive actions
- ✅ Visual feedback animations
- ✅ Auto-focus on form fields

## Acknowledgments

Built with Flask, Bootstrap, and love for efficient warehouse operations.
