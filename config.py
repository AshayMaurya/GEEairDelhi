"""
Configuration file for Air Quality Forecasting Project
Modify these parameters to customize your analysis
"""

from datetime import datetime, timedelta

# ==================== REGION CONFIGURATION ====================
REGION_CONFIG = {
    'name': 'Delhi',
    'admin_level': 'ADM1_NAME',  # Administrative level in GAUL dataset
    'center_coords': [77.2090, 28.6139],  # [longitude, latitude]
    'zoom_level': 7
}

# ==================== DATE RANGE CONFIGURATION ====================
# Training data range
# NOTE: Sentinel-5P data available from April 30, 2018 onwards
TRAIN_START_DATE = '2020-01-01'  # Start from May 2018 (when data is available)
TRAIN_END_DATE = '2022-12-31'

# Validation/Test split
VALIDATION_SPLIT = 0.2  # 20% of data for validation

# Forecast horizon (days into the future)
FORECAST_DAYS = 30

# ==================== POLLUTANT CONFIGURATION ====================
POLLUTANTS = {
    'SO2': {
        'collection': 'COPERNICUS/S5P/OFFL/L3_SO2',
        'band': 'SO2_column_number_density',
        'vis_params': {'min': 0, 'max': 0.001},
        'palette': ['yellow', 'orange', 'red', 'purple', 'blue', 'cyan', 'white'],
        'unit': 'mol/m²'
    },
    'NO2': {
        'collection': 'COPERNICUS/S5P/OFFL/L3_NO2',
        'band': 'NO2_column_number_density',
        'vis_params': {'min': 0, 'max': 0.0002},
        'palette': ['green', 'yellow', 'orange', 'red', 'purple', 'blue', 'white'],
        'unit': 'mol/m²'
    },
    'CO': {
        'collection': 'COPERNICUS/S5P/OFFL/L3_CO',
        'band': 'CO_column_number_density',
        'vis_params': {'min': 0, 'max': 0.05},
        'palette': ['green', 'yellow', 'orange', 'red', 'purple', 'blue', 'white'],
        'unit': 'mol/m²'
    },
    'Aerosol': {
        'collection': 'COPERNICUS/S5P/OFFL/L3_AER_AI',
        'band': 'absorbing_aerosol_index',
        'vis_params': {'min': -1, 'max': 2},
        'palette': ['blue', 'white', 'red'],
        'unit': 'index'
    },
    'O3': {
        'collection': 'COPERNICUS/S5P/OFFL/L3_O3',
        'band': 'O3_column_number_density',
        'vis_params': {'min': 0.12, 'max': 0.15},
        'palette': ['blue', 'cyan', 'green', 'yellow', 'orange', 'red'],
        'unit': 'mol/m²'
    }
}

# Select which pollutants to analyze (comment out to exclude)
ACTIVE_POLLUTANTS = ['SO2', 'NO2', 'CO', 'Aerosol']

# ==================== DATA PROCESSING CONFIGURATION ====================
# Spatial resolution for data extraction (meters)
SPATIAL_SCALE = 1000

# Statistical reducer to use (median, mean, max, min)
REDUCER = 'median'

# Temporal resolution for data fetching
# 'monthly' - Faster, avoids 5000 element limit, good for long-term trends
# 'daily' - More detailed, slower, may hit limits with large date ranges
TEMPORAL_RESOLUTION = 'monthly'

# Performance optimizations
USE_POLARS = True  # Use Polars for faster data processing (5-10x faster than pandas)
PARALLEL_FETCH = True  # Fetch multiple pollutants in parallel (2-4x faster)

# Handle missing data
INTERPOLATION_METHOD = 'linear'  # 'linear', 'polynomial', 'spline'
MAX_MISSING_DAYS = 7  # Maximum consecutive missing days to interpolate

# ==================== FEATURE ENGINEERING CONFIGURATION ====================
FEATURE_CONFIG = {
    # Lag features (previous values)
    'lag_days': [1, 3, 7, 14, 30],
    
    # Rolling window statistics
    'rolling_windows': [7, 14, 30],  # days
    'rolling_stats': ['mean', 'std', 'min', 'max'],
    
    # Temporal features
    'temporal_features': [
        'day_of_week',
        'day_of_month',
        'month',
        'quarter',
        'is_weekend',
        'is_month_start',
        'is_month_end'
    ],
    
    # Seasonal decomposition
    'use_seasonal_decompose': True,
    'seasonal_period': 365  # days
}

# ==================== MODEL CONFIGURATION ====================
MODEL_CONFIG = {
    'ARIMA': {
        'enabled': True,
        'order': (5, 1, 2),  # (p, d, q)
        'seasonal_order': (1, 1, 1, 7)  # (P, D, Q, s)
    },
    
    'Prophet': {
        'enabled': True,
        'changepoint_prior_scale': 0.05,
        'seasonality_prior_scale': 10,
        'yearly_seasonality': True,
        'weekly_seasonality': True,
        'daily_seasonality': False
    },
    
    'LSTM': {
        'enabled': True,
        'sequence_length': 30,  # Look back window
        'hidden_units': [64, 32],
        'dropout': 0.2,
        'epochs': 50,
        'batch_size': 32,
        'learning_rate': 0.001
    },
    
    'XGBoost': {
        'enabled': True,
        'n_estimators': 100,
        'max_depth': 7,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8
    },
    
    'RandomForest': {
        'enabled': True,
        'n_estimators': 100,
        'max_depth': 15,
        'min_samples_split': 5,
        'min_samples_leaf': 2
    }
}

# ==================== VISUALIZATION CONFIGURATION ====================
VIS_CONFIG = {
    'figure_size': (15, 8),
    'dpi': 100,
    'style': 'seaborn-v0_8-darkgrid',  # matplotlib style
    'color_palette': 'husl',
    
    # Forecast plot settings
    'show_confidence_interval': True,
    'confidence_level': 0.95,
    
    # Map settings
    'map_tiles': 'OpenStreetMap',  # 'OpenStreetMap', 'Stamen Terrain', 'CartoDB positron'
    'map_opacity': 0.7,
    
    # Save settings
    'save_plots': True,
    'output_dir': 'outputs',
    'plot_format': 'png'  # 'png', 'jpg', 'svg', 'pdf'
}

# ==================== EVALUATION METRICS ====================
METRICS = [
    'MAE',   # Mean Absolute Error
    'RMSE',  # Root Mean Squared Error
    'MAPE',  # Mean Absolute Percentage Error
    'R2'     # R-squared Score
]

# ==================== GOOGLE EARTH ENGINE CONFIGURATION ====================
GEE_CONFIG = {
    'project_id': None,  # Set your GEE project ID if using a cloud project
    'max_retries': 3,
    'timeout': 300  # seconds
}

# ==================== EXPORT CONFIGURATION ====================
EXPORT_CONFIG = {
    'save_raw_data': True,
    'save_processed_data': True,
    'save_predictions': True,
    'data_format': 'csv',  # 'csv', 'parquet', 'json'
    'data_dir': 'data'
}

# ==================== SPATIAL MAPPING CONFIGURATION ====================
SPATIAL_MAP_CONFIG = {
    # Pixel density control (meters per pixel)
    # Lower values = higher resolution but slower processing
    # Higher values = lower resolution but faster processing
    # Recommended range: 100-5000
    'default_pixel_density': 1000,  # 1km per pixel (good balance)
    
    # Available pixel density presets
    'pixel_density_presets': {
        'ultra_high': 100,   # 100m - Very detailed, slow
        'high': 500,         # 500m - Detailed
        'medium': 1000,      # 1km - Balanced (default)
        'low': 2000,         # 2km - Fast
        'ultra_low': 5000    # 5km - Very fast, less detail
    },
    
    # Map output settings
    'output_dir': 'outputs/maps',
    'map_opacity': 0.7,
    'show_region_boundary': True,
    'show_colorbar': True,
    
    # Time series animation settings
    'animation_fps': 2,  # Frames per second for animations
    'animation_format': 'gif',  # 'gif' or 'mp4'
}

# ==================== HELPER FUNCTIONS ====================
def get_date_range(start_date=None, end_date=None):
    """Get date range as datetime objects"""
    start = datetime.strptime(start_date or TRAIN_START_DATE, '%Y-%m-%d')
    end = datetime.strptime(end_date or TRAIN_END_DATE, '%Y-%m-%d')
    return start, end

def get_forecast_dates(base_date=None, days=None):
    """Get future dates for forecasting"""
    if base_date is None:
        base_date = datetime.strptime(TRAIN_END_DATE, '%Y-%m-%d')
    elif isinstance(base_date, str):
        base_date = datetime.strptime(base_date, '%Y-%m-%d')
    
    forecast_days = days or FORECAST_DAYS
    return [base_date + timedelta(days=i) for i in range(1, forecast_days + 1)]

def get_active_models():
    """Get list of enabled models"""
    return [model for model, config in MODEL_CONFIG.items() if config.get('enabled', False)]

def print_config_summary():
    """Print configuration summary"""
    print("=" * 60)
    print("AIR QUALITY FORECASTING - CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"\n📍 Region: {REGION_CONFIG['name']}")
    print(f"📅 Training Period: {TRAIN_START_DATE} to {TRAIN_END_DATE}")
    print(f"🔮 Forecast Horizon: {FORECAST_DAYS} days")
    print(f"\n🌫️  Active Pollutants: {', '.join(ACTIVE_POLLUTANTS)}")
    print(f"🤖 Active Models: {', '.join(get_active_models())}")
    print(f"📊 Metrics: {', '.join(METRICS)}")
    print("=" * 60)

if __name__ == "__main__":
    print_config_summary()
