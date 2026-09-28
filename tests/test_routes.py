"""
tests/test_routes.py
Integration tests for EstateAI Flask web application routes and APIs.
"""

import os
import sys
import json
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from database.database import db


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_landing_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Predict Property Value With Machine Learning." in response.data


def test_dashboard_page(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Analytics Dashboard" in response.data
    assert b"Model Status" in response.data


def test_prediction_page(client):
    response = client.get('/predict')
    assert response.status_code == 200
    assert b"Estimate Property Value" in response.data


def test_api_predict_valid(client):
    payload = {
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
        'furnishing_status': 'Semi-Furnished'
    }

    response = client.post(
        '/api/predict',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'predicted_price' in data['prediction']
    assert 'formatted_price' in data['prediction']


def test_api_predict_invalid_data(client):
    bad_payload = {'area': -10}
    response = client.post(
        '/api/predict',
        data=json.dumps(bad_payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_dataset_overview_api(client):
    response = client.get('/api/dataset/overview')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['overview']['total_rows'] > 0


def test_dataset_rows_api(client):
    response = client.get('/api/dataset/rows?page=1&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']['records']) == 5


def test_analytics_charts_api(client):
    response = client.get('/api/analytics/charts')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'price_bins' in data['charts']
    assert 'area_vs_price' in data['charts']


def test_auth_registration_and_login(client):
    # Register new user
    reg_resp = client.post('/register', data={
        'username': 'tester_jane',
        'email': 'jane@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert reg_resp.status_code == 200

    # Logout
    logout_resp = client.get('/logout', follow_redirects=True)
    assert logout_resp.status_code == 200

    # Login
    login_resp = client.post('/login', data={
        'username': 'tester_jane',
        'password': 'password123'
    }, follow_redirects=True)
    assert login_resp.status_code == 200
    assert b"tester_jane" in login_resp.data
