"""
ml/preprocess.py
Reusable Data Preprocessing Pipeline for EstateAI House Price Prediction Platform.
Handles data loading, cleaning, missing values, duplicate removal, feature scaling,
and categorical encoding using scikit-learn transformers.
"""

import os
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

NUMERICAL_FEATURES = ['area', 'bedrooms', 'bathrooms', 'floors', 'parking']
CATEGORICAL_FEATURES = [
    'location',
    'main_road',
    'guestroom',
    'basement',
    'air_conditioning',
    'preferred_area',
    'furnishing_status'
]
ALL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = 'price'

# Standard reference categories for encoding consistency
KNOWN_LOCATIONS = [
    'Whitefield, Bangalore',
    'Indiranagar, Bangalore',
    'Koramangala, Bangalore',
    'Bandra West, Mumbai',
    'Andheri East, Mumbai',
    'Gachibowli, Hyderabad',
    'Cyber City, Gurgaon',
    'Kothrud, Pune'
]

BINARY_CHOICES = ['no', 'yes']
FURNISHING_CHOICES = ['Furnished', 'Semi-Furnished', 'Unfurnished']


class HousingPreprocessor(BaseEstimator, TransformerMixin):
    """
    Custom transformer combining cleaning, numerical scaling, and categorical one-hot encoding.
    Ensures exact consistency between training and real-time single-sample inference.
    """
    def __init__(self):
        self.num_features = NUMERICAL_FEATURES
        self.cat_features = CATEGORICAL_FEATURES
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(
            handle_unknown='ignore',
            sparse_output=False
        )
        self.column_transformer = None
        self.feature_names_ = []
        self.is_fitted_ = False

    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Imputes missing values using domain medians and modes."""
        df_clean = df.copy()
        for col in self.num_features:
            if col in df_clean.columns:
                med_val = df_clean[col].median()
                if pd.isna(med_val):
                    med_val = 1
                df_clean[col] = df_clean[col].fillna(med_val)
        for col in self.cat_features:
            if col in df_clean.columns:
                mode_val = df_clean[col].mode()
                fill_val = mode_val[0] if len(mode_val) > 0 else 'no'
                df_clean[col] = df_clean[col].fillna(fill_val)
        return df_clean

    def fit(self, X: pd.DataFrame, y=None):
        X_clean = self._impute_missing(X)
        self.column_transformer = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.num_features),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), self.cat_features)
            ],
            remainder='drop'
        )
        self.column_transformer.fit(X_clean)
        
        # Build feature names
        num_names = self.num_features
        cat_names = list(self.column_transformer.named_transformers_['cat'].get_feature_names_out(self.cat_features))
        self.feature_names_ = list(num_names) + list(cat_names)
        self.is_fitted_ = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted_:
            raise ValueError("HousingPreprocessor is not fitted yet. Call fit() before transform().")
        X_clean = self._impute_missing(X)
        return self.column_transformer.transform(X_clean)

    def get_feature_names_out(self):
        return self.feature_names_


def load_dataset(file_path: str) -> pd.DataFrame:
    """Loads and performs initial checks on the housing dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    
    df = pd.read_csv(file_path)
    
    # Drop pure duplicates
    initial_rows = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    dropped = initial_rows - len(df)
    if dropped > 0:
        print(f"Removed {dropped} duplicate rows.")

    # Validate target column
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' missing from dataset.")

    return df


def prepare_train_test_data(data_path: str, test_size=0.2, random_state=42):
    """
    Loads raw CSV, cleans, separates features & target, and splits into train/test sets.
    """
    df = load_dataset(data_path)
    
    # Validate required columns
    missing_cols = [c for c in ALL_FEATURES if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    X = df[ALL_FEATURES].copy()
    y = df[TARGET_COLUMN].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    preprocessor = HousingPreprocessor()
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    return X_train, X_test, y_train, y_test, X_train_trans, X_test_trans, preprocessor
