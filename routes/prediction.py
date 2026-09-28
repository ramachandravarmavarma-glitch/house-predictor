"""
routes/prediction.py
Prediction endpoints for EstateAI: UI view, REST API inference, and prediction details.
"""

from flask import Blueprint, render_template, request, jsonify, session
from services.prediction_service import PredictionService
from ml.preprocess import KNOWN_LOCATIONS, FURNISHING_CHOICES
from routes.auth import get_current_user

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/predict')
def predict_page():
    user = get_current_user()
    return render_template(
        'prediction.html',
        user=user,
        locations=KNOWN_LOCATIONS,
        furnishing_options=FURNISHING_CHOICES
    )


@prediction_bp.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            # Fallback to form data
            data = request.form.to_dict()

        if not data:
            return jsonify({'success': False, 'error': 'No input data provided'}), 400

        user = get_current_user()
        user_id = user.id if user else None

        result = PredictionService.execute_and_record_prediction(data, user_id=user_id)
        return jsonify({
            'success': True,
            'prediction': result
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({'success': False, 'error': f"Model error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f"An error occurred while calculating estimate: {str(e)}"}), 500


@prediction_bp.route('/api/prediction/<int:pred_id>')
def api_get_prediction(pred_id):
    user = get_current_user()
    user_id = user.id if user else None
    prediction = PredictionService.get_prediction_by_id(pred_id, user_id=user_id)
    if not prediction:
        return jsonify({'success': False, 'error': 'Prediction record not found'}), 404
    return jsonify({'success': True, 'prediction': prediction})
