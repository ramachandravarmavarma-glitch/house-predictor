"""
services/prediction_service.py
Business logic service for managing prediction inference, persistence, and history.
"""

import json
from datetime import datetime
from database.database import db
from database.models import Prediction
from ml.predict import predict_price, format_inr


class PredictionService:

    @staticmethod
    def execute_and_record_prediction(input_data: dict, user_id: int = None) -> dict:
        """
        Executes prediction with the real Linear Regression model and stores record.
        """
        result = predict_price(input_data)
        
        # Save record to database
        record = Prediction(
            user_id=user_id,
            input_data=json.dumps(result['input_summary']),
            predicted_price=result['predicted_price'],
            formatted_price=result['formatted_price'],
            model_name=result['model_used'],
            model_r2=result['model_r2']
        )
        db.session.add(record)
        db.session.commit()

        result['prediction_id'] = record.id
        result['created_at'] = record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return result

    @staticmethod
    def get_user_history(user_id: int = None, search: str = None, sort_by: str = 'date_desc'):
        """
        Retrieves prediction history for a specific user with search and sorting.
        """
        query = Prediction.query
        if user_id:
            query = query.filter_by(user_id=user_id)

        if search:
            search_term = f"%{search.strip().lower()}%"
            query = query.filter(
                db.or_(
                    Prediction.input_data.ilike(search_term),
                    Prediction.formatted_price.ilike(search_term)
                )
            )

        if sort_by == 'price_desc':
            query = query.order_by(Prediction.predicted_price.desc())
        elif sort_by == 'price_asc':
            query = query.order_by(Prediction.predicted_price.asc())
        elif sort_by == 'date_asc':
            query = query.order_by(Prediction.created_at.asc())
        else:
            query = query.order_by(Prediction.created_at.desc())

        records = query.all()
        return [r.to_dict() for r in records]

    @staticmethod
    def get_prediction_by_id(prediction_id: int, user_id: int = None):
        query = Prediction.query.filter_by(id=prediction_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        record = query.first()
        return record.to_dict() if record else None

    @staticmethod
    def delete_prediction(prediction_id: int, user_id: int = None) -> bool:
        query = Prediction.query.filter_by(id=prediction_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        record = query.first()
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False

    @staticmethod
    def clear_history(user_id: int = None) -> int:
        query = Prediction.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        count = query.count()
        query.delete(synchronize_session=False)
        db.session.commit()
        return count

    @staticmethod
    def get_summary_stats(user_id: int = None) -> dict:
        query = Prediction.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        total = query.count()
        if total == 0:
            return {
                'total_predictions': 0,
                'avg_price': '₹0',
                'max_price': '₹0',
                'min_price': '₹0'
            }
        
        prices = [p.predicted_price for p in query.all()]
        avg_p = sum(prices) / total
        max_p = max(prices)
        min_p = min(prices)
        return {
            'total_predictions': total,
            'avg_price': format_inr(avg_p),
            'max_price': format_inr(max_p),
            'min_price': format_inr(min_p)
        }
