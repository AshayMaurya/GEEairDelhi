# Air Quality Forecasting - Delhi NCR

Complete ML-based air quality analysis with **geographical spatial mapping** for Delhi-NCR region.

## 🌟 Features

### Core Capabilities
- **Multi-Pollutant Analysis**: SO2, NO2, CO, Aerosol Index
- **Multiple ML Models**: ARIMA, Prophet, LSTM, XGBoost, Random Forest
- **Time Series Forecasting**: 30-day predictions
- **Automated Pipeline**: Processes ALL pollutants automatically

### 🗺️ Spatial Mapping (NEW!)
- **Geographical Color-Coded Maps**: Visual pollutant density across Delhi-NCR
- **Pixel-Level Precision**: Configurable resolution (100m - 5000m per pixel)
- **Time Evolution**: Track pollutant changes over time
- **Interactive Maps**: Toggle layers, zoom, explore region
- **Historical + Predictions**: Maps for both past data and forecasts

## 📊 What You Get

### For Each Pollutant:
1. **Data**: Raw and processed time series
2. **Models**: 5 trained ML models with performance metrics
3. **Predictions**: 30-day forecasts
4. **Visualizations**: Time series plots, prediction comparisons
5. **Spatial Maps**: Interactive geographical maps showing density evolution

### Output Structure:
```
outputs/
├── maps/          # Interactive HTML and Static PNG geographical maps
├── plots/         # Time series and prediction charts
├── predictions/   # Model predictions and metrics (JSON)
├── models/        # Saved model files
└── reports/       # Analysis summary reports
```

## 🚀 Quick Start

### 1. Setup
```bash
pip install -r requirements.txt
```

### 2. Clean and Prepare
```bash
python cleanup_project.py
python update_notebook.py
```

### 3. Run Analysis

**Option A: Jupyter Notebook** (Recommended)
```bash
jupyter notebook analysis.ipynb
```
Then run all cells.

**Option B: Python Script**
```bash
python complete_analysis.py
```

## 🎛️ Configuration

### Pixel Density Control
Edit `config.py`:
```python
SPATIAL_MAP_CONFIG = {
    'default_pixel_density': 1000,  # meters per pixel
}
```

**Presets:**
- `ultra_high` (100m): Maximum detail, slow
- `high` (500m): High detail
- `medium` (1000m): Balanced ⭐ **Default**
- `low` (2000m): Fast processing
- `ultra_low` (5000m): Very fast, regional view

### Select Pollutants
```python
ACTIVE_POLLUTANTS = ['SO2', 'NO2', 'CO', 'Aerosol']
```

### Date Range
```python
TRAIN_START_DATE = '2020-01-01'
TRAIN_END_DATE = '2022-12-31'
FORECAST_DAYS = 30
```

### Enable/Disable Models
```python
MODEL_CONFIG = {
    'ARIMA': {'enabled': True, ...},
    'Prophet': {'enabled': True, ...},
    # ... etc
}
```

## 📈 Analysis Pipeline

```
1. Initialize GEE → 2. Fetch Data → 3. Train Models → 4. Predict → 5. Visualize → 6. Map
```

For **each pollutant**, the system:
1. Fetches historical data from Google Earth Engine
2. Trains all enabled ML models
3. Generates predictions and forecasts
4. Creates time series visualizations
5. Generates geographical color-coded maps
6. Saves all outputs with metrics

## 🗺️ Spatial Mapping Details

### Map Features
- **Color-coded density**: Visual representation of pollutant levels
- **Region boundary**: Delhi-NCR highlighted
- **Colorbar legend**: Concentration scale
- **Interactive**: Zoom, pan, toggle layers
- **Time series**: Multiple maps show evolution

### Creating Maps

**Single pollutant map:**
```python
from spatial_mapper import quick_map

m = quick_map(
    pollutant='NO2',
    date='2022-06-01',
    pixel_density=1000
)
```

**Time evolution maps:**
```python
mapper.create_time_series_maps(
    pollutant_name='NO2',
    start_date='2022-01-01',
    end_date='2022-12-31',
    interval_days=30  # Monthly
)
```

**Multi-pollutant map:**
```python
mapper.create_multi_pollutant_map(
    date_str='2022-06-01',
    pollutant_names=['NO2', 'SO2', 'CO']
)
```

## 📁 Project Structure

```
GEE/
├── Core Modules
│   ├── config.py              # Configuration
│   ├── data_fetcher.py        # GEE data fetching
│   ├── preprocessing.py       # Data preprocessing
│   ├── models.py              # ML models
│   ├── visualization.py       # Plotting
│   ├── spatial_mapper.py      # Geographical mapping
│   └── complete_analysis.py   # Complete pipeline
│
├── Analysis
│   └── analysis.ipynb         # Main notebook
│
├── Data & Outputs
│   ├── data/                  # Raw/processed data
│   └── outputs/
│       ├── maps/              # Geographical maps
│       ├── plots/             # Visualizations
│       ├── predictions/       # Predictions & metrics
│       └── reports/           # Summary reports
│
└── Documentation
    ├── README.md              # This file
    ├── EXECUTION_PLAN.md      # Detailed execution guide
    └── requirements.txt       # Dependencies
```

## 🎯 Use Cases

### Research
- Study pollutant spatial distribution
- Analyze temporal trends
- Compare model performance
- Generate forecasts

### Policy Making
- Identify pollution hotspots
- Track seasonal variations
- Evaluate intervention effectiveness
- Plan mitigation strategies

### Public Awareness
- Share interactive maps
- Visualize air quality trends
- Communicate predictions
- Educate about pollution patterns

## 📊 Model Performance

Each model generates metrics:
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **MAPE**: Mean Absolute Percentage Error
- **R²**: R-squared score

Best model is automatically identified for each pollutant.

## 🔧 Advanced Usage

### Adjust Pixel Density Dynamically
```python
analysis = CompleteAnalysis()
analysis.mapper.set_pixel_density(500)  # High detail
```

### Export High-Res GeoTIFF
```python
task = mapper.export_high_res_image(
    pollutant_name='NO2',
    date_str='2022-06-01'
)
# Check Google Drive 'GEE_Exports' folder
```

### Process Single Pollutant
```python
analysis = CompleteAnalysis()
analysis.initialize()
results = analysis.analyze_pollutant('NO2', raw_data)
```

## 📝 Output Files

### Data Files
- `data/raw_data.csv` - Raw fetched data
- `outputs/predictions/{pollutant}_predictions.json` - Predictions
- `outputs/predictions/{pollutant}_metrics.json` - Performance metrics

### Visualizations
- `outputs/plots/{pollutant}_timeseries.png` - Time series
- `outputs/plots/{pollutant}_predictions.png` - Predictions
- `outputs/plots/{pollutant}_model_comparison.png` - Model comparison

### Spatial Maps
- `outputs/maps/{pollutant}_YYYYMMDD.html` - Interactive maps
- Quarterly maps for each pollutant
- Multi-pollutant comparison maps

### Reports
- `outputs/reports/analysis_summary.txt` - Complete summary

## ⚡ Performance Tips

**For Speed:**
- Use higher pixel density (2000-5000m)
- Monthly temporal resolution
- Disable some models
- Shorter date range

**For Quality:**
- Use lower pixel density (100-500m)
- Daily temporal resolution
- Enable all models
- Longer training period

## 🐛 Troubleshooting

### GEE Authentication
```python
import ee
ee.Authenticate()
ee.Initialize()
```

### Memory Issues
- Increase pixel density
- Reduce date range
- Process fewer pollutants

### Slow Processing
- Use 'monthly' resolution
- Higher pixel density
- Disable heavy models (LSTM)

## 📖 Documentation

- **EXECUTION_PLAN.md**: Detailed step-by-step guide
- **STATUS.md**: Project status and progress
- **config.py**: All configuration options with comments

## 🎓 Understanding Results

### Map Colors
- **Blue/Cyan**: Low concentration
- **Green/Yellow**: Medium
- **Orange/Red**: High
- **Purple**: Very high

### Metrics
- **Lower MAE/RMSE**: Better accuracy
- **Higher R²**: Better fit (max 1.0)
- **Lower MAPE**: Better percentage accuracy

## ✅ Success Checklist

- [ ] GEE authenticated
- [ ] Data fetched for all pollutants
- [ ] Models trained successfully
- [ ] Visualizations generated
- [ ] Spatial maps created
- [ ] Summary report available
- [ ] No critical errors

## 🔄 Workflow Summary

1. **Setup**: Install dependencies, authenticate GEE
2. **Configure**: Adjust settings in config.py
3. **Execute**: Run complete_analysis.py or notebook
4. **Review**: Check outputs/ directory
5. **Explore**: Open HTML maps in browser
6. **Analyze**: Review metrics and predictions
7. **Iterate**: Adjust parameters and rerun

## 📧 Support

For detailed execution instructions, see **EXECUTION_PLAN.md**.

## 🌍 Data Source

- **Google Earth Engine**: Sentinel-5P satellite data
- **Pollutants**: SO2, NO2, CO, Aerosol Index
- **Coverage**: Delhi-NCR region
- **Resolution**: Configurable (100m - 5000m per pixel)
- **Temporal**: Daily to monthly aggregation

## 🎉 What Makes This Special

1. **Fully Automated**: Processes ALL pollutants automatically
2. **Spatial Visualization**: Geographical maps with pixel-level precision
3. **Multiple Models**: 5 ML models for robust predictions
4. **Time Evolution**: Track changes over time
5. **Interactive**: Explore maps, toggle layers
6. **Configurable**: Adjust resolution for speed vs detail
7. **Complete Pipeline**: From data fetch to final maps
8. **Production Ready**: Saves all outputs, generates reports

---

**Ready to analyze Delhi-NCR air quality with spatial precision!** 🚀
