"""
ml/train_model.py
Model Training Workflow for EstateAI House Price Prediction Platform.
Trains a genuine Linear Regression model using scikit-learn, computes MAE, MSE, RMSE, R²,
and serializes artifacts safely to the models/ directory.
"""

import os
import sys
import json
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure ml package is resolvable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ml.preprocess import prepare_train_test_data, ALL_FEATURES

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'house_prices.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_FILE = os.path.join(MODELS_DIR, 'house_price_model.pkl')
PREPROCESSOR_FILE = os.path.join(MODELS_DIR, 'preprocessor.pkl')
METRICS_FILE = os.path.join(MODELS_DIR, 'model_metrics.json')


def train_and_evaluate(data_path=DATA_PATH):
    print("=" * 60)
    print("ESTATEAI: Linear Regression Training Pipeline")
    print("=" * 60)
    print(f"[1/6] Loading & splitting dataset from: {data_path}")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    X_train, X_test, y_train, y_test, X_train_trans, X_test_trans, preprocessor = (
        prepare_train_test_data(data_path, test_size=0.2, random_state=42)
    )

    print(f"      - Training records: {len(X_train)}")
    print(f"      - Testing records:  {len(X_test)}")
    print(f"      - Transformed feature dimensions: {X_train_trans.shape[1]}")

    print("[2/6] Initializing and fitting scikit-learn Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train_trans, y_train)

    print("[3/6] Generating predictions on evaluation sets...")
    y_train_pred = model.predict(X_train_trans)
    y_test_pred = model.predict(X_test_trans)

    print("[4/6] Computing evaluation metrics on test data...")
    train_r2 = float(r2_score(y_train, y_train_pred))
    test_r2 = float(r2_score(y_test, y_test_pred))
    mae = float(mean_absolute_error(y_test, y_test_pred))
    mse = float(mean_squared_error(y_test, y_test_pred))
    rmse = float(np.sqrt(mse))

    print(f"      -> Train R2 Score : {train_r2:.4f}")
    print(f"      -> Test R2 Score  : {test_r2:.4f}")
    print(f"      -> MAE            : INR {mae:,.2f}")
    print(f"      -> MSE            : {mse:,.2f}")
    print(f"      -> RMSE           : INR {rmse:,.2f}")

    print("[5/6] Extracting feature coefficients...")
    feature_names = preprocessor.get_feature_names_out()
    coef_dict = {
        name: float(coef) for name, coef in zip(feature_names, model.coef_)
    }

    # Extract sample actual vs predicted points for interactive charting
    sample_points = []
    for actual, pred, (_, row) in zip(y_test.values[:60], y_test_pred[:60], X_test.iloc[:60].iterrows()):
        sample_points.append({
            'actual': float(actual),
            'predicted': float(round(pred, 2)),
            'residual': float(round(actual - pred, 2)),
            'area': int(row['area']),
            'location': str(row['location']),
            'bedrooms': int(row['bedrooms'])
        })

    metrics_payload = {
        'model_name': 'Linear Regression',
        'algorithm': 'Ordinary Least Squares (OLS)',
        'framework': 'scikit-learn',
        'trained_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'dataset_file': 'data/house_prices.csv',
        'total_samples': len(X_train) + len(X_test),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'input_features': ALL_FEATURES,
        'encoded_features': feature_names,
        'intercept': float(model.intercept_),
        'coefficients': coef_dict,
        'metrics': {
            'r2_score': round(test_r2, 4),
            'train_r2_score': round(train_r2, 4),
            'mae': round(mae, 2),
            'mse': round(mse, 2),
            'rmse': round(rmse, 2)
        },
        'actual_vs_predicted_samples': sample_points,
        'status': 'Ready'
    }

    print("[6/6] Saving trained model, preprocessor, and metrics...")
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    joblib.dump(preprocessor, PREPROCESSOR_FILE)
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"      - Saved model:        {MODEL_FILE}")
    print(f"      - Saved preprocessor: {PREPROCESSOR_FILE}")
    print(f"      - Saved metrics:      {METRICS_FILE}")
    print("=" * 60)
    print("Training successfully completed!")
    print("=" * 60)
    return metrics_payload


if __name__ == '__main__':
    train_and_evaluate()
