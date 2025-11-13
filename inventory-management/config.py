"""
Configuration settings for Inventory Management System
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data', 'inventory.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    # Pagination
    ITEMS_PER_PAGE = 50

    # Application settings
    APP_NAME = 'Inventory Management System'
    APP_VERSION = '1.0.0'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


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
