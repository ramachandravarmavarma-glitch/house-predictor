"""
app.py
Main entry point for EstateAI - Intelligent House Price Prediction Platform.
Flask Application Factory and Server Runner.
"""

import os
import sys

# Ensure root directory is on pythonpath
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, jsonify
from config import Config
from database.database import db
from ml.predict import format_inr, format_inr_words

# Import Blueprints
from routes.main import main_bp
from routes.auth import auth_bp
from routes.prediction import prediction_bp
from routes.dataset import dataset_bp
from routes.analytics import analytics_bp
from routes.history import history_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(history_bp)

    # Register custom template filters
    @app.template_filter('inr')
    def inr_filter(value):
        try:
            return format_inr(value)
        except Exception:
            return str(value)

    @app.template_filter('inr_words')
    def inr_words_filter(value):
        try:
            return format_inr_words(value)
        except Exception:
            return str(value)

    # Global Context Processor
    @app.context_processor
    def inject_global_data():
        from routes.auth import get_current_user
        return {
            'app_name': 'House Predictor',
            'app_tagline': 'Intelligent House Price Prediction Platform',
            'current_user': get_current_user()
        }

    # Friendly Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, message="The requested property intelligence page could not be located."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error_code=500, message="An internal analytics processing error occurred. Our engineers have been alerted."), 500

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting House Predictor Platform on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
