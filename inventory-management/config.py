"""
Configuration settings for Inventory Management System
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        import warnings
        warnings.warn(
            "SECRET_KEY environment variable is not set! "
            "Using a temporary key. Set SECRET_KEY in your .env file for production.",
            UserWarning
        )
        SECRET_KEY = 'temporary-secret-key-please-change-in-production'

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data/inventory.db')
    # Handle relative SQLite paths
    if DATABASE_URL.startswith('sqlite:///') and not DATABASE_URL.startswith('sqlite:////'):
        db_path = DATABASE_URL.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            DATABASE_URL = 'sqlite:///' + os.path.join(basedir, db_path)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Session
    SESSION_LIFETIME_HOURS = int(os.environ.get('SESSION_LIFETIME_HOURS', '24'))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=SESSION_LIFETIME_HOURS)

    # File uploads
    MAX_UPLOAD_SIZE_MB = int(os.environ.get('MAX_UPLOAD_SIZE_MB', '16'))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '50'))

    # Application settings
    APP_NAME = os.environ.get('APP_NAME', 'Inventory Management System')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')

    # CSRF Protection
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', '3600'))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # Allow dev without SECRET_KEY enforcement
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-for-development-only')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # Production MUST have SECRET_KEY set
    def __init__(self):
        if not os.environ.get('SECRET_KEY'):
            raise ValueError(
                "SECRET_KEY environment variable is REQUIRED for production! "
                "Please set it in your .env file to a secure random value."
            )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
