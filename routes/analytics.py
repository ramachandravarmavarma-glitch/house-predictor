"""
routes/analytics.py
Analytics routes for EstateAI: Interactive charts for property price distributions,
feature correlations, and model actual vs predicted evaluation plots.
"""

from flask import Blueprint, render_template, jsonify
from services.dataset_service import DatasetService
from routes.auth import get_current_user

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics')
def analytics_page():
    user = get_current_user()
    return render_template('analytics.html', user=user)


@analytics_bp.route('/api/analytics/charts')
def api_analytics_charts():
    try:
        data = DatasetService.get_analytics()
        return jsonify({'success': True, 'charts': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
