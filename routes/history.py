"""
routes/history.py
Prediction History routes for EstateAI: Search, filter, delete, and view detailed predictions.
"""

from flask import Blueprint, render_template, request, jsonify
from services.prediction_service import PredictionService
from routes.auth import get_current_user

history_bp = Blueprint('history', __name__)


@history_bp.route('/history')
def history_page():
    user = get_current_user()
    user_id = user.id if user else None
    predictions = PredictionService.get_user_history(user_id=user_id)
    summary_stats = PredictionService.get_summary_stats(user_id=user_id)
    return render_template(
        'history.html',
        user=user,
        predictions=predictions,
        stats=summary_stats
    )


@history_bp.route('/api/history')
def api_get_history():
    try:
        user = get_current_user()
        user_id = user.id if user else None
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'date_desc')

        predictions = PredictionService.get_user_history(
            user_id=user_id,
            search=search if search else None,
            sort_by=sort_by
        )
        return jsonify({'success': True, 'predictions': predictions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@history_bp.route('/api/history/<int:pred_id>', methods=['DELETE'])
def api_delete_prediction(pred_id):
    try:
        user = get_current_user()
        user_id = user.id if user else None
        success = PredictionService.delete_prediction(pred_id, user_id=user_id)
        if success:
            return jsonify({'success': True, 'message': 'Prediction deleted successfully.'})
        return jsonify({'success': False, 'error': 'Record not found or unauthorized.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@history_bp.route('/api/history/clear', methods=['POST', 'DELETE'])
def api_clear_history():
    try:
        user = get_current_user()
        user_id = user.id if user else None
        deleted_count = PredictionService.clear_history(user_id=user_id)
        return jsonify({'success': True, 'message': f'Cleared {deleted_count} prediction records.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
