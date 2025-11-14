# Production Deployment Guide

## Overview

This guide covers deploying the Inventory Management System to production using Docker (recommended) or direct installation.

## Prerequisites

### For Docker Deployment (Recommended)
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### For Direct Installation
- Linux server (Ubuntu 20.04+ or similar)
- Python 3.9+
- systemd
- 2GB RAM minimum
- 10GB disk space

## Quick Start with Docker

1. **Clone the repository and navigate to the directory**
   ```bash
   cd inventory-management
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   nano .env  # Edit configuration
   ```

   **Important**: Change `SECRET_KEY` to a random string:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Run the deployment script**
   ```bash
   ./deploy.sh
   ```
   Select option 1 (Docker) when prompted.

4. **Access the application**
   - URL: http://localhost:5001
   - Default credentials: `admin` / `admin123`
   - **Change the password immediately after first login!**

## Docker Deployment Details

### Starting the Application
```bash
docker-compose up -d
```

### Stopping the Application
```bash
docker-compose down
```

### Viewing Logs
```bash
docker-compose logs -f
```

### Updating the Application
```bash
git pull
docker-compose build
docker-compose up -d
```

### Backing Up Data
```bash
# Backup database and uploads
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/
```

### Restoring Data
```bash
# Stop the application
docker-compose down

# Restore from backup
tar -xzf backup-YYYYMMDD.tar.gz

# Start the application
docker-compose up -d
```

## Direct Installation (Linux/systemd)

### Installation Steps

1. **Run the deployment script**
   ```bash
   ./deploy.sh
   ```
   Select option 2 (Direct Installation) when prompted.

2. **The script will:**
   - Create a virtual environment
   - Install dependencies
   - Initialize the database
   - Create a systemd service
   - Start the application

### Managing the Service

```bash
# Start
sudo systemctl start inventory-management

# Stop
sudo systemctl stop inventory-management

# Restart
sudo systemctl restart inventory-management

# Check status
sudo systemctl status inventory-management

# View logs
sudo journalctl -u inventory-management -f
```

## Environment Configuration

### Required Variables

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here  # MUST be changed!

# Database
DATABASE_URL=sqlite:///data/inventory.db

# Security
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600
```

### Optional Variables

```env
# Application
APP_NAME=Inventory Management System
APP_VERSION=1.0.0
DEBUG=False

# Session
SESSION_LIFETIME_HOURS=24

# File Uploads
MAX_UPLOAD_SIZE_MB=16

# Pagination
ITEMS_PER_PAGE=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Database Options

### SQLite (Default)
- Best for: Small to medium deployments, single server
- Configuration: `DATABASE_URL=sqlite:///data/inventory.db`

### PostgreSQL (Recommended for Production)
1. **Uncomment the PostgreSQL service in docker-compose.yml**

2. **Update DATABASE_URL**
   ```env
   DATABASE_URL=postgresql://inventory:yourpassword@db:5432/inventory
   DB_PASSWORD=yourpassword
   ```

3. **Restart services**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### MySQL
```env
DATABASE_URL=mysql://username:password@localhost:3306/inventory
```

## Using Nginx Reverse Proxy

For production, use Nginx for SSL/TLS and better performance.

### nginx.conf Example

```nginx
upstream inventory_app {
    server localhost:5001;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    client_max_body_size 16M;

    location / {
        proxy_pass http://inventory_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/inventory-management/inventory-management/static;
        expires 30d;
    }
}
```

## Security Hardening

### Essential Steps

1. **Change Default Password**
   - Login as admin
   - Change password immediately
   - Consider creating a new admin account and disabling the default one

2. **Generate Strong SECRET_KEY**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Enable HTTPS**
   - Use Let's Encrypt for free SSL certificates
   - Configure Nginx with SSL

4. **Firewall Configuration**
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

5. **Regular Updates**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade

   # Update Python dependencies
   pip install --upgrade -r requirements.txt
   ```

### Additional Security Measures

- Run application as non-root user (done automatically in Docker)
- Enable automatic backups
- Monitor logs for suspicious activity
- Keep database backups offsite
- Use strong passwords for database
- Consider implementing IP whitelisting for admin access

## Monitoring and Health Checks

### Health Check Endpoint
```bash
curl http://localhost:5001/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Monitoring Logs

Docker:
```bash
docker-compose logs -f web
```

Systemd:
```bash
sudo journalctl -u inventory-management -f
```

### Disk Space Monitoring
```bash
# Check database size
du -sh data/

# Check logs size
du -sh logs/

# Check uploads size
du -sh uploads/
```

## Backup Strategy

### Automated Backup Script

Create `/usr/local/bin/backup-inventory.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/inventory"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

cd /path/to/inventory-management
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" data/ uploads/

# Keep only last 30 days
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete
```

### Cron Job for Daily Backups

```bash
# Edit crontab
crontab -e

# Add line for 2 AM daily backup
0 2 * * * /usr/local/bin/backup-inventory.sh
```

## Troubleshooting

### Application Won't Start

1. **Check logs**
   ```bash
   docker-compose logs
   # or
   sudo journalctl -u inventory-management
   ```

2. **Verify environment variables**
   ```bash
   cat .env
   ```

3. **Check database connection**
   ```bash
   # For SQLite
   ls -la data/inventory.db

   # For PostgreSQL
   docker-compose exec db psql -U inventory -c '\l'
   ```

### Database Errors

1. **Reset database** (WARNING: This deletes all data!)
   ```bash
   # Backup first!
   cp data/inventory.db data/inventory.db.backup

   # Remove database
   rm data/inventory.db

   # Restart application (will recreate database)
   docker-compose restart
   ```

### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER data/ logs/ uploads/

# Fix permissions
chmod 755 data/ logs/ uploads/
```

### Port Already in Use

```bash
# Find process using port 5001
sudo lsof -i :5001

# Kill process
sudo kill -9 <PID>
```

## Performance Tuning

### Gunicorn Workers

Adjust in `docker-compose.yml` or systemd service:
```
workers = (2 x CPU cores) + 1
```

For 4 cores: `--workers 9`

### Database Optimization

For PostgreSQL, create indexes:
```sql
CREATE INDEX idx_batches_received ON batches(received_date);
CREATE INDEX idx_inventory_levels_location ON inventory_levels(location_id);
CREATE INDEX idx_transactions_date ON inventory_transactions(transaction_date);
```

## Upgrading

### From Previous Version

1. **Backup current data**
   ```bash
   ./backup.sh
   ```

2. **Pull latest code**
   ```bash
   git pull origin main
   ```

3. **Rebuild and restart**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **Verify**
   ```bash
   curl http://localhost:5001/health
   ```

## Support

For issues or questions:
- Check logs first
- Review this documentation
- Contact system administrator

## Warehouse Worker Guide

The system now includes enhanced features for warehouse workers:

### Keyboard Shortcuts
- `N` - New item (context-dependent)
- `R` - New Receipt
- `T` - New Transfer
- `A` - New Adjustment
- `S` - New Scrap
- `D` - Dashboard
- `/` - Search
- `?` - Show shortcuts help

### Barcode Scanner Support
- Simply scan barcodes in forms
- The system automatically detects barcode input
- Works with any USB or Bluetooth barcode scanner

### Touch-Friendly Interface
- Large buttons for easy tapping
- Clear, visible labels
- Confirmation dialogs prevent accidental deletions
- Visual feedback on actions

### Tips for Warehouse Workers
1. Use Enter key to move between fields quickly
2. Scan barcodes directly - no need to click input fields
3. Look for keyboard shortcut hints next to menu items
4. Green borders mean success, red means error
