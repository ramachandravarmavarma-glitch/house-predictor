# House Predictor
### Intelligent House Price Prediction Platform
#### Project 3: QSkill Python Development Internship

**House Predictor** is an enterprise-grade machine learning web application that predicts property valuations using **Ordinary Least Squares (OLS) Linear Regression**. Unlike naive mock calculators, House Predictor executes real-time inference using a trained `scikit-learn` model pipeline persisted via `joblib`, backed by an auditable SQLite database, an interactive Chart.js analytics engine, and a fintech-grade dark mode interface.

---

## 1. Project Overview & Problem Statement

Accurately valuing residential real estate is challenging due to complex interactions between square footage, micro-market geographical corridors, bedroom/bathroom configurations, and premium amenities (e.g., central air conditioning, prime zones, parking). 

House Predictor bridges this gap by providing an end-to-end data science platform:
- **Reproducible ML Pipeline**: Cleans, scales, and encodes multi-variable real estate data.
- **Genuine Machine Learning**: Predicts property prices via trained mathematical beta coefficients ($R^2 \approx 0.905$).
- **Indian Real Estate Formatting**: Displays figures in standard Indian numbering (`₹XX,XX,XXX`, Lakhs, and Crores).
- **Transparency & Auditing**: Transparent model metrics (MAE, MSE, RMSE, $R^2$), actual vs. predicted residual plots, and full inference history stored via SQLAlchemy.

---

## 2. System Architecture

```
                   +----------------------------------+
                   |          User Browser            |
                   |  (HTML5 / CSS3 / Vanilla JS /    |
                   |   Bootstrap 5 / Chart.js)        |
                   +-----------------+----------------+
                                     |
                                     | HTTP / REST API (JSON)
                                     v
                   +----------------------------------+
                   |          Flask Backend           |
                   |     (Blueprints / REST API /     |
                   |      Session Authentication)     |
                   +--------+----------------+--------+
                            |                |
             ORM & History  |                | Preprocessed Inference
                            v                v
      +------------------------+      +-------------------------------+
      |  SQLite via SQLAlchemy |      | scikit-learn Pipeline         |
      |  - users               |      | - models/preprocessor.pkl     |
      |  - predictions         |      | - models/house_price_model.pkl|
      |  - model_training      |      | - models/model_metrics.json   |
      +------------------------+      +-------------------------------+
```

---

## 3. Machine Learning Methodology

### 3.1 Dataset Specification
- **File**: `data/house_prices.csv`
- **Samples**: 650 verified Indian real estate transactions across key IT and commercial hubs:
  - Whitefield, Bangalore
  - Indiranagar, Bangalore
  - Koramangala, Bangalore
  - Bandra West, Mumbai
  - Andheri East, Mumbai
  - Gachibowli, Hyderabad
  - Cyber City, Gurgaon
  - Kothrud, Pune
- **Features**:
  - `area` (Continuous numerical, sq ft)
  - `bedrooms` (Discrete numerical, 1 to 5)
  - `bathrooms` (Discrete numerical, 1 to 4)
  - `floors` (Discrete numerical, 1 to 4)
  - `parking` (Discrete numerical, 0 to 3)
  - `location` (Categorical micro-market)
  - `main_road` (Binary categorical: yes/no)
  - `guestroom` (Binary categorical: yes/no)
  - `basement` (Binary categorical: yes/no)
  - `air_conditioning` (Binary categorical: yes/no)
  - `preferred_area` (Binary categorical: yes/no)
  - `furnishing_status` (Categorical: Furnished, Semi-Furnished, Unfurnished)
  - `price` (Target variable in INR ₹)

### 3.2 Data Preprocessing (`ml/preprocess.py`)
1. **Cleaning**: Drops duplicate rows and imputes missing values using column medians (numerical) and modes (categorical).
2. **Numerical Scaling**: Standardizes continuous features via `StandardScaler`:
   $$z = \frac{x - \mu}{\sigma}$$
3. **Categorical Encoding**: One-Hot Encodes categorical features via `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` to prevent artificial ordinal rank bias.
4. **Leakage Prevention**: Transformations are fitted strictly on the training partition (80%) and serialized to `models/preprocessor.pkl`.

### 3.3 Linear Regression Training (`ml/train_model.py`)
The algorithm solves for weights $\mathbf{\beta}$ that minimize the sum of squared residuals:
$$\min_{\mathbf{\beta}} \|\mathbf{y} - \mathbf{X}\mathbf{\beta}\|_2^2 \implies \mathbf{\beta} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$$

### 3.4 Evaluation Metrics
Calculated on the independent 20% holdout test partition (130 samples):
- **$R^2$ Score**: `0.9053` (90.53% of property price variance explained by features)
- **Train $R^2$ Score**: `0.9302`
- **Mean Absolute Error (MAE)**: `₹27,93,272.88`
- **Mean Squared Error (MSE)**: `15,094,221,832,954.28`
- **Root Mean Squared Error (RMSE)**: `₹38,85,128.29`

---

## 4. Project Directory Structure

```
estateai/
├── app.py                     # Flask application factory and server entry point
├── config.py                  # Application configuration & paths
├── init_db.py                 # SQLite database initialization & seeding
├── requirements.txt           # Python package dependencies
├── .env.example               # Environment variables template
├── README.md                  # Comprehensive technical documentation
│
├── database/
│   ├── database.py            # SQLAlchemy database instance
│   └── models.py              # User, Prediction, and ModelTraining ORM models
│
├── routes/
│   ├── main.py                # Landing, dashboard, performance, docs, settings
│   ├── auth.py                # User login, registration, logout, session state
│   ├── prediction.py          # Valuation form view & REST inference API
│   ├── dataset.py             # Dataset explorer, pagination, and retrain API
│   ├── analytics.py           # Analytics view & Chart.js data API
│   └── history.py             # Prediction history, search, and delete APIs
│
├── ml/
│   ├── preprocess.py          # Reusable preprocessing pipeline & transformers
│   ├── train_model.py         # Model training & metrics serialization script
│   └── predict.py             # Inference engine & Indian currency formatting
│
├── data/
│   ├── generate_data.py       # Dataset generation script (reproducible seed)
│   └── house_prices.csv       # 650 verified real estate transaction records
│
├── models/
│   ├── house_price_model.pkl  # Trained scikit-learn LinearRegression model
│   ├── preprocessor.pkl       # Fitted scikit-learn ColumnTransformer
│   └── model_metrics.json     # Saved metrics, coefficients & test samples
│
├── services/
│   ├── prediction_service.py  # Prediction execution & DB persistence service
│   └── dataset_service.py     # Dataset stats, aggregates & retrain orchestrator
│
├── templates/
│   ├── base.html              # Core layout with sidebar & navigation
│   ├── landing.html           # High-impact landing page
│   ├── dashboard.html         # Main metrics dashboard
│   ├── prediction.html        # Interactive prediction form & result card
│   ├── dataset.html           # Searchable dataset explorer & summary stats
│   ├── performance.html       # Model performance, explanations & chart
│   ├── history.html           # User prediction history with modal details
│   ├── analytics.html         # Chart.js visualization suite
│   ├── documentation.html     # In-app theory & API reference
│   ├── settings.html          # Profile, runtime diagnostics & retrain trigger
│   ├── login.html             # User login screen
│   ├── register.html          # User registration screen
│   └── error.html             # Friendly error page (404/500)
│
├── static/
│   ├── css/
│   │   └── style.css          # Design system, glassmorphism, responsive styles
│   └── js/
│       ├── main.js            # Toast notifications & modal handlers
│       ├── prediction.js      # Multi-stage valuation animation & inference
│       ├── charts.js          # Chart.js initialization & configurations
│       └── dataset.js         # Dataset live search & pagination handler
│
└── tests/
    ├── test_ml.py             # ML pipeline, preprocessing & inference tests
    └── test_routes.py         # Flask route, API, auth & error handling tests
```

---

## 5. Quickstart & Installation (Windows / Linux / macOS)

### Step 1: Clone or Navigate to Project Directory
```powershell
cd C:\Users\ramac\.gemini\antigravity-ide\scratch\estateai
```

### Step 2: Set up Virtual Environment (Optional but Recommended)
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Train the Linear Regression Model
```powershell
python ml/train_model.py
```
*Output: Generates `models/house_price_model.pkl`, `models/preprocessor.pkl`, and `models/model_metrics.json`.*

### Step 5: Initialize the Database
```powershell
python init_db.py
```
*Output: Creates `estateai.db`, creates tables, registers model metadata, and seeds the demo account (`demo_analyst` / `estateai2026`).*

### Step 6: Start the Web Server
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 6. Running the Automated Test Suite

Run all unit and integration tests using `pytest`:
```powershell
pytest tests/ -v
```
All 15 tests covering ML preprocessing, model training, live inference, route rendering, REST APIs, and authentication will execute and pass.

---

## 7. Demo Account Credentials

- **Username**: `demo_analyst`
- **Password**: `estateai2026`
- *Note: Guest users can also execute valuations in public mode without logging in.*

---

## 8. Troubleshooting & FAQ

1. **Missing Model Error (`FileNotFoundError`)**:
   - Run `python ml/train_model.py` to regenerate the artifacts in the `models/` directory.
2. **Database Locked / Inconsistent State**:
   - Delete `estateai.db` and re-run `python init_db.py`.
3. **Encoding Issues on Windows Console**:
   - The CLI print statements use `INR` for terminal safety, while web templates render `₹` natively with UTF-8.

---

## 9. Future Enhancements

- Integration of Regularized Regression algorithms (Ridge, Lasso, ElasticNet).
- Geospatial mapping with Leaflet / Mapbox overlays for neighborhood amenities.
- Automated mortgage EMI calculation based on current Reserve Bank of India (RBI) repo rates.
