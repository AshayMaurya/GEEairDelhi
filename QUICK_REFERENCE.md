# Quick Reference Guide

## 🚀 Getting Started (3 Steps)

```bash
# Step 1: Clean up
python cleanup_project.py

# Step 2: Update notebook  
python update_notebook.py

# Step 3: Run analysis
python complete_analysis.py
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `complete_analysis.py` | Main analysis pipeline - processes ALL pollutants |
| `spatial_mapper.py` | Geographical mapping with pixel control |
| `config.py` | All configuration settings |
| `analysis.ipynb` | Jupyter notebook (recommended) |
| `EXECUTION_PLAN.md` | Detailed instructions |
| `README.md` | Complete documentation |

## ⚙️ Quick Configuration

### Change Pixel Density
```python
# In config.py
SPATIAL_MAP_CONFIG = {
    'default_pixel_density': 1000,  # Change this: 100-5000
}
```

### Select Pollutants
```python
# In config.py
ACTIVE_POLLUTANTS = ['SO2', 'NO2', 'CO', 'Aerosol']  # Edit list
```

### Enable/Disable Models
```python
# In config.py, MODEL_CONFIG section
'ARIMA': {'enabled': True, ...},      # Set to False to disable
'Prophet': {'enabled': True, ...},
'LSTM': {'enabled': True, ...},
'XGBoost': {'enabled': True, ...},
'RandomForest': {'enabled': True, ...}
```

## 🎛️ Pixel Density Presets

| Preset | Value | Speed | Detail | Use For |
|--------|-------|-------|--------|---------|
| ultra_high | 100m | ⭐ | ⭐⭐⭐⭐⭐ | Research |
| high | 500m | ⭐⭐ | ⭐⭐⭐⭐ | Analysis |
| **medium** | **1000m** | **⭐⭐⭐** | **⭐⭐⭐** | **Default** |
| low | 2000m | ⭐⭐⭐⭐ | ⭐⭐ | Quick view |
| ultra_low | 5000m | ⭐⭐⭐⭐⭐ | ⭐ | Overview |

## 📊 What Gets Generated

```
outputs/
├── maps/          # Interactive HTML maps (open in browser)
├── plots/         # PNG visualizations
├── predictions/   # JSON data and metrics
├── models/        # Saved model files
└── reports/       # Summary text reports
```

## 🗺️ Creating Maps

### Single Pollutant Map
```python
from spatial_mapper import quick_map

m = quick_map(
    pollutant='NO2',
    date='2022-06-01',
    pixel_density=1000
)
```

### Time Evolution Maps
```python
from complete_analysis import CompleteAnalysis

analysis = CompleteAnalysis()
analysis.initialize()

maps = analysis.mapper.create_time_series_maps(
    pollutant_name='NO2',
    start_date='2022-01-01',
    end_date='2022-12-31',
    interval_days=30  # Monthly maps
)
```

### Multi-Pollutant Map
```python
m = analysis.mapper.create_multi_pollutant_map(
    date_str='2022-06-01',
    pollutant_names=['NO2', 'SO2', 'CO']
)
```

## 🔧 Common Tasks

### Run for Single Pollutant
```python
from complete_analysis import CompleteAnalysis

analysis = CompleteAnalysis()
analysis.initialize()
raw_data = analysis.fetch_all_data()
results = analysis.analyze_pollutant('NO2', raw_data)
```

### Change Pixel Density On-the-Fly
```python
analysis = CompleteAnalysis()
analysis.mapper.set_pixel_density(500)  # High detail
results = analysis.run_complete_analysis()
```

### Export High-Res GeoTIFF
```python
task = analysis.mapper.export_high_res_image(
    pollutant_name='NO2',
    date_str='2022-06-01'
)
# Check Google Drive 'GEE_Exports' folder
```

## 🐛 Quick Troubleshooting

### GEE Authentication Error
```python
import ee
ee.Authenticate()
ee.Initialize()
```

### Slow Processing
- Increase pixel density to 2000 or 5000
- Use TEMPORAL_RESOLUTION = 'monthly'
- Disable LSTM model

### Memory Issues
- Increase pixel density
- Reduce date range
- Process fewer pollutants

### Maps Not Loading
- Check outputs/maps/ directory exists
- Open HTML files in modern browser
- Check console for JavaScript errors

## 📈 Understanding Output

### Metrics (Lower is Better)
- **MAE**: Average error
- **RMSE**: Error with penalty for large mistakes
- **MAPE**: Percentage error
- **R²**: Model fit (higher is better, max 1.0)

### Map Colors
- **Blue/Cyan**: Low concentration ✅
- **Green/Yellow**: Medium ⚠️
- **Orange/Red**: High ⚠️⚠️
- **Purple**: Very high ❌

## ⚡ Performance Tips

### For Speed
```python
# config.py
SPATIAL_MAP_CONFIG['default_pixel_density'] = 2000
TEMPORAL_RESOLUTION = 'monthly'
MODEL_CONFIG['LSTM']['enabled'] = False
```

### For Quality
```python
# config.py
SPATIAL_MAP_CONFIG['default_pixel_density'] = 500
TEMPORAL_RESOLUTION = 'daily'
# Enable all models
```

## 📋 Checklist

### Before Running
- [ ] GEE authenticated
- [ ] Config.py reviewed
- [ ] Pollutants selected
- [ ] Pixel density chosen

### After Running
- [ ] Check outputs/maps/ for HTML files
- [ ] Check outputs/plots/ for visualizations
- [ ] Check outputs/predictions/ for metrics
- [ ] Review outputs/reports/analysis_summary.txt

## 🎯 Common Use Cases

### Quick Overview
```python
# Use low pixel density for speed
analysis = CompleteAnalysis()
analysis.mapper.set_pixel_density(2000)
results = analysis.run_complete_analysis()
```

### Detailed Research
```python
# Use high pixel density for detail
analysis = CompleteAnalysis()
analysis.mapper.set_pixel_density(500)
results = analysis.run_complete_analysis()
```

### Single Pollutant Focus
```python
# Edit config.py
ACTIVE_POLLUTANTS = ['NO2']  # Only NO2

# Then run
python complete_analysis.py
```

## 📞 Need Help?

1. Check `EXECUTION_PLAN.md` for detailed instructions
2. Check `README.md` for complete documentation
3. Check `IMPLEMENTATION_SUMMARY.md` for feature overview
4. Review console output for error messages

## 🎉 Success Indicators

✅ Console shows "ANALYSIS COMPLETE!"
✅ outputs/maps/ contains HTML files
✅ outputs/plots/ contains PNG files
✅ outputs/predictions/ contains JSON files
✅ outputs/reports/analysis_summary.txt exists
✅ No critical errors in console

---

**You're ready to analyze Delhi-NCR air quality!** 🚀

Open `outputs/maps/*.html` in your browser to see the geographical visualizations!
