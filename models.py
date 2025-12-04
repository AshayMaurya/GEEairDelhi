"""
ML Models Module for Air Quality Forecasting
Implements multiple forecasting models
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Statistical models
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️  Prophet not available. Install with: pip install prophet")

# ML models
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not available. Install with: pip install tensorflow")

# XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not available. Install with: pip install xgboost")


class ForecastModel:
    """Base class for forecasting models"""
    
    def __init__(self, model_name: str, config: Dict):
        self.model_name = model_name
        self.config = config
        self.model = None
        self.is_fitted = False
        
    def fit(self, X_train, y_train):
        raise NotImplementedError
        
    def predict(self, X_test):
        raise NotImplementedError
        
    def forecast(self, steps: int):
        raise NotImplementedError


class ARIMAModel(ForecastModel):
    """ARIMA/SARIMA model for time-series forecasting"""
    
    def __init__(self, config: Dict):
        super().__init__("ARIMA", config)
        
    def fit(self, y_train: pd.Series):
        """Fit ARIMA model"""
        print(f"🔧 Training ARIMA model...")
        
        order = self.config.get('order', (5, 1, 2))
        seasonal_order = self.config.get('seasonal_order', (1, 1, 1, 7))
        
        try:
            self.model = SARIMAX(
                y_train,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.model = self.model.fit(disp=False)
            self.is_fitted = True
            print("✅ ARIMA model trained")
        except Exception as e:
            print(f"❌ ARIMA training failed: {e}")
            
    def predict(self, steps: int) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        forecast = self.model.forecast(steps=steps)
        return forecast.values
    
    def get_confidence_intervals(self, steps: int, alpha: float = 0.05):
        """Get prediction confidence intervals"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        forecast_result = self.model.get_forecast(steps=steps)
        conf_int = forecast_result.conf_int(alpha=alpha)
        
        return conf_int


class ProphetModel(ForecastModel):
    """Facebook Prophet model"""
    
    def __init__(self, config: Dict):
        super().__init__("Prophet", config)
        
    def fit(self, df: pd.DataFrame, target_col: str = 'y'):
        """Fit Prophet model"""
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet not installed")
        
        print(f"🔧 Training Prophet model...")
        
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_df = df.copy()
        if 'ds' not in prophet_df.columns and 'date' in prophet_df.columns:
            prophet_df['ds'] = prophet_df['date']
        if 'y' not in prophet_df.columns and target_col in prophet_df.columns:
            prophet_df['y'] = prophet_df[target_col]
        
        self.model = Prophet(
            changepoint_prior_scale=self.config.get('changepoint_prior_scale', 0.05),
            seasonality_prior_scale=self.config.get('seasonality_prior_scale', 10),
            yearly_seasonality=self.config.get('yearly_seasonality', True),
            weekly_seasonality=self.config.get('weekly_seasonality', True),
            daily_seasonality=self.config.get('daily_seasonality', False)
        )
        
        self.model.fit(prophet_df[['ds', 'y']])
        self.is_fitted = True
        print("✅ Prophet model trained")
        
    def predict(self, future_df: pd.DataFrame) -> pd.DataFrame:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        forecast = self.model.predict(future_df)
        return forecast


class LSTMModel(ForecastModel):
    """LSTM neural network for time-series"""
    
    def __init__(self, config: Dict):
        super().__init__("LSTM", config)
        self.sequence_length = config.get('sequence_length', 30)
        
    def create_sequences(self, data: np.ndarray, seq_length: int):
        """Create sequences for LSTM"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i+seq_length])
            y.append(data[i+seq_length])
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple):
        """Build LSTM architecture"""
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow not installed")
        
        hidden_units = self.config.get('hidden_units', [64, 32])
        dropout = self.config.get('dropout', 0.2)
        learning_rate = self.config.get('learning_rate', 0.001)
        
        model = keras.Sequential()
        
        # First LSTM layer
        model.add(layers.LSTM(
            hidden_units[0],
            return_sequences=len(hidden_units) > 1,
            input_shape=input_shape
        ))
        model.add(layers.Dropout(dropout))
        
        # Additional LSTM layers
        for i, units in enumerate(hidden_units[1:]):
            return_seq = i < len(hidden_units) - 2
            model.add(layers.LSTM(units, return_sequences=return_seq))
            model.add(layers.Dropout(dropout))
        
        # Output layer
        model.add(layers.Dense(1))
        
        # Compile
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train LSTM model"""
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow not installed")
        
        print(f"🔧 Training LSTM model...")
        
        # Create sequences
        X_seq, y_seq = self.create_sequences(X_train, self.sequence_length)
        
        # Reshape for LSTM [samples, time steps, features]
        if len(X_seq.shape) == 2:
            X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
        
        # Build model
        self.model = self.build_model(input_shape=(X_seq.shape[1], X_seq.shape[2]))
        
        # Train
        epochs = self.config.get('epochs', 50)
        batch_size = self.config.get('batch_size', 32)
        
        self.model.fit(
            X_seq, y_seq,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=0
        )
        
        self.is_fitted = True
        print("✅ LSTM model trained")
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        # Create sequences
        X_seq, _ = self.create_sequences(X_test, self.sequence_length)
        
        # Reshape
        if len(X_seq.shape) == 2:
            X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
        
        predictions = self.model.predict(X_seq, verbose=0)
        return predictions.flatten()


class XGBoostModel(ForecastModel):
    """XGBoost model for forecasting"""
    
    def __init__(self, config: Dict):
        super().__init__("XGBoost", config)
        
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train XGBoost model"""
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost not installed")
        
        print(f"🔧 Training XGBoost model...")
        
        self.model = xgb.XGBRegressor(
            n_estimators=self.config.get('n_estimators', 100),
            max_depth=self.config.get('max_depth', 7),
            learning_rate=self.config.get('learning_rate', 0.1),
            subsample=self.config.get('subsample', 0.8),
            colsample_bytree=self.config.get('colsample_bytree', 0.8),
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        print("✅ XGBoost model trained")
    
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        return self.model.predict(X_test)
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        return dict(zip(
            self.model.get_booster().feature_names,
            self.model.feature_importances_
        ))


class RandomForestModel(ForecastModel):
    """Random Forest model for forecasting"""
    
    def __init__(self, config: Dict):
        super().__init__("RandomForest", config)
        
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train Random Forest model"""
        print(f"🔧 Training Random Forest model...")
        
        self.model = RandomForestRegressor(
            n_estimators=self.config.get('n_estimators', 100),
            max_depth=self.config.get('max_depth', 15),
            min_samples_split=self.config.get('min_samples_split', 5),
            min_samples_leaf=self.config.get('min_samples_leaf', 2),
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        print("✅ Random Forest model trained")
    
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        return self.model.predict(X_test)
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        return dict(zip(
            X_train.columns if hasattr(self, 'X_train') else range(len(self.model.feature_importances_)),
            self.model.feature_importances_
        ))


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "") -> Dict:
    """
    Evaluate model performance
    
    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
    
    Returns:
        Dictionary with metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape,
        'R2': r2
    }
    
    if model_name:
        print(f"\n📊 {model_name} Performance:")
        print(f"  MAE:  {mae:.6f}")
        print(f"  RMSE: {rmse:.6f}")
        print(f"  MAPE: {mape:.2f}%")
        print(f"  R²:   {r2:.4f}")
    
    return metrics


if __name__ == "__main__":
    print("Models module loaded successfully!")
    print(f"Prophet available: {PROPHET_AVAILABLE}")
    print(f"TensorFlow available: {TF_AVAILABLE}")
    print(f"XGBoost available: {XGBOOST_AVAILABLE}")
