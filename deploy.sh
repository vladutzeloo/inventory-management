#!/bin/bash

##############################################################################
# Production Deployment Script for Inventory Management System
# This script handles deployment using Docker or direct installation
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_info "Creating .env from .env.example..."
    cp .env.example .env

    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-secret-key-here-generate-a-random-string/$SECRET_KEY/" .env

    print_info "Please edit .env file and configure your settings"
    print_info "Then run this script again"
    exit 1
fi

# Load environment variables
source .env

# Deployment type selection
echo "====================================="
echo "Inventory Management System Deployment"
echo "====================================="
echo ""
echo "Select deployment type:"
echo "1) Docker (Recommended)"
echo "2) Direct Installation (Linux/systemd)"
echo "3) Exit"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        print_info "Deploying with Docker..."

        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            print_error "Docker is not installed!"
            print_info "Install Docker: https://docs.docker.com/engine/install/"
            exit 1
        fi

        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            print_error "Docker Compose is not installed!"
            print_info "Install Docker Compose: https://docs.docker.com/compose/install/"
            exit 1
        fi

        # Create required directories
        print_info "Creating required directories..."
        mkdir -p data logs uploads

        # Build and start containers
        print_info "Building Docker image..."
        docker-compose build

        print_info "Starting containers..."
        docker-compose up -d

        # Wait for health check
        print_info "Waiting for application to be ready..."
        sleep 10

        # Check health
        if curl -f http://localhost:5001/health &> /dev/null; then
            print_success "Application is running!"
            print_success "Access the application at: http://localhost:5001"
            print_info "Default credentials: admin / admin123"
            print_info "View logs: docker-compose logs -f"
            print_info "Stop: docker-compose down"
        else
            print_error "Application health check failed"
            print_info "Check logs: docker-compose logs"
            exit 1
        fi
        ;;

    2)
        print_info "Direct installation deployment..."

        # Check Python version
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        REQUIRED_VERSION="3.9"

        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
            print_error "Python 3.9 or higher is required"
            exit 1
        fi

        # Create virtual environment
        print_info "Creating virtual environment..."
        cd inventory-management
        python3 -m venv venv
        source venv/bin/activate

        # Install dependencies
        print_info "Installing dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt

        # Create required directories
        mkdir -p data logs uploads

        # Initialize database
        print_info "Initializing database..."
        python3 -c "from app import create_app; app = create_app('production'); app.app_context().push(); from models import db; db.create_all()"

        # Create systemd service
        print_info "Creating systemd service..."

        SERVICE_FILE="/tmp/inventory-management.service"
        cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Inventory Management System
After=network.target

[Service]
Type=notify
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn --bind 0.0.0.0:5001 --workers 4 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

        print_info "Installing systemd service (requires sudo)..."
        sudo mv "$SERVICE_FILE" /etc/systemd/system/inventory-management.service
        sudo systemctl daemon-reload
        sudo systemctl enable inventory-management
        sudo systemctl start inventory-management

        # Check status
        sleep 3
        if sudo systemctl is-active --quiet inventory-management; then
            print_success "Service is running!"
            print_success "Access the application at: http://localhost:5001"
            print_info "Default credentials: admin / admin123"
            print_info "View logs: sudo journalctl -u inventory-management -f"
            print_info "Stop: sudo systemctl stop inventory-management"
        else
            print_error "Service failed to start"
            print_info "Check logs: sudo journalctl -u inventory-management"
            exit 1
        fi
        ;;

    3)
        print_info "Exiting..."
        exit 0
        ;;

    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

print_success "Deployment complete!"
