"""
init_db.py
Database initialization script for EstateAI.
Creates tables, creates default demo user, and records model state.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import Config
from database.database import db
from database.models import User, Prediction, ModelTraining
from ml.predict import format_inr


def init_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        print("Creating all database tables...")
        db.create_all()

        # Seed default demo user if not exists
        demo_user = User.query.filter_by(username='demo_analyst').first()
        if not demo_user:
            demo_user = User(
                username='demo_analyst',
                email='analyst@estateai.com',
                role='Senior Real Estate Analyst'
            )
            demo_user.set_password('estateai2026')
            db.session.add(demo_user)
            db.session.commit()
            print(f"Created demo user: {demo_user.username} (password: estateai2026)")

        # Sync ModelTraining table with models/model_metrics.json
        metrics_file = Config.METRICS_FILE
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            
            existing_record = ModelTraining.query.first()
            if not existing_record:
                training_log = ModelTraining(
                    model_name=metrics_data.get('model_name', 'Linear Regression'),
                    r2_score=metrics_data.get('metrics', {}).get('r2_score', 0.90),
                    mae=metrics_data.get('metrics', {}).get('mae', 2700000),
                    rmse=metrics_data.get('metrics', {}).get('rmse', 3800000),
                    dataset_rows=metrics_data.get('total_samples', 650),
                    status=metrics_data.get('status', 'Ready'),
                    details=json.dumps(metrics_data)
                )
                db.session.add(training_log)
                db.session.commit()
                print("Model training record synced to database.")

        # Seed initial sample predictions if none exist
        if Prediction.query.count() == 0:
            sample_predictions = [
                {
                    'area': 1850,
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'floors': 2,
                    'parking': 1,
                    'location': 'Whitefield, Bangalore',
                    'main_road': 'yes',
                    'guestroom': 'no',
                    'basement': 'no',
                    'air_conditioning': 'yes',
                    'preferred_area': 'yes',
                    'furnishing_status': 'Semi-Furnished',
                    'predicted_price': 16170000
                },
                {
                    'area': 2400,
                    'bedrooms': 4,
                    'bathrooms': 3,
                    'floors': 2,
                    'parking': 2,
                    'location': 'Bandra West, Mumbai',
                    'main_road': 'yes',
                    'guestroom': 'yes',
                    'basement': 'no',
                    'air_conditioning': 'yes',
                    'preferred_area': 'yes',
                    'furnishing_status': 'Furnished',
                    'predicted_price': 58500000
                },
                {
                    'area': 1200,
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'floors': 1,
                    'parking': 1,
                    'location': 'Kothrud, Pune',
                    'main_road': 'yes',
                    'guestroom': 'no',
                    'basement': 'no',
                    'air_conditioning': 'no',
                    'preferred_area': 'no',
                    'furnishing_status': 'Semi-Furnished',
                    'predicted_price': 8950000
                }
            ]
            for item in sample_predictions:
                price = item.pop('predicted_price')
                pred = Prediction(
                    user_id=demo_user.id,
                    input_data=json.dumps(item),
                    predicted_price=price,
                    formatted_price=format_inr(price),
                    model_name='Linear Regression',
                    model_r2=0.9053
                )
                db.session.add(pred)
            db.session.commit()
            print("Seeded sample prediction records.")

        print("Database successfully initialized!")

if __name__ == '__main__':
    init_database()
