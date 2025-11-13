"""
Inventory Management System - Main Application
Flask application with FIFO batch tracking
"""
import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user
from config import config
from models import db, User

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'


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

    # Register blueprints
    from routes import auth, dashboard, materials, items, locations
    from routes import receipts, transfers, adjustments, scraps, reports

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(materials.bp, url_prefix='/materials')
    app.register_blueprint(items.bp, url_prefix='/items')
    app.register_blueprint(locations.bp, url_prefix='/locations')
    app.register_blueprint(receipts.bp, url_prefix='/receipts')
    app.register_blueprint(transfers.bp, url_prefix='/transfers')
    app.register_blueprint(adjustments.bp, url_prefix='/adjustments')
    app.register_blueprint(scraps.bp, url_prefix='/scraps')
    app.register_blueprint(reports.bp, url_prefix='/reports')

    # Root route
    @app.route('/')
    def index():
        """Root route - redirect to dashboard or login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

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

    return app


if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(host='0.0.0.0', port=5001, debug=True)
