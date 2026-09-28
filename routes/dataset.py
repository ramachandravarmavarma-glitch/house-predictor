"""
routes/dataset.py
Dataset explorer routes for EstateAI: UI view, statistics, paginated table, and model retraining.
"""

from flask import Blueprint, render_template, request, jsonify
from services.dataset_service import DatasetService
from routes.auth import get_current_user

dataset_bp = Blueprint('dataset', __name__)


@dataset_bp.route('/dataset')
def dataset_page():
    user = get_current_user()
    overview = DatasetService.get_overview()
    initial_page = DatasetService.get_paginated(page=1, per_page=12)
    return render_template(
        'dataset.html',
        user=user,
        overview=overview,
        initial_page=initial_page
    )


@dataset_bp.route('/api/dataset/overview')
def api_dataset_overview():
    try:
        overview = DatasetService.get_overview()
        return jsonify({'success': True, 'overview': overview})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dataset_bp.route('/api/dataset/rows')
def api_dataset_rows():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        search = request.args.get('search', '').strip()

        result = DatasetService.get_paginated(page=page, per_page=per_page, search=search if search else None)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dataset_bp.route('/api/model/retrain', methods=['POST'])
def api_retrain_model():
    try:
        payload = DatasetService.trigger_retraining()
        return jsonify({
            'success': True,
            'message': 'Model successfully retrained and deployed!',
            'metrics': payload.get('metrics', {}),
            'timestamp': payload.get('trained_at')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f"Retraining failed: {str(e)}"}), 500
