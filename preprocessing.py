"""
Data Preprocessing and Feature Engineering Module
Handles data cleaning, interpolation, and feature creation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy import interpolate
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import warnings
warnings.filterwarnings('ignore')


class DataPreprocessor:
    """Preprocess and engineer features for time-series forecasting"""
    
    def __init__(self, feature_config: Dict):
        """
        Initialize preprocessor
        
        Args:
            feature_config: Configuration dictionary for feature engineering
        """
        self.feature_config = feature_config
        self.scalers = {}
        self.original_columns = []
        
    def clean_data(
        self,
        df: pd.DataFrame,
        interpolation_method: str = 'linear',
        max_missing_days: int = 7
    ) -> pd.DataFrame:
        """
        Clean data by handling missing values and outliers
        
        Args:
            df: Input DataFrame with 'date' column
            interpolation_method: Method for interpolation
            max_missing_days: Maximum consecutive days to interpolate
        
        Returns:
            Cleaned DataFrame
        """
        print("🧹 Cleaning data...")
        
        df = df.copy()
        
        # Ensure date column is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
        
        # Create complete date range
        date_range = pd.date_range(
            start=df['date'].min(),
            end=df['date'].max(),
            freq='D'
        )
        
        # Reindex to fill missing dates
        df = df.set_index('date').reindex(date_range).reset_index()
        df.rename(columns={'index': 'date'}, inplace=True)
        
        # Store original columns
        self.original_columns = [col for col in df.columns if col != 'date']
        
        # Interpolate missing values
        for col in self.original_columns:
            if df[col].isna().any():
                missing_count = df[col].isna().sum()
                print(f"  ⚠️  {col}: {missing_count} missing values")
                
                # Interpolate
                df[col] = df[col].interpolate(method=interpolation_method, limit=max_missing_days)
                
                # Fill remaining NaNs with forward/backward fill
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
        
        # Remove outliers using IQR method
        for col in self.original_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if outliers > 0:
                print(f"  🔍 {col}: {outliers} outliers detected and capped")
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        print(f"✅ Data cleaned: {len(df)} records")
        return df
    
    def create_lag_features(self, df: pd.DataFrame, target_cols: List[str]) -> pd.DataFrame:
        """
        Create lag features
        
        Args:
            df: Input DataFrame
            target_cols: Columns to create lags for
        
        Returns:
            DataFrame with lag features
        """
        df = df.copy()
        lag_days = self.feature_config.get('lag_days', [1, 3, 7, 14, 30])
        
        print(f"📊 Creating lag features for {len(lag_days)} time steps...")
        
        for col in target_cols:
            for lag in lag_days:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, target_cols: List[str]) -> pd.DataFrame:
        """
        Create rolling window statistics
        
        Args:
            df: Input DataFrame
            target_cols: Columns to create rolling features for
        
        Returns:
            DataFrame with rolling features
        """
        df = df.copy()
        windows = self.feature_config.get('rolling_windows', [7, 14, 30])
        stats = self.feature_config.get('rolling_stats', ['mean', 'std'])
        
        print(f"📊 Creating rolling features for {len(windows)} windows...")
        
        for col in target_cols:
            for window in windows:
                for stat in stats:
                    if stat == 'mean':
                        df[f'{col}_rolling_{window}_mean'] = df[col].rolling(window=window).mean()
                    elif stat == 'std':
                        df[f'{col}_rolling_{window}_std'] = df[col].rolling(window=window).std()
                    elif stat == 'min':
                        df[f'{col}_rolling_{window}_min'] = df[col].rolling(window=window).min()
                    elif stat == 'max':
                        df[f'{col}_rolling_{window}_max'] = df[col].rolling(window=window).max()
        
        return df
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal features from date
        
        Args:
            df: Input DataFrame with 'date' column
        
        Returns:
            DataFrame with temporal features
        """
        df = df.copy()
        temporal_features = self.feature_config.get('temporal_features', [])
        
        print(f"📅 Creating {len(temporal_features)} temporal features...")
        
        if 'day_of_week' in temporal_features:
            df['day_of_week'] = df['date'].dt.dayofweek
        
        if 'day_of_month' in temporal_features:
            df['day_of_month'] = df['date'].dt.day
        
        if 'month' in temporal_features:
            df['month'] = df['date'].dt.month
        
        if 'quarter' in temporal_features:
            df['quarter'] = df['date'].dt.quarter
        
        if 'is_weekend' in temporal_features:
            df['is_weekend'] = (df['date'].dt.dayofweek >= 5).astype(int)
        
        if 'is_month_start' in temporal_features:
            df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        
        if 'is_month_end' in temporal_features:
            df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        # Cyclical encoding for periodic features
        if 'day_of_week' in df.columns:
            df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        if 'month' in df.columns:
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def create_all_features(
        self,
        df: pd.DataFrame,
        target_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Create all features at once
        
        Args:
            df: Input DataFrame
            target_cols: Target columns (if None, uses all non-date columns)
        
        Returns:
            DataFrame with all features
        """
        print("\n🔧 Feature Engineering Pipeline")
        print("=" * 50)
        
        df = df.copy()
        
        if target_cols is None:
            target_cols = [col for col in df.columns if col != 'date']
        
        # Create temporal features
        df = self.create_temporal_features(df)
        
        # Create lag features
        df = self.create_lag_features(df, target_cols)
        
        # Create rolling features
        df = self.create_rolling_features(df, target_cols)
        
        # Drop rows with NaN (from lag/rolling operations)
        initial_rows = len(df)
        df = df.dropna().reset_index(drop=True)
        dropped_rows = initial_rows - len(df)
        
        print(f"\n📉 Dropped {dropped_rows} rows due to feature creation")
        print(f"✅ Final dataset: {len(df)} rows, {len(df.columns)} columns")
        print("=" * 50)
        
        return df
    
    def scale_features(
        self,
        df: pd.DataFrame,
        method: str = 'standard',
        exclude_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Scale features for ML models
        
        Args:
            df: Input DataFrame
            method: Scaling method ('standard' or 'minmax')
            exclude_cols: Columns to exclude from scaling
        
        Returns:
            Scaled DataFrame
        """
        df = df.copy()
        
        if exclude_cols is None:
            exclude_cols = ['date']
        
        cols_to_scale = [col for col in df.columns if col not in exclude_cols]
        
        print(f"⚖️  Scaling {len(cols_to_scale)} features using {method} scaling...")
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
        self.scalers[method] = scaler
        
        return df
    
    def inverse_scale(
        self,
        values: np.ndarray,
        method: str = 'standard',
        feature_index: int = 0
    ) -> np.ndarray:
        """
        Inverse transform scaled values
        
        Args:
            values: Scaled values
            method: Scaling method used
            feature_index: Index of feature in scaler
        
        Returns:
            Original scale values
        """
        if method not in self.scalers:
            raise ValueError(f"No scaler found for method: {method}")
        
        scaler = self.scalers[method]
        
        # Create dummy array with same shape as scaler expects
        n_features = scaler.n_features_in_
        dummy = np.zeros((len(values), n_features))
        dummy[:, feature_index] = values.flatten()
        
        # Inverse transform
        inverse = scaler.inverse_transform(dummy)
        
        return inverse[:, feature_index]
    
    def train_test_split(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        validation_size: float = 0.1
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train, validation, and test sets (time-based)
        
        Args:
            df: Input DataFrame
            test_size: Proportion of data for testing
            validation_size: Proportion of training data for validation
        
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        n = len(df)
        test_idx = int(n * (1 - test_size))
        val_idx = int(test_idx * (1 - validation_size))
        
        train_df = df.iloc[:val_idx].copy()
        val_df = df.iloc[val_idx:test_idx].copy()
        test_df = df.iloc[test_idx:].copy()
        
        print(f"\n📊 Data Split:")
        print(f"  Train: {len(train_df)} samples ({train_df['date'].min()} to {train_df['date'].max()})")
        print(f"  Validation: {len(val_df)} samples ({val_df['date'].min()} to {val_df['date'].max()})")
        print(f"  Test: {len(test_df)} samples ({test_df['date'].min()} to {test_df['date'].max()})")
        
        return train_df, val_df, test_df
    
    def get_feature_importance_data(self, df: pd.DataFrame) -> Dict:
        """
        Prepare data for feature importance analysis
        
        Args:
            df: DataFrame with features
        
        Returns:
            Dictionary with feature categories
        """
        features = {
            'original': self.original_columns,
            'lag': [col for col in df.columns if 'lag' in col],
            'rolling': [col for col in df.columns if 'rolling' in col],
            'temporal': [col for col in df.columns if any(x in col for x in ['day_', 'month_', 'quarter', 'weekend'])],
            'all_features': [col for col in df.columns if col != 'date']
        }
        
        return features


def quick_preprocess(
    df: pd.DataFrame,
    feature_config: Dict,
    clean: bool = True,
    create_features: bool = True,
    scale: bool = False
) -> pd.DataFrame:
    """
    Quick preprocessing function
    
    Args:
        df: Input DataFrame
        feature_config: Feature configuration
        clean: Whether to clean data
        create_features: Whether to create features
        scale: Whether to scale features
    
    Returns:
        Processed DataFrame
    """
    preprocessor = DataPreprocessor(feature_config)
    
    if clean:
        df = preprocessor.clean_data(df)
    
    if create_features:
        df = preprocessor.create_all_features(df)
    
    if scale:
        df = preprocessor.scale_features(df)
    
    return df


if __name__ == "__main__":
    # Example usage
    from config import FEATURE_CONFIG
    
    # Create sample data
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'SO2': np.random.rand(len(dates)) * 0.001,
        'NO2': np.random.rand(len(dates)) * 0.0002
    })
    
    # Add some missing values
    sample_data.loc[10:15, 'SO2'] = np.nan
    
    # Preprocess
    preprocessor = DataPreprocessor(FEATURE_CONFIG)
    cleaned = preprocessor.clean_data(sample_data)
    featured = preprocessor.create_all_features(cleaned)
    
    print("\nProcessed data shape:", featured.shape)
    print("\nFeature columns:")
    print(featured.columns.tolist())
