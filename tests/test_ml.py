"""
tests/test_ml.py
Unit and regression tests for EstateAI machine learning pipeline.
Tests preprocessing, artifact serialization, model training, and inference.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config
from ml.preprocess import (
    load_dataset,
    prepare_train_test_data,
    HousingPreprocessor,
    ALL_FEATURES
)
from ml.train_model import train_and_evaluate
from ml.predict import predict_price, format_inr, format_inr_words


def test_dataset_exists_and_loads():
    assert os.path.exists(Config.DATA_PATH), f"Dataset file missing at {Config.DATA_PATH}"
    df = load_dataset(Config.DATA_PATH)
    assert len(df) > 100, f"Expected dataset rows > 100, got {len(df)}"
    assert 'price' in df.columns, "Target column 'price' missing"
    for feat in ALL_FEATURES:
        assert feat in df.columns, f"Required feature '{feat}' missing in dataset"


def test_preprocessing_pipeline():
    df = load_dataset(Config.DATA_PATH)
    X = df[ALL_FEATURES]
    preprocessor = HousingPreprocessor()
    X_trans = preprocessor.fit_transform(X)

    assert X_trans.shape[0] == len(df)
    assert X_trans.shape[1] >= len(ALL_FEATURES)
    assert not np.isnan(X_trans).any(), "NaN values found in transformed feature matrix"


def test_model_training_and_artifacts():
    metrics = train_and_evaluate(Config.DATA_PATH)
    assert os.path.exists(Config.MODEL_FILE), "Model pickle artifact not created"
    assert os.path.exists(Config.PREPROCESSOR_FILE), "Preprocessor pickle artifact not created"
    assert os.path.exists(Config.METRICS_FILE), "Metrics JSON artifact not created"

    # Scientific metric sanity checks
    r2 = metrics['metrics']['r2_score']
    assert 0.60 <= r2 <= 1.0, f"Unrealistic R2 score: {r2}"
    assert metrics['metrics']['mae'] > 0
    assert metrics['metrics']['rmse'] > 0


def test_inference_pipeline_valid():
    sample_input = {
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

    result = predict_price(sample_input)
    assert 'predicted_price' in result
    assert result['predicted_price'] > 1000000, "Price prediction unrealistically low"
    assert 'formatted_price' in result
    assert '₹' in result['formatted_price']
    assert result['model_used'] == 'Linear Regression'


def test_inference_missing_input_raises():
    bad_input = {
        'bedrooms': 3,
        'location': 'Whitefield, Bangalore'
        # Missing area, bathrooms, etc.
    }
    with pytest.raises(ValueError):
        predict_price(bad_input)


def test_inr_formatting():
    assert format_inr(100000) == "₹1,00,000"
    assert format_inr(15000000) == "₹1,50,00,000"
    assert format_inr(24500000) == "₹2,45,00,000"
    assert "Cr" in format_inr_words(25000000)
    assert "Lakhs" in format_inr_words(4500000)
