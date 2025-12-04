"""
Complete Air Quality Analysis Pipeline
Processes ALL pollutants with ML models and spatial mapping
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

from config import *
from data_fetcher import GEEDataFetcher
from preprocessing import DataPreprocessor
from models import (ARIMAModel, ProphetModel, LSTMModel, 
                   XGBoostModel, RandomForestModel, evaluate_model)
from visualization import Visualizer
from spatial_mapper import SpatialMapper


class CompleteAnalysis:
    """
    Complete analysis pipeline for all pollutants
    """
    
    def __init__(self):
        """Initialize analysis pipeline"""
        self.fetcher = None
        self.preprocessor = None
        self.visualizer = None
        self.mapper = None
        self.results = {}
        
        # Create output directories
        self.output_dirs = {
            'data': 'data',
            'models': 'outputs/models',
            'plots': 'outputs/plots',
            'maps': 'outputs/maps',
            'predictions': 'outputs/predictions',
            'reports': 'outputs/reports'
        }
        
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def initialize(self):
        """Initialize all components"""
        print("=" * 70)
        print("INITIALIZING AIR QUALITY ANALYSIS PIPELINE")
        print("=" * 70)
        
        # Initialize GEE
        self.fetcher = GEEDataFetcher(REGION_CONFIG, GEE_CONFIG)
        self.fetcher.authenticate_and_initialize()
        
        # Initialize other components
        # Initialize other components
        self.preprocessor = DataPreprocessor(FEATURE_CONFIG)
        self.visualizer = Visualizer(VIS_CONFIG)
        self.mapper = SpatialMapper(self.fetcher, REGION_CONFIG, POLLUTANTS)
        
        # Set pixel density from config
        self.mapper.set_pixel_density(
            SPATIAL_MAP_CONFIG['default_pixel_density']
        )
        
        print("✅ All components initialized\n")
    
    def fetch_all_data(self):
        """Fetch data for all active pollutants"""
        print("=" * 70)
        print("FETCHING DATA FOR ALL POLLUTANTS")
        print("=" * 70)
        print(f"Pollutants: {', '.join(ACTIVE_POLLUTANTS)}")
        print(f"Date Range: {TRAIN_START_DATE} to {TRAIN_END_DATE}")
        print(f"Temporal Resolution: {TEMPORAL_RESOLUTION}\n")
        
        # Fetch data
        raw_data = self.fetcher.fetch_all_pollutants(
            pollutants_config=POLLUTANTS,
            active_pollutants=ACTIVE_POLLUTANTS,
            start_date=TRAIN_START_DATE,
            end_date=TRAIN_END_DATE,
            scale=SPATIAL_SCALE,
            reducer=REDUCER,
            temporal_resolution=TEMPORAL_RESOLUTION
        )
        
        # Save raw data
        if EXPORT_CONFIG['save_raw_data']:
            filename = f"{self.output_dirs['data']}/raw_data.csv"
            raw_data.to_csv(filename, index=False)
            print(f"\n💾 Raw data saved to {filename}")
        
        return raw_data
    
    def analyze_pollutant(self, pollutant_name, data):
        """
        Complete analysis for a single pollutant
        
        Args:
            pollutant_name: Name of pollutant
            data: DataFrame with pollutant data
            
        Returns:
            Dictionary with analysis results
        """
        print("\n" + "=" * 70)
        print(f"ANALYZING {pollutant_name}")
        print("=" * 70)
        
        results = {
            'pollutant': pollutant_name,
            'models': {},
            'predictions': {},
            'metrics': {},
            'plots': [],
            'maps': []
        }
        
        # Prepare data
        pollutant_data = data[['date', pollutant_name]].copy()
        pollutant_data = pollutant_data.dropna()
        
        if len(pollutant_data) == 0:
            print(f"⚠️  No data available for {pollutant_name}")
            return results
        
        # Split data
        train_size = int(len(pollutant_data) * (1 - VALIDATION_SPLIT))
        train_data = pollutant_data[:train_size]
        test_data = pollutant_data[train_size:]
        
        print(f"Training samples: {len(train_data)}")
        print(f"Testing samples: {len(test_data)}\n")
        
        # Train models
        active_models = get_active_models()
        print(f"Training {len(active_models)} models: {', '.join(active_models)}\n")
        
        for model_name in active_models:
            try:
                print(f"Training {model_name}...")
                model, predictions, metrics = self._train_model(
                    model_name, pollutant_name, train_data, test_data
                )
                
                results['models'][model_name] = model
                results['predictions'][model_name] = predictions
                results['metrics'][model_name] = metrics
                
                print(f"  ✅ {model_name} - RMSE: {metrics.get('RMSE', 'N/A'):.6f}")
                
            except Exception as e:
                print(f"  ❌ {model_name} failed: {e}")
        
        # Generate forecasts
        print(f"\nGenerating {FORECAST_DAYS}-day forecast...")
        forecast_dates = get_forecast_dates()
        
        for model_name, model in results['models'].items():
            try:
                forecast = self._generate_forecast(
                    model, model_name, pollutant_data, forecast_dates
                )
                results['predictions'][f'{model_name}_forecast'] = forecast
            except Exception as e:
                print(f"  ⚠️  Forecast failed for {model_name}: {e}")
        
        # Create visualizations
        print("\nCreating visualizations...")
        results['plots'] = self._create_visualizations(
            pollutant_name, pollutant_data, results
        )
        
        # Create spatial maps
        print("\nCreating spatial maps...")
        results['maps'] = self._create_spatial_maps(
            pollutant_name, results
        )
        
        # Save results
        self._save_results(pollutant_name, results)
        
        return results
    
    def _train_model(self, model_name, pollutant_name, train_data, test_data):
        """Train a single model"""
        # Prepare data format based on model type
        if model_name == 'ARIMA':
            model = ARIMAModel(MODEL_CONFIG['ARIMA'])
            model.train(train_data[pollutant_name].values)
            predictions = model.predict(len(test_data))
            
        elif model_name == 'Prophet':
            model = ProphetModel(MODEL_CONFIG['Prophet'])
            prophet_data = train_data.rename(columns={'date': 'ds', pollutant_name: 'y'})
            model.train(prophet_data)
            future_dates = test_data['date'].values
            predictions = model.predict(future_dates)
            
        elif model_name == 'LSTM':
            model = LSTMModel(MODEL_CONFIG['LSTM'])
            model.train(train_data[pollutant_name].values)
            predictions = model.predict(len(test_data))
            
        elif model_name == 'XGBoost':
            model = XGBoostModel(MODEL_CONFIG['XGBoost'])
            X_train, y_train = self._prepare_ml_data(train_data, pollutant_name)
            X_test, y_test = self._prepare_ml_data(test_data, pollutant_name)
            model.train(X_train, y_train)
            predictions = model.predict(X_test)
            
        elif model_name == 'RandomForest':
            model = RandomForestModel(MODEL_CONFIG['RandomForest'])
            X_train, y_train = self._prepare_ml_data(train_data, pollutant_name)
            X_test, y_test = self._prepare_ml_data(test_data, pollutant_name)
            model.train(X_train, y_train)
            predictions = model.predict(X_test)
        
        # Evaluate
        actual = test_data[pollutant_name].values
        metrics = evaluate_model(actual, predictions)
        
        return model, predictions, metrics
    
    def _prepare_ml_data(self, data, pollutant_name):
        """Prepare data for ML models"""
        # Simple feature engineering - add lag features
        df = data.copy()
        
        # Add lag features
        for lag in [1, 3, 7]:
            df[f'lag_{lag}'] = df[pollutant_name].shift(lag)
        
        # Add rolling mean
        df['rolling_mean_7'] = df[pollutant_name].rolling(7).mean()
        
        # Drop NaN
        df = df.dropna()
        
        # Features and target
        feature_cols = [col for col in df.columns if col not in ['date', pollutant_name]]
        X = df[feature_cols].values
        y = df[pollutant_name].values
        
        return X, y
    
    def _generate_forecast(self, model, model_name, data, forecast_dates):
        """Generate future forecast"""
        if model_name in ['ARIMA', 'LSTM']:
            return model.predict(len(forecast_dates))
        elif model_name == 'Prophet':
            return model.predict(forecast_dates)
        else:
            # For ML models, use last known values as features
            # This is simplified - in production you'd use proper feature engineering
            return np.zeros(len(forecast_dates))
    
    def _create_visualizations(self, pollutant_name, data, results):
        """Create all visualizations for a pollutant"""
        plots = []
        
        try:
            # Time series plot
            filename = f"{self.output_dirs['plots']}/{pollutant_name}_timeseries.png"
            self.visualizer.plot_time_series(
                data, pollutant_name, save_path=filename
            )
            plots.append(filename)
            
            # Predictions comparison
            if results['predictions']:
                filename = f"{self.output_dirs['plots']}/{pollutant_name}_predictions.png"
                self.visualizer.plot_predictions(
                    data, results['predictions'], pollutant_name, save_path=filename
                )
                plots.append(filename)
            
            # Model comparison
            if results['metrics']:
                filename = f"{self.output_dirs['plots']}/{pollutant_name}_model_comparison.png"
                self.visualizer.plot_model_comparison(
                    results['metrics'], save_path=filename
                )
                plots.append(filename)
                
        except Exception as e:
            print(f"  ⚠️  Visualization error: {e}")
        
        return plots
    
    def _create_spatial_maps(self, pollutant_name, results):
        """Create spatial maps for pollutant"""
        maps = []
        
        try:
            # Historical maps (quarterly)
            dates_to_map = [
                '2022-01-01', '2022-04-01', '2022-07-01', '2022-10-01'
            ]
            
            for date in dates_to_map:
                try:
                    # Create HTML map
                    m = self.mapper.create_pollutant_map(
                        pollutant_name, date,
                        output_dir=self.output_dirs['maps']
                    )
                    maps.append(f"{pollutant_name}_{date.replace('-', '')}.html")
                    
                    # Create static PNG map
                    self.mapper.create_static_map(
                        pollutant_name, date,
                        output_dir=self.output_dirs['maps']
                    )
                except Exception as e:
                    print(f"    ⚠️  Map creation failed for {date}: {e}")
            
        except Exception as e:
            print(f"  ⚠️  Spatial mapping error: {e}")
        
        return maps
    
    def _save_results(self, pollutant_name, results):
        """Save analysis results"""
        # Save predictions
        predictions_file = f"{self.output_dirs['predictions']}/{pollutant_name}_predictions.json"
        
        # Convert predictions to serializable format
        predictions_data = {}
        for key, value in results['predictions'].items():
            if isinstance(value, np.ndarray):
                predictions_data[key] = value.tolist()
            else:
                predictions_data[key] = value
        
        with open(predictions_file, 'w') as f:
            json.dump(predictions_data, f, indent=2)
        
        # Save metrics
        metrics_file = f"{self.output_dirs['predictions']}/{pollutant_name}_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(results['metrics'], f, indent=2)
        
        print(f"  💾 Results saved to {self.output_dirs['predictions']}/")
    
    def run_complete_analysis(self):
        """Run complete analysis for all pollutants"""
        print("\n" + "=" * 70)
        print("STARTING COMPLETE ANALYSIS PIPELINE")
        print("=" * 70)
        
        # Initialize
        self.initialize()
        
        # Fetch data
        raw_data = self.fetch_all_data()
        
        # Analyze each pollutant
        for pollutant in ACTIVE_POLLUTANTS:
            try:
                results = self.analyze_pollutant(pollutant, raw_data)
                self.results[pollutant] = results
            except Exception as e:
                print(f"\n❌ Analysis failed for {pollutant}: {e}")
        
        # Generate summary report
        self._generate_summary_report()
        
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"\n📁 Results saved in:")
        for name, path in self.output_dirs.items():
            print(f"   {name}: {path}/")
        
        return self.results
    
    def _generate_summary_report(self):
        """Generate summary report of all analyses"""
        report_file = f"{self.output_dirs['reports']}/analysis_summary.txt"
        
        with open(report_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("AIR QUALITY ANALYSIS SUMMARY REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Region: {REGION_CONFIG['name']}\n")
            f.write(f"Date Range: {TRAIN_START_DATE} to {TRAIN_END_DATE}\n")
            f.write(f"Pollutants Analyzed: {', '.join(ACTIVE_POLLUTANTS)}\n")
            f.write(f"Pixel Density: {self.mapper.get_pixel_density()}m\n\n")
            
            for pollutant, results in self.results.items():
                f.write(f"\n{pollutant}\n")
                f.write("-" * 70 + "\n")
                
                if results['metrics']:
                    f.write("Model Performance:\n")
                    for model_name, metrics in results['metrics'].items():
                        f.write(f"  {model_name}:\n")
                        for metric, value in metrics.items():
                            f.write(f"    {metric}: {value:.6f}\n")
                
                f.write(f"\nVisualizations: {len(results['plots'])} plots created\n")
                f.write(f"Spatial Maps: {len(results['maps'])} maps created\n")
        
        print(f"\n📄 Summary report saved to {report_file}")


if __name__ == "__main__":
    # Run complete analysis
    analysis = CompleteAnalysis()
    results = analysis.run_complete_analysis()
