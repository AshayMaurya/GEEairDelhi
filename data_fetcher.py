"""
Data Fetcher Module for Google Earth Engine
Handles authentication and data extraction from GEE
"""

import ee
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import time

class GEEDataFetcher:
    """Fetch air quality data from Google Earth Engine"""
    
    def __init__(self, region_config: Dict, gee_config: Dict):
        """
        Initialize GEE Data Fetcher
        
        Args:
            region_config: Dictionary with region configuration
            gee_config: Dictionary with GEE configuration
        """
        self.region_config = region_config
        self.gee_config = gee_config
        self.region = None
        self.is_initialized = False
        
    def authenticate_and_initialize(self, project_id: Optional[str] = None):
        """
        Authenticate and initialize Google Earth Engine
        
        Args:
            project_id: Optional GEE project ID
        """
        try:
            # Try to initialize (will use cached credentials if available)
            if project_id:
                ee.Initialize(project=project_id)
            else:
                ee.Initialize()
            
            self.is_initialized = True
            print("✅ Google Earth Engine initialized successfully!")
            
        except Exception as e:
            print("⚠️  Authentication required. Starting authentication process...")
            try:
                # Authenticate if initialization fails
                ee.Authenticate()
                
                # Initialize after authentication
                if project_id:
                    ee.Initialize(project=project_id)
                else:
                    ee.Initialize()
                
                self.is_initialized = True
                print("✅ Google Earth Engine authenticated and initialized!")
                
            except Exception as auth_error:
                print(f"❌ Failed to authenticate: {auth_error}")
                raise
    
    def load_region(self):
        """Load the region of interest from GEE"""
        if not self.is_initialized:
            raise RuntimeError("GEE not initialized. Call authenticate_and_initialize() first.")
        
        try:
            # Load administrative boundaries
            region_name = self.region_config['name']
            admin_level = self.region_config['admin_level']
            
            self.region = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(
                ee.Filter.eq(admin_level, region_name)
            )
            
            print(f"✅ Loaded region: {region_name}")
            return self.region
            
        except Exception as e:
            print(f"❌ Failed to load region: {e}")
            raise
    
    def fetch_pollutant_timeseries(
        self,
        pollutant_name: str,
        pollutant_config: Dict,
        start_date: str,
        end_date: str,
        scale: int = 1000,
        reducer: str = 'median',
        temporal_resolution: str = 'monthly'  # 'daily' or 'monthly'
    ) -> pd.DataFrame:
        """
        Fetch time-series data for a specific pollutant
        
        Args:
            pollutant_name: Name of the pollutant (e.g., 'SO2', 'NO2')
            pollutant_config: Configuration dictionary for the pollutant
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            scale: Spatial scale in meters
            reducer: Statistical reducer ('median', 'mean', 'max', 'min')
            temporal_resolution: 'daily' or 'monthly' aggregation
        
        Returns:
            DataFrame with date and pollutant values
        """
        if self.region is None:
            self.load_region()
        
        print(f"📡 Fetching {pollutant_name} data from {start_date} to {end_date} ({temporal_resolution})...")
        
        try:
            # Load image collection
            collection = ee.ImageCollection(pollutant_config['collection']) \
                .filterDate(start_date, end_date) \
                .select(pollutant_config['band']) \
                .filterBounds(self.region)
            
            # Get reducer function
            reducer_func = self._get_reducer(reducer)
            
            # Aggregate by month if needed to avoid 5000 element limit
            if temporal_resolution == 'monthly':
                data = self._fetch_monthly_aggregated(
                    collection, 
                    pollutant_config['band'],
                    pollutant_name,
                    start_date,
                    end_date,
                    reducer_func,
                    scale
                )
            else:
                # Daily data - use batching for large ranges
                data = self._fetch_daily_batched(
                    collection,
                    pollutant_config['band'],
                    pollutant_name,
                    start_date,
                    end_date,
                    reducer_func,
                    scale
                )
            
            df = pd.DataFrame(data)
            
            if len(df) > 0:
                df = df.sort_values('date').reset_index(drop=True)
                print(f"✅ Fetched {len(df)} records for {pollutant_name}")
            else:
                print(f"⚠️  No data found for {pollutant_name}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching {pollutant_name}: {e}")
            return pd.DataFrame()
    
    def _fetch_monthly_aggregated(
        self,
        collection,
        band_name: str,
        pollutant_name: str,
        start_date: str,
        end_date: str,
        reducer_func,
        scale: int
    ) -> List[Dict]:
        """Fetch data aggregated by month - optimized version"""
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        import gc
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        data = []
        current = start
        error_count = 0
        
        while current <= end:
            month_start = current.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - relativedelta(days=1)
            
            if month_end > end:
                month_end = end
            
            try:
                # Filter collection for this month
                month_collection = collection.filterDate(
                    month_start.strftime('%Y-%m-%d'),
                    (month_end + relativedelta(days=1)).strftime('%Y-%m-%d')
                )
                
                # Check if collection has images
                count = month_collection.size().getInfo()
                if count == 0:
                    continue
                
                # Get mean of all images in the month
                month_mean = month_collection.mean()
                
                # Extract value for the region
                stats = month_mean.reduceRegion(
                    reducer=reducer_func,
                    geometry=self.region,
                    scale=scale,
                    maxPixels=1e9
                )
                
                result = stats.getInfo()
                value = result.get(band_name)
                
                if value is not None:
                    data.append({
                        'date': month_start.date(),
                        pollutant_name: value
                    })
            
            except Exception as e:
                error_count += 1
                print(f"  ❌ Error at {month_start.strftime('%Y-%m')}: {str(e)[:50]}")
            
            # Move to next month
            current = month_start + relativedelta(months=1)
            
            # Clear memory periodically
            if len(data) % 12 == 0:
                gc.collect()
        
        if error_count > 0:
            print(f"  ⚠️  {error_count} months had errors")
        
        return data
    
    def _fetch_daily_batched(
        self,
        collection,
        band_name: str,
        pollutant_name: str,
        start_date: str,
        end_date: str,
        reducer_func,
        scale: int,
        batch_days: int = 90  # Fetch 90 days at a time
    ) -> List[Dict]:
        """Fetch daily data in batches to avoid 5000 element limit"""
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_data = []
        current = start
        
        while current <= end:
            batch_end = min(current + timedelta(days=batch_days), end)
            
            try:
                # Filter for this batch
                batch_collection = collection.filterDate(
                    current.strftime('%Y-%m-%d'),
                    (batch_end + timedelta(days=1)).strftime('%Y-%m-%d')
                )
                
                # Extract values
                def extract_value(image):
                    stats = image.reduceRegion(
                        reducer=reducer_func,
                        geometry=self.region,
                        scale=scale,
                        maxPixels=1e9
                    )
                    return ee.Feature(None, stats).set(
                        'system:time_start', image.get('system:time_start')
                    )
                
                features = batch_collection.map(extract_value)
                feature_list = features.getInfo()['features']
                
                # Parse features
                for feature in feature_list:
                    props = feature['properties']
                    timestamp = props.get('system:time_start')
                    value = props.get(band_name)
                    
                    if timestamp and value is not None:
                        date = datetime.fromtimestamp(timestamp / 1000)
                        all_data.append({
                            'date': date.date(),
                            pollutant_name: value
                        })
                
                print(f"  ✓ Batch {current.strftime('%Y-%m-%d')} to {batch_end.strftime('%Y-%m-%d')}: {len(feature_list)} records")
                
            except Exception as e:
                print(f"  ⚠️  Batch failed {current.strftime('%Y-%m-%d')}: {e}")
            
            current = batch_end + timedelta(days=1)
            time.sleep(0.5)  # Rate limiting
        
        return all_data
    
    def fetch_all_pollutants(
        self,
        pollutants_config: Dict,
        active_pollutants: List[str],
        start_date: str,
        end_date: str,
        scale: int = 1000,
        reducer: str = 'median',
        temporal_resolution: str = 'monthly',
        use_polars: bool = True,
        parallel: bool = True
    ) -> pd.DataFrame:
        """
        Fetch data for all active pollutants - optimized with parallelism
        
        Args:
            pollutants_config: Dictionary with all pollutant configurations
            active_pollutants: List of pollutant names to fetch
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            scale: Spatial scale in meters
            reducer: Statistical reducer to use
            temporal_resolution: 'daily' or 'monthly' aggregation
            use_polars: Use Polars for faster processing
            parallel: Fetch pollutants in parallel
        
        Returns:
            DataFrame with all pollutants
        """
        import gc
        
        if parallel:
            # Parallel fetching
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            all_data = None
            completed = 0
            total = len(active_pollutants)
            
            def fetch_single(pollutant_name):
                """Fetch single pollutant"""
                if pollutant_name not in pollutants_config:
                    return None
                
                pollutant_config = pollutants_config[pollutant_name]
                
                df = self.fetch_pollutant_timeseries(
                    pollutant_name=pollutant_name,
                    pollutant_config=pollutant_config,
                    start_date=start_date,
                    end_date=end_date,
                    scale=scale,
                    reducer=reducer,
                    temporal_resolution=temporal_resolution
                )
                
                return (pollutant_name, df)
            
            # Use ThreadPoolExecutor for parallel fetching
            with ThreadPoolExecutor(max_workers=min(4, total)) as executor:
                futures = {executor.submit(fetch_single, p): p for p in active_pollutants}
                
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        pollutant_name, df = result
                        completed += 1
                        
                        if df is not None and not df.empty:
                            if all_data is None:
                                all_data = df
                            else:
                                all_data = pd.merge(all_data, df, on='date', how='outer')
                            
                            print(f"  ✅ {pollutant_name} complete ({completed}/{total})")
                        
                        # Clear memory
                        del df
                        gc.collect()
        
        else:
            # Sequential fetching (original method)
            all_data = None
            
            for pollutant_name in active_pollutants:
                if pollutant_name not in pollutants_config:
                    print(f"⚠️  Skipping {pollutant_name}: not in configuration")
                    continue
                
                pollutant_config = pollutants_config[pollutant_name]
                
                df = self.fetch_pollutant_timeseries(
                    pollutant_name=pollutant_name,
                    pollutant_config=pollutant_config,
                    start_date=start_date,
                    end_date=end_date,
                    scale=scale,
                    reducer=reducer,
                    temporal_resolution=temporal_resolution
                )
                
                if df.empty:
                    continue
                
                if all_data is None:
                    all_data = df
                else:
                    all_data = pd.merge(all_data, df, on='date', how='outer')
                
                time.sleep(0.5)
        
        if all_data is not None:
            all_data = all_data.sort_values('date').reset_index(drop=True)
            
            # Convert to Polars if requested
            if use_polars:
                try:
                    import polars as pl
                    all_data = pl.from_pandas(all_data)
                    print(f"\n✅ Data converted to Polars DataFrame for faster processing")
                except ImportError:
                    print(f"\n⚠️  Polars not available, using Pandas")
            
            print(f"\n📊 Final dataset:")
            print(f"  Records: {len(all_data)}")
            print(f"  Date range: {all_data['date'].min()} to {all_data['date'].max()}")
            
            if use_polars and isinstance(all_data, pl.DataFrame):
                print(f"  Pollutants: {', '.join([col for col in all_data.columns if col != 'date'])}")
            else:
                print(f"  Pollutants: {', '.join([col for col in all_data.columns if col != 'date'])}")
        
        return all_data
    
    def get_spatial_image(
        self,
        pollutant_name: str,
        pollutant_config: Dict,
        start_date: str,
        end_date: str,
        reducer: str = 'median'
    ) -> ee.Image:
        """
        Get spatial image for visualization
        
        Args:
            pollutant_name: Name of the pollutant
            pollutant_config: Configuration dictionary for the pollutant
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            reducer: Statistical reducer to use
        
        Returns:
            Earth Engine Image object
        """
        if self.region is None:
            self.load_region()
        
        # Load and reduce collection
        collection = ee.ImageCollection(pollutant_config['collection']) \
            .filterDate(start_date, end_date) \
            .select(pollutant_config['band']) \
            .filterBounds(self.region)
        
        # Apply reducer
        reducer_func = self._get_reducer(reducer)
        image = collection.reduce(reducer_func).clip(self.region)
        
        return image
    
    def _get_reducer(self, reducer: str):
        """Get EE reducer function"""
        reducers = {
            'median': ee.Reducer.median(),
            'mean': ee.Reducer.mean(),
            'max': ee.Reducer.max(),
            'min': ee.Reducer.min(),
            'stdDev': ee.Reducer.stdDev()
        }
        return reducers.get(reducer, ee.Reducer.median())
    
    def export_to_csv(self, df: pd.DataFrame, filename: str):
        """Export DataFrame to CSV"""
        df.to_csv(filename, index=False)
        print(f"💾 Data saved to {filename}")
    
    def get_region_geometry(self):
        """Get region geometry for visualization"""
        if self.region is None:
            self.load_region()
        return self.region.geometry()


# Convenience functions
def quick_fetch(
    pollutants: List[str],
    start_date: str,
    end_date: str,
    region_name: str = 'Delhi',
    scale: int = 1000
) -> pd.DataFrame:
    """
    Quick fetch function for common use cases
    
    Args:
        pollutants: List of pollutant names
        start_date: Start date
        end_date: End date
        region_name: Name of region
        scale: Spatial scale
    
    Returns:
        DataFrame with pollutant data
    """
    from config import REGION_CONFIG, POLLUTANTS, GEE_CONFIG
    
    # Update region name if different
    region_config = REGION_CONFIG.copy()
    region_config['name'] = region_name
    
    # Initialize fetcher
    fetcher = GEEDataFetcher(region_config, GEE_CONFIG)
    fetcher.authenticate_and_initialize()
    
    # Fetch data
    df = fetcher.fetch_all_pollutants(
        pollutants_config=POLLUTANTS,
        active_pollutants=pollutants,
        start_date=start_date,
        end_date=end_date,
        scale=scale
    )
    
    return df


if __name__ == "__main__":
    # Example usage
    from config import REGION_CONFIG, POLLUTANTS, ACTIVE_POLLUTANTS, GEE_CONFIG
    
    fetcher = GEEDataFetcher(REGION_CONFIG, GEE_CONFIG)
    fetcher.authenticate_and_initialize()
    
    # Fetch sample data
    df = fetcher.fetch_all_pollutants(
        pollutants_config=POLLUTANTS,
        active_pollutants=ACTIVE_POLLUTANTS[:2],  # Just first 2 pollutants for testing
        start_date='2023-01-01',
        end_date='2023-01-31',
        scale=1000
    )
    
    print("\nSample data:")
    print(df.head())
