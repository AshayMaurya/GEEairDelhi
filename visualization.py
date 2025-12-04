"""
Visualization Module for Air Quality Forecasting
Handles all plotting and visualization tasks
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# For interactive maps
try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("⚠️  Folium not available. Install with: pip install folium")

# For advanced plotting
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️  Plotly not available. Install with: pip install plotly")


class Visualizer:
    """Visualization utilities for air quality forecasting"""
    
    def __init__(self, vis_config: Dict):
        """
        Initialize visualizer
        
        Args:
            vis_config: Visualization configuration dictionary
        """
        self.config = vis_config
        self.setup_style()
        
    def setup_style(self):
        """Setup matplotlib style"""
        plt.style.use(self.config.get('style', 'seaborn-v0_8-darkgrid'))
        sns.set_palette(self.config.get('color_palette', 'husl'))
        
    def plot_timeseries(
        self,
        df: pd.DataFrame,
        columns: List[str],
        title: str = "Time Series Data",
        save_path: Optional[str] = None
    ):
        """
        Plot time series data
        
        Args:
            df: DataFrame with 'date' column
            columns: List of columns to plot
            title: Plot title
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(
            len(columns), 1,
            figsize=self.config.get('figure_size', (15, 8)),
            dpi=self.config.get('dpi', 100)
        )
        
        if len(columns) == 1:
            axes = [axes]
        
        for i, col in enumerate(columns):
            axes[i].plot(df['date'], df[col], linewidth=2, label=col)
            axes[i].set_ylabel(col, fontsize=12, fontweight='bold')
            axes[i].legend(loc='upper right')
            axes[i].grid(True, alpha=0.3)
            
            if i == 0:
                axes[i].set_title(title, fontsize=14, fontweight='bold')
            if i == len(columns) - 1:
                axes[i].set_xlabel('Date', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.get('dpi', 100))
            print(f"💾 Saved plot to {save_path}")
        
        plt.show()
    
    def plot_forecast(
        self,
        historical_dates: pd.Series,
        historical_values: np.ndarray,
        forecast_dates: pd.Series,
        forecast_values: np.ndarray,
        pollutant_name: str,
        model_name: str = "",
        confidence_intervals: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        save_path: Optional[str] = None
    ):
        """
        Plot forecast with historical data
        
        Args:
            historical_dates: Historical dates
            historical_values: Historical values
            forecast_dates: Forecast dates
            forecast_values: Forecasted values
            pollutant_name: Name of pollutant
            model_name: Name of model used
            confidence_intervals: Tuple of (lower, upper) confidence bounds
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(
            figsize=self.config.get('figure_size', (15, 8)),
            dpi=self.config.get('dpi', 100)
        )
        
        # Plot historical data
        ax.plot(
            historical_dates,
            historical_values,
            label='Historical Data',
            color='steelblue',
            linewidth=2
        )
        
        # Plot forecast
        ax.plot(
            forecast_dates,
            forecast_values,
            label=f'Forecast ({model_name})' if model_name else 'Forecast',
            color='orangered',
            linewidth=2,
            linestyle='--'
        )
        
        # Plot confidence intervals
        if confidence_intervals is not None and self.config.get('show_confidence_interval', True):
            lower, upper = confidence_intervals
            ax.fill_between(
                forecast_dates,
                lower,
                upper,
                alpha=0.3,
                color='orangered',
                label=f'{int(self.config.get("confidence_level", 0.95)*100)}% Confidence Interval'
            )
        
        # Styling
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{pollutant_name} Concentration', fontsize=12, fontweight='bold')
        ax.set_title(
            f'{pollutant_name} Forecast - {model_name}' if model_name else f'{pollutant_name} Forecast',
            fontsize=14,
            fontweight='bold'
        )
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.get('dpi', 100))
            print(f"💾 Saved forecast plot to {save_path}")
        
        plt.show()
    
    def plot_multiple_forecasts(
        self,
        historical_dates: pd.Series,
        historical_values: np.ndarray,
        forecasts: Dict[str, Tuple[pd.Series, np.ndarray]],
        pollutant_name: str,
        save_path: Optional[str] = None
    ):
        """
        Plot multiple model forecasts together
        
        Args:
            historical_dates: Historical dates
            historical_values: Historical values
            forecasts: Dict of {model_name: (forecast_dates, forecast_values)}
            pollutant_name: Name of pollutant
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(
            figsize=self.config.get('figure_size', (15, 8)),
            dpi=self.config.get('dpi', 100)
        )
        
        # Plot historical data
        ax.plot(
            historical_dates,
            historical_values,
            label='Historical Data',
            color='steelblue',
            linewidth=2.5,
            alpha=0.8
        )
        
        # Plot each forecast
        colors = plt.cm.Set2(np.linspace(0, 1, len(forecasts)))
        
        for i, (model_name, (dates, values)) in enumerate(forecasts.items()):
            ax.plot(
                dates,
                values,
                label=f'{model_name}',
                color=colors[i],
                linewidth=2,
                linestyle='--',
                marker='o',
                markersize=4,
                alpha=0.8
            )
        
        # Styling
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{pollutant_name} Concentration', fontsize=12, fontweight='bold')
        ax.set_title(
            f'{pollutant_name} - Model Comparison',
            fontsize=14,
            fontweight='bold'
        )
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.get('dpi', 100))
            print(f"💾 Saved comparison plot to {save_path}")
        
        plt.show()
    
    def plot_model_comparison(
        self,
        metrics_df: pd.DataFrame,
        save_path: Optional[str] = None
    ):
        """
        Plot model performance comparison
        
        Args:
            metrics_df: DataFrame with models as index and metrics as columns
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(
            2, 2,
            figsize=(14, 10),
            dpi=self.config.get('dpi', 100)
        )
        axes = axes.flatten()
        
        metrics = ['MAE', 'RMSE', 'MAPE', 'R2']
        
        for i, metric in enumerate(metrics):
            if metric in metrics_df.columns:
                metrics_df[metric].plot(
                    kind='bar',
                    ax=axes[i],
                    color=sns.color_palette('husl', len(metrics_df))
                )
                axes[i].set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
                axes[i].set_ylabel(metric, fontsize=10)
                axes[i].set_xlabel('Model', fontsize=10)
                axes[i].tick_params(axis='x', rotation=45)
                axes[i].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.get('dpi', 100))
            print(f"💾 Saved comparison plot to {save_path}")
        
        plt.show()
    
    def plot_feature_importance(
        self,
        importance_dict: Dict[str, float],
        top_n: int = 20,
        save_path: Optional[str] = None
    ):
        """
        Plot feature importance
        
        Args:
            importance_dict: Dictionary of {feature: importance}
            top_n: Number of top features to show
            save_path: Path to save figure
        """
        # Sort and get top N
        sorted_features = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        features, importances = zip(*sorted_features)
        
        fig, ax = plt.subplots(
            figsize=(12, 8),
            dpi=self.config.get('dpi', 100)
        )
        
        y_pos = np.arange(len(features))
        ax.barh(y_pos, importances, color=sns.color_palette('viridis', len(features)))
        ax.set_yticks(y_pos)
        ax.set_yticklabels(features)
        ax.invert_yaxis()
        ax.set_xlabel('Importance', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Feature Importances', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.get('dpi', 100))
            print(f"💾 Saved feature importance plot to {save_path}")
        
        plt.show()
    
    def plot_correlation_matrix(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        save_path: Optional[str] = None
    ):
        """
        Plot correlation matrix
        
        Args:
            df: DataFrame
            columns: Columns to include (if None, uses all numeric columns)
            save_path: Path to save figure
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        corr = df[columns].corr()
        
        fig, ax = plt.subplots(
            figsize=(12, 10),
            dpi=self.config.get('dpi', 100)
        )
        
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.get('dpi', 100))
            print(f"💾 Saved correlation matrix to {save_path}")
        
        plt.show()
    
    def create_interactive_map(
        self,
        center_coords: List[float],
        pollutant_data: Optional[Dict] = None,
        save_path: Optional[str] = None
    ):
        """
        Create interactive map with pollution data
        
        Args:
            center_coords: [latitude, longitude]
            pollutant_data: Dictionary with pollution data
            save_path: Path to save HTML map
        """
        if not FOLIUM_AVAILABLE:
            print("❌ Folium not available for interactive maps")
            return None
        
        # Create map
        m = folium.Map(
            location=[center_coords[1], center_coords[0]],  # folium uses [lat, lon]
            zoom_start=10,
            tiles=self.config.get('map_tiles', 'OpenStreetMap')
        )
        
        # Add marker for center
        folium.Marker(
            [center_coords[1], center_coords[0]],
            popup='Delhi NCR',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        if save_path:
            m.save(save_path)
            print(f"💾 Saved interactive map to {save_path}")
        
        return m
    
    def plot_seasonal_decomposition(
        self,
        dates: pd.Series,
        trend: np.ndarray,
        seasonal: np.ndarray,
        residual: np.ndarray,
        pollutant_name: str,
        save_path: Optional[str] = None
    ):
        """
        Plot seasonal decomposition
        
        Args:
            dates: Date series
            trend: Trend component
            seasonal: Seasonal component
            residual: Residual component
            pollutant_name: Name of pollutant
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(
            3, 1,
            figsize=(15, 10),
            dpi=self.config.get('dpi', 100)
        )
        
        axes[0].plot(dates, trend, color='steelblue', linewidth=2)
        axes[0].set_ylabel('Trend', fontsize=12, fontweight='bold')
        axes[0].set_title(f'{pollutant_name} - Seasonal Decomposition', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(dates, seasonal, color='green', linewidth=2)
        axes[1].set_ylabel('Seasonal', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        axes[2].plot(dates, residual, color='red', linewidth=1, alpha=0.7)
        axes[2].set_ylabel('Residual', fontsize=12, fontweight='bold')
        axes[2].set_xlabel('Date', fontsize=12, fontweight='bold')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.get('dpi', 100))
            print(f"💾 Saved decomposition plot to {save_path}")
        
        plt.show()


def quick_plot(
    df: pd.DataFrame,
    columns: List[str],
    plot_type: str = 'line',
    title: str = "Quick Plot"
):
    """
    Quick plotting function
    
    Args:
        df: DataFrame with data
        columns: Columns to plot
        plot_type: Type of plot ('line', 'scatter', 'bar')
        title: Plot title
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for col in columns:
        if plot_type == 'line':
            ax.plot(df.index, df[col], label=col, linewidth=2)
        elif plot_type == 'scatter':
            ax.scatter(df.index, df[col], label=col, alpha=0.6)
        elif plot_type == 'bar':
            ax.bar(df.index, df[col], label=col, alpha=0.7)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("Visualization module loaded successfully!")
    print(f"Folium available: {FOLIUM_AVAILABLE}")
    print(f"Plotly available: {PLOTLY_AVAILABLE}")
