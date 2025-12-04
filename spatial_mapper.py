import ee
import folium
from folium import plugins
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import os
import requests
import shutil

# Global variable for pixel density control
PIXEL_DENSITY = 1000  # meters per pixel (can be adjusted: 100-5000)

class SpatialMapper:
    """
    Creates geographical color-coded maps for pollutant visualization
    """
    
    def __init__(self, fetcher, region_config, pollutants_config):
        """
        Initialize Spatial Mapper
        
        Args:
            fetcher: GEEDataFetcher instance
            region_config: Region configuration dictionary
            pollutants_config: Pollutants configuration dictionary
        """
        self.fetcher = fetcher
        self.region_config = region_config
        self.pollutants_config = pollutants_config
        self.region = fetcher.region
        
    def set_pixel_density(self, density):
        """
        Set global pixel density for data fetching
        
        Args:
            density: Pixel size in meters (100-5000)
        """
        global PIXEL_DENSITY
        PIXEL_DENSITY = density
        print(f"✅ Pixel density set to {density}m per pixel")
        
    def get_pixel_density(self):
        """Get current pixel density setting"""
        return PIXEL_DENSITY
    
    def create_pollutant_map(self, pollutant_name, date_str, 
                            predictions=None, output_dir='outputs/maps'):
        """
        Create color-coded map for a specific pollutant and date
        
        Args:
            pollutant_name: Name of pollutant (SO2, NO2, CO, Aerosol)
            date_str: Date in 'YYYY-MM-DD' format
            predictions: Optional predicted values dictionary
            output_dir: Directory to save maps
            
        Returns:
            Folium map object
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if pollutant_name not in self.pollutants_config:
            raise ValueError(f"Unknown pollutant: {pollutant_name}")
            
        config = self.pollutants_config[pollutant_name]
        
        # Get the image for this date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"📍 Creating map for {pollutant_name} on {date_str}")
        print(f"   Pixel density: {PIXEL_DENSITY}m")
        
        # Load image collection
        collection = ee.ImageCollection(config['collection']) \
            .filterDate(date_str, end_date) \
            .select(config['band']) \
            .filterBounds(self.region)
        
        # Get mean image
        image = collection.mean().clip(self.region.geometry())
        
        # Create base map
        center = self.region_config['center_coords'][::-1]  # [lat, lon]
        m = folium.Map(
            location=center,
            zoom_start=self.region_config['zoom_level'],
            tiles='OpenStreetMap'
        )
        
        # Add region boundary
        self._add_region_boundary(m)
        
        # Get visualization parameters
        vis_params = config['vis_params'].copy()
        vis_params['palette'] = ','.join(config['palette'])
        
        # Add the pollutant layer
        map_id = image.getMapId(vis_params)
        
        folium.TileLayer(
            tiles=map_id['tile_fetcher'].url_format,
            attr='Google Earth Engine',
            name=f'{pollutant_name} - {date_str}',
            overlay=True,
            control=True,
            opacity=0.7
        ).add_to(m)
        
        # Add colorbar
        self._add_colorbar(m, config, pollutant_name)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add title
        title_html = f'''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 400px; height: 60px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; padding: 10px">
            <b>{pollutant_name} Concentration</b><br>
            Date: {date_str}<br>
            Pixel Density: {PIXEL_DENSITY}m
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        filename = f"{output_dir}/{pollutant_name}_{date_str.replace('-', '')}.html"
        m.save(filename)
        print(f"💾 Map saved to {filename}")
        
        return m

    def create_static_map(self, pollutant_name, date_str, output_dir='outputs/maps'):
        """
        Create and save a static PNG map for a specific pollutant and date
        
        Args:
            pollutant_name: Name of pollutant
            date_str: Date in 'YYYY-MM-DD' format
            output_dir: Directory to save maps
            
        Returns:
            Filename of the saved image
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if pollutant_name not in self.pollutants_config:
            raise ValueError(f"Unknown pollutant: {pollutant_name}")
            
        config = self.pollutants_config[pollutant_name]
        
        # Get the image for this date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"📍 Creating static map for {pollutant_name} on {date_str}")
        
        # Load image collection
        collection = ee.ImageCollection(config['collection']) \
            .filterDate(date_str, end_date) \
            .select(config['band']) \
            .filterBounds(self.region)
        
        # Get mean image
        image = collection.mean().clip(self.region.geometry())
        
        # Get visualization parameters
        vis_params = config['vis_params'].copy()
        vis_params['palette'] = config['palette']
        vis_params['region'] = self.region.geometry().getInfo()
        vis_params['dimensions'] = 800  # Width in pixels
        
        try:
            # Get thumbnail URL
            thumb_url = image.getThumbURL(vis_params)
            
            # Download image
            response = requests.get(thumb_url, stream=True)
            if response.status_code == 200:
                filename = f"{output_dir}/{pollutant_name}_{date_str.replace('-', '')}.png"
                with open(filename, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
                print(f"💾 Static map saved to {filename}")
                return filename
            else:
                print(f"⚠️  Failed to download static map: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  Error creating static map: {e}")
            return None
    
    def create_time_series_maps(self, pollutant_name, start_date, end_date,
                               interval_days=30, output_dir='outputs/maps'):
        """
        Create series of maps showing pollutant evolution over time
        
        Args:
            pollutant_name: Name of pollutant
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            interval_days: Days between each map
            output_dir: Output directory
            
        Returns:
            List of map filenames
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current = start
        maps = []
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            try:
                m = self.create_pollutant_map(
                    pollutant_name, 
                    date_str, 
                    output_dir=output_dir
                )
                maps.append(date_str)
            except Exception as e:
                print(f"⚠️  Error creating map for {date_str}: {e}")
            
            current += timedelta(days=interval_days)
        
        print(f"\n✅ Created {len(maps)} maps for {pollutant_name}")
        return maps
    
    def create_multi_pollutant_map(self, date_str, pollutant_names=None,
                                  output_dir='outputs/maps'):
        """
        Create map with multiple pollutant layers
        
        Args:
            date_str: Date in 'YYYY-MM-DD' format
            pollutant_names: List of pollutants (default: all active)
            output_dir: Output directory
            
        Returns:
            Folium map object
        """
        if pollutant_names is None:
            pollutant_names = list(self.pollutants_config.keys())
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create base map
        center = self.region_config['center_coords'][::-1]
        m = folium.Map(
            location=center,
            zoom_start=self.region_config['zoom_level'],
            tiles='OpenStreetMap'
        )
        
        # Add region boundary
        self._add_region_boundary(m)
        
        # Add each pollutant layer
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
        
        for pollutant_name in pollutant_names:
            if pollutant_name not in self.pollutants_config:
                continue
                
            config = self.pollutants_config[pollutant_name]
            
            # Load and process image
            collection = ee.ImageCollection(config['collection']) \
                .filterDate(date_str, end_date) \
                .select(config['band']) \
                .filterBounds(self.region)
            
            image = collection.mean().clip(self.region.geometry())
            
            # Visualization parameters
            vis_params = config['vis_params'].copy()
            vis_params['palette'] = ','.join(config['palette'])
            
            # Add layer
            map_id = image.getMapId(vis_params)
            
            folium.TileLayer(
                tiles=map_id['tile_fetcher'].url_format,
                attr='Google Earth Engine',
                name=pollutant_name,
                overlay=True,
                control=True,
                opacity=0.6,
                show=False  # Start with layers hidden
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add title
        title_html = f'''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 400px; height: 60px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; padding: 10px">
            <b>Multi-Pollutant View</b><br>
            Date: {date_str}<br>
            Pixel Density: {PIXEL_DENSITY}m
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save
        filename = f"{output_dir}/multi_pollutant_{date_str.replace('-', '')}.html"
        m.save(filename)
        print(f"💾 Multi-pollutant map saved to {filename}")
        
        return m
    
    def create_prediction_comparison_map(self, pollutant_name, date_str,
                                        predicted_value, output_dir='outputs/maps'):
        """
        Create side-by-side comparison of actual vs predicted
        
        Args:
            pollutant_name: Pollutant name
            date_str: Date string
            predicted_value: Predicted concentration value
            output_dir: Output directory
        """
        # This would create a comparison visualization
        # Implementation depends on how predictions are structured
        pass
    
    def _add_region_boundary(self, map_obj):
        """Add region boundary to map"""
        try:
            # Get region geometry
            geom = self.region.geometry()
            coords = geom.getInfo()['coordinates']
            
            # Add to map
            folium.GeoJson(
                coords,
                name='Region Boundary',
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'red',
                    'weight': 2
                }
            ).add_to(map_obj)
        except Exception as e:
            print(f"⚠️  Could not add region boundary: {e}")
    
    def _add_colorbar(self, map_obj, config, pollutant_name):
        """Add colorbar legend to map"""
        # Create colormap
        colors = config['palette']
        n_colors = len(colors)
        
        # Create HTML colorbar
        colorbar_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px">
            <b>{pollutant_name}</b><br>
            <div style="background: linear-gradient(to right, {','.join(colors)}); 
                        height: 20px; margin: 5px 0;"></div>
            <div style="display: flex; justify-content: space-between;">
                <span>{config['vis_params']['min']}</span>
                <span>{config['vis_params']['max']}</span>
            </div>
            <div style="text-align: center; margin-top: 5px;">
                {config['unit']}
            </div>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(colorbar_html))
    
    def export_high_res_image(self, pollutant_name, date_str, 
                             output_dir='outputs/maps'):
        """
        Export high-resolution GeoTIFF image
        
        Args:
            pollutant_name: Pollutant name
            date_str: Date string
            output_dir: Output directory
        """
        config = self.pollutants_config[pollutant_name]
        
        # Get image
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
        
        collection = ee.ImageCollection(config['collection']) \
            .filterDate(date_str, end_date) \
            .select(config['band']) \
            .filterBounds(self.region)
        
        image = collection.mean().clip(self.region.geometry())
        
        # Export task
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=f'{pollutant_name}_{date_str}',
            folder='GEE_Exports',
            fileNamePrefix=f'{pollutant_name}_{date_str}',
            scale=PIXEL_DENSITY,
            region=self.region.geometry(),
            maxPixels=1e13
        )
        
        task.start()
        print(f"📤 Export task started for {pollutant_name} on {date_str}")
        print(f"   Check Google Drive folder 'GEE_Exports'")
        
        return task


# Convenience function
def quick_map(pollutant, date, region='Delhi', pixel_density=1000):
    """
    Quick function to create a single pollutant map
    
    Args:
        pollutant: Pollutant name
        date: Date string 'YYYY-MM-DD'
        region: Region name
        pixel_density: Pixel size in meters
    
    Returns:
        Folium map object
    """
    from config import REGION_CONFIG, POLLUTANTS, GEE_CONFIG
    from data_fetcher import GEEDataFetcher
    
    # Update region if needed
    region_config = REGION_CONFIG.copy()
    region_config['name'] = region
    
    # Initialize
    fetcher = GEEDataFetcher(region_config, GEE_CONFIG)
    fetcher.authenticate_and_initialize()
    
    mapper = SpatialMapper(fetcher, region_config, POLLUTANTS)
    mapper.set_pixel_density(pixel_density)
    
    return mapper.create_pollutant_map(pollutant, date)


if __name__ == "__main__":
    # Example usage
    from config import REGION_CONFIG, POLLUTANTS, ACTIVE_POLLUTANTS, GEE_CONFIG
    from data_fetcher import GEEDataFetcher
    
    # Initialize
    fetcher = GEEDataFetcher(REGION_CONFIG, GEE_CONFIG)
    fetcher.authenticate_and_initialize()
    
    mapper = SpatialMapper(fetcher, REGION_CONFIG, POLLUTANTS)
    
    # Set pixel density (adjust for performance vs detail)
    mapper.set_pixel_density(1000)  # 1km per pixel
    
    # Create single map
    m = mapper.create_pollutant_map('NO2', '2022-01-01')
    
    # Create time series
    # mapper.create_time_series_maps('NO2', '2022-01-01', '2022-12-31', interval_days=30)
    
    # Create multi-pollutant map
    # mapper.create_multi_pollutant_map('2022-06-01', ACTIVE_POLLUTANTS)
