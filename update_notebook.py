"""
Script to add spatial mapping and complete analysis cells to the notebook
"""

import nbformat as nbf

# Read existing notebook
with open('analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# New cells to add at the end
new_cells = []

# Cell 1: Import complete analysis
cell1 = nbf.v4.new_code_cell("""# Import Complete Analysis Module
from complete_analysis import CompleteAnalysis
from spatial_mapper import SpatialMapper
from config import SPATIAL_MAP_CONFIG

print("✅ Complete analysis module imported")""")
new_cells.append(cell1)

# Cell 2: Run complete analysis
cell2 = nbf.v4.new_markdown_cell("""## 🗺️ Complete Analysis with Spatial Mapping

This section runs the complete analysis pipeline for **ALL pollutants**:
- Fetches data for all active pollutants (SO2, NO2, CO, Aerosol)
- Trains all enabled ML models
- Generates predictions and forecasts
- Creates visualizations for each pollutant
- Generates geographical color-coded maps (**HTML and Static PNG**)
- Saves all outputs with time evolution

**Pixel Density Control:**
- `ultra_high` (100m): Very detailed, slow processing
- `high` (500m): Detailed
- `medium` (1000m): Balanced (default)
- `low` (2000m): Faster processing
- `ultra_low` (5000m): Very fast, less detail""")
new_cells.append(cell2)

# Cell 3: Configure and run
cell3 = nbf.v4.new_code_cell("""# Configure Analysis
analysis = CompleteAnalysis()

# Optional: Adjust pixel density for spatial maps
# analysis.mapper.set_pixel_density(SPATIAL_MAP_CONFIG['pixel_density_presets']['high'])

print("Starting complete analysis for all pollutants...")
print("This will:")
print("  1. Fetch data for all active pollutants")
print("  2. Train all enabled ML models")
print("  3. Generate predictions and forecasts")
print("  4. Create time series visualizations")
print("  5. Generate geographical maps showing pollutant evolution")
print("  6. Save all outputs")
print("\\nThis may take several minutes...\\n")

# Run complete analysis
results = analysis.run_complete_analysis()""")
new_cells.append(cell3)

# Cell 4: Display results summary
cell4 = nbf.v4.new_code_cell("""# Display Results Summary
print("=" * 70)
print("ANALYSIS RESULTS SUMMARY")
print("=" * 70)

for pollutant, result in results.items():
    print(f"\\n{pollutant}:")
    print(f"  Models trained: {len(result['models'])}")
    print(f"  Visualizations created: {len(result['plots'])}")
    print(f"  Spatial maps created: {len(result['maps'])}")
    
    if result['metrics']:
        print(f"\\n  Best Model Performance:")
        best_model = min(result['metrics'].items(), 
                        key=lambda x: x[1].get('RMSE', float('inf')))
        print(f"    Model: {best_model[0]}")
        for metric, value in best_model[1].items():
            print(f"    {metric}: {value:.6f}")

print(f"\\n📁 All outputs saved in:")
for name, path in analysis.output_dirs.items():
    print(f"   {name}: {path}/")""")
new_cells.append(cell4)

# Cell 5: View spatial maps
cell5 = nbf.v4.new_markdown_cell("""## 📍 View Spatial Maps

The geographical maps have been created in the `outputs/maps/` directory.

Each map shows:
- **Color-coded pollutant density** across Delhi-NCR
- **Region boundary** in red
- **Colorbar legend** showing concentration levels
- **Interactive layers** (for multi-pollutant maps)

To view a map, open the HTML file in your browser.""")
new_cells.append(cell5)

# Cell 6: Create custom maps
cell6 = nbf.v4.new_code_cell("""# Create Custom Spatial Maps

# Example: Create map for specific pollutant and date
from spatial_mapper import quick_map

# Create single pollutant map
m = quick_map(
    pollutant='NO2',
    date='2022-06-01',
    region='Delhi',
    pixel_density=1000  # Adjust for detail level
)

print("✅ Custom map created in outputs/maps/")

# Example: Create time series of maps
# Uncomment to create monthly evolution maps:
'''
mapper = analysis.mapper
maps = mapper.create_time_series_maps(
    pollutant_name='NO2',
    start_date='2022-01-01',
    end_date='2022-12-31',
    interval_days=30  # One map per month
)
print(f"✅ Created {len(maps)} time evolution maps")
'''""")
new_cells.append(cell6)

# Cell 7: Export high-res images
cell7 = nbf.v4.new_code_cell("""# Export High-Resolution GeoTIFF Images

# Export to Google Drive for GIS analysis
# Uncomment to export:
'''
for pollutant in ACTIVE_POLLUTANTS:
    task = analysis.mapper.export_high_res_image(
        pollutant_name=pollutant,
        date_str='2022-06-01'
    )
    print(f"Export task started for {pollutant}")

print("\\nCheck your Google Drive 'GEE_Exports' folder for GeoTIFF files")
'''""")
new_cells.append(cell7)

# Cell 8: Pixel density comparison
cell8 = nbf.v4.new_markdown_cell("""## 🔬 Understanding Pixel Density

**Pixel density** controls the resolution of spatial maps:

| Preset | Meters/Pixel | Detail Level | Processing Speed | Use Case |
|--------|--------------|--------------|------------------|----------|
| ultra_high | 100m | Very High | Slow | Detailed analysis |
| high | 500m | High | Moderate | Research |
| **medium** | **1000m** | **Balanced** | **Fast** | **Default** |
| low | 2000m | Low | Very Fast | Quick overview |
| ultra_low | 5000m | Very Low | Fastest | Regional view |

**Trade-offs:**
- Lower pixel density = More detail but slower data fetching
- Higher pixel density = Less detail but faster processing
- Data volume increases exponentially with higher resolution""")
new_cells.append(cell8)

# Cell 9: Next steps
cell9 = nbf.v4.new_markdown_cell("""## 📊 Next Steps

Your complete analysis is done! Here's what you have:

### Outputs Generated:
1. **Data**: `data/` - Raw and processed data
2. **Models**: `outputs/models/` - Trained model files
3. **Plots**: `outputs/plots/` - Time series and prediction charts
4. **Maps**: `outputs/maps/` - Interactive geographical maps
5. **Predictions**: `outputs/predictions/` - Forecast data and metrics
6. **Reports**: `outputs/reports/` - Summary reports

### To Explore Results:
- Open HTML maps in `outputs/maps/` to see pollutant distribution
- Check prediction accuracy in `outputs/predictions/*_metrics.json`
- View time series evolution in `outputs/plots/`
- Read summary in `outputs/reports/analysis_summary.txt`

### To Rerun with Different Settings:
- Adjust pixel density in config.py
- Enable/disable models in MODEL_CONFIG
- Change date ranges in config.py
- Modify ACTIVE_POLLUTANTS list""")
new_cells.append(cell9)

# Add all new cells to notebook
nb.cells.extend(new_cells)

# Save updated notebook
with open('analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("✅ Notebook updated with spatial mapping and complete analysis cells")
print(f"   Added {len(new_cells)} new cells")
print("   Cells added at the end of the notebook")
