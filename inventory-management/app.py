"""
Inventory Management System - Main Application
Flask application with FIFO batch tracking
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
from models import db, User

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize CSRF Protection
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure data directory exists
    data_dir = os.path.join(app.root_path, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Ensure upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configure logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # File handler
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Inventory Management System startup')

    # Register blueprints
    from routes import auth, dashboard, materials, items, locations, bins
    from routes import receipts, transfers, adjustments, scraps, reports, organization

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(materials.bp, url_prefix='/materials')
    app.register_blueprint(items.bp, url_prefix='/items')
    app.register_blueprint(locations.bp, url_prefix='/locations')
    app.register_blueprint(bins.bp, url_prefix='/bins')
    app.register_blueprint(receipts.bp, url_prefix='/receipts')
    app.register_blueprint(transfers.bp, url_prefix='/transfers')
    app.register_blueprint(adjustments.bp, url_prefix='/adjustments')
    app.register_blueprint(scraps.bp, url_prefix='/scraps')
    app.register_blueprint(reports.bp, url_prefix='/reports')
    app.register_blueprint(organization.bp, url_prefix='/organization')

    # Root route
    @app.route('/')
    def index():
        """Root route - redirect to dashboard or login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Health check endpoint for monitoring
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers and monitoring"""
        from flask import jsonify
        try:
            # Check database connection
            db.session.execute(db.text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'version': app.config['APP_VERSION']
            }), 200
        except Exception as e:
            app.logger.error(f'Health check failed: {str(e)}')
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 503

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # Template context processors
    @app.context_processor
    def inject_app_info():
        """Inject app information into all templates"""
        return {
            'app_name': app.config['APP_NAME'],
            'app_version': app.config['APP_VERSION']
        }

    # Create database tables
    with app.app_context():
        try:
            db.create_all()

            # Create default admin user if no users exist
            if User.query.count() == 0:
                admin = User(
                    username='admin',
                    full_name='System Administrator',
                    email='admin@example.com',
                    active=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Default admin user created: admin / admin123")
        except Exception as e:
            print(f"Error initializing database: {e}")
            print("Please run setup.bat to properly initialize the database")

    return app


if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(host='0.0.0.0', port=5001, debug=True)
