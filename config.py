"""
config.py
Configuration settings for EstateAI House Price Prediction Platform.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'estateai-super-secret-key-production-grade-2026')
    
    # SQLite Database configuration
    DB_PATH = os.path.join(BASE_DIR, 'estateai.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application Paths
    DATA_PATH = os.path.join(BASE_DIR, 'data', 'house_prices.csv')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    MODEL_FILE = os.path.join(MODELS_DIR, 'house_price_model.pkl')
    PREPROCESSOR_FILE = os.path.join(MODELS_DIR, 'preprocessor.pkl')
    METRICS_FILE = os.path.join(MODELS_DIR, 'model_metrics.json')

    # Security & Sessions
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
