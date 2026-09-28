"""
database/models.py
ORM Models for EstateAI: User, Prediction, ModelTraining.
"""

from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='analyst')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'predictions_count': len(self.predictions)
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    input_data = db.Column(db.Text, nullable=False)  # Serialized JSON string
    predicted_price = db.Column(db.Float, nullable=False)
    formatted_price = db.Column(db.String(64), nullable=False)
    model_name = db.Column(db.String(64), default='Linear Regression')
    model_r2 = db.Column(db.Float, default=0.90)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def get_input_dict(self) -> dict:
        try:
            return json.loads(self.input_data)
        except Exception:
            return {}

    def to_dict(self):
        input_dict = self.get_input_dict()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'input_data': input_dict,
            'predicted_price': self.predicted_price,
            'formatted_price': self.formatted_price,
            'model_name': self.model_name,
            'model_r2': self.model_r2,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'location': input_dict.get('location', 'N/A'),
            'area': input_dict.get('area', 'N/A'),
            'bedrooms': input_dict.get('bedrooms', 'N/A'),
            'bathrooms': input_dict.get('bathrooms', 'N/A')
        }


class ModelTraining(db.Model):
    __tablename__ = 'model_training'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(64), nullable=False, default='Linear Regression')
    r2_score = db.Column(db.Float, nullable=False)
    mae = db.Column(db.Float, nullable=False)
    rmse = db.Column(db.Float, nullable=False)
    dataset_rows = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(32), default='Ready')
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=True)  # JSON summary

    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'r2_score': self.r2_score,
            'mae': self.mae,
            'rmse': self.rmse,
            'dataset_rows': self.dataset_rows,
            'status': self.status,
            'trained_at': self.trained_at.strftime('%Y-%m-%d %H:%M:%S')
        }
