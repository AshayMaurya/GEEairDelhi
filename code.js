// Get the layer for the city
var delhi = ee.FeatureCollection("FAO/GAUL/2015/level1")
    .filter(ee.Filter.or(
        ee.Filter.eq('ADM1_NAME', 'Delhi')));
Map.addLayer(delhi);
Map.centerObject(delhi, 7);

// Add image collection with filters for the year 2019 - SO2
var y2019_SO2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_SO2")
  .filterDate("2019-04-01", "2019-04-30")
  .select('SO2_column_number_density')
  .filterBounds(delhi);

// Add image collection with filters for the year 2020 - SO2
var y2020_SO2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_SO2")
  .filterDate("2020-04-01", "2020-04-30")
  .select('SO2_column_number_density')
  .filterBounds(delhi);

// Add image collection with filters for the year 2019 - NO2
var y2019_NO2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
  .filterDate("2019-04-01", "2019-04-30")
  .select('NO2_column_number_density')
  .filterBounds(delhi);

// Add image collection with filters for the year 2020 - NO2
var y2020_NO2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
  .filterDate("2020-04-01", "2020-04-30")
  .select('NO2_column_number_density')
  .filterBounds(delhi);

// Add image collection with filters for the year 2019 - CO
var y2019_CO = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CO")
  .filterDate("2019-04-01", "2019-04-30")
  .select('CO_column_number_density')
  .filterBounds(delhi);

// Add image collection with filters for the year 2020 - CO
var y2020_CO = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CO")
  .filterDate("2020-04-01", "2020-04-30")
  .select('CO_column_number_density')
  .filterBounds(delhi);

// Add image collection with filters for the year 2019 - Aerosol
var y2019_Aerosol = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_AER_AI")
  .filterDate("2019-04-01", "2019-04-30")
  .select('absorbing_aerosol_index')
  .filterBounds(delhi);

// Add image collection with filters for the year 2020 - Aerosol
var y2020_Aerosol = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_AER_AI")
  .filterDate("2020-04-01", "2020-04-30")
  .select('absorbing_aerosol_index')
  .filterBounds(delhi);

// Air quality measurement station
var station = ee.Geometry.Point([77.2090, 28.6139]); // Coordinates for Delhi
Map.addLayer(station);

// Clip the city from SO2 layers
var y2019_SO2_clipped = y2019_SO2.median().clip(delhi);
var y2020_SO2_clipped = y2020_SO2.median().clip(delhi);

// Clip the city from NO2 layers
var y2019_NO2_clipped = y2019_NO2.median().clip(delhi);
var y2020_NO2_clipped = y2020_NO2.median().clip(delhi);

// Clip the city from CO layers
var y2019_CO_clipped = y2019_CO.median().clip(delhi);
var y2020_CO_clipped = y2020_CO.median().clip(delhi);

// Clip the city from Aerosol layers
var y2019_Aerosol_clipped = y2019_Aerosol.median().clip(delhi);
var y2020_Aerosol_clipped = y2020_Aerosol.median().clip(delhi);

// Add layers to the map
Map.addLayer(y2019_SO2_clipped, {min: 0, max: 0.001, palette: ['orange', 'yellow', 'green', 'cyan', 'purple', 'blue', 'white']}, "April 2019 - SO2");
Map.addLayer(y2020_SO2_clipped, {min: 0, max: 0.001, palette: ['orange', 'yellow', 'green', 'cyan', 'purple', 'blue', 'white']}, "April 2020 - SO2");

Map.addLayer(y2019_NO2_clipped, {min: 0, max: 0.0002, palette: ['orange', 'yellow', 'green', 'cyan', 'purple', 'blue', 'white']}, "April 2019 - NO2");
Map.addLayer(y2020_NO2_clipped, {min: 0, max: 0.0002, palette: ['orange', 'yellow', 'green', 'cyan', 'purple', 'blue', 'white']}, "April 2020 - NO2");

Map.addLayer(y2019_CO_clipped, {min: 0, max: 0.01, palette: ['orange', 'yellow', 'green', 'cyan', 'purple', 'blue', 'white']}, "April 2019 - CO");
Map.addLayer(y2020_CO_clipped, {min: 0, max: 0.01, palette: ['orange', 'yellow', 'green', 'cyan', 'purple', 'blue', 'white']}, "April 2020 - CO");

Map.addLayer(y2019_Aerosol_clipped, {min: -1, max: 1, palette: ['blue', 'white', 'red']}, "April 2019 - Aerosol");
Map.addLayer(y2020_Aerosol_clipped, {min: -1, max: 1, palette: ['blue', 'white', 'red']}, "April 2020 - Aerosol");

// Calculate median values for each date and region for all pollutants
var feats2019_SO2 = y2019_SO2.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

var feats2020_SO2 = y2020_SO2.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

var feats2019_NO2 = y2019_NO2.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

var feats2020_NO2 = y2020_NO2.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

var feats2019_CO = y2019_CO.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

var feats2020_CO = y2020_CO.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

var feats2019_Aerosol = y2019_Aerosol.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

var feats2020_Aerosol = y2020_Aerosol.map(function(image) {
  var reducer = ee.Reducer.median();
  var stats = image.reduceRegion(reducer, delhi, 1000);
  return ee.Feature(null, stats).set('system:time_start', image.get('system:time_start'));
});

// Plot the feature collections for SO2
var chart2019_SO2 = ui.Chart.feature.byFeature(feats2019_SO2, 'system:time_start')
  .setSeriesNames(['SO2 median for April 2019'])
  .setOptions({
    title: 'Median SO2 Values for April 2019',
    hAxis: {title: 'Date'},
    vAxis: {title: 'SO2 Median'}
  });

var chart2020_SO2 = ui.Chart.feature.byFeature(feats2020_SO2, 'system:time_start')
  .setSeriesNames(['SO2 median for April 2020'])
  .setOptions({
    title: 'Median SO2 Values for April 2020',
    hAxis: {title: 'Date'},
    vAxis: {title: 'SO2 Median'}
  });

// Plot the feature collections for NO2
var chart2019_NO2 = ui.Chart.feature.byFeature(feats2019_NO2, 'system:time_start')
  .setSeriesNames(['NO2 median for April 2019'])
  .setOptions({
    title: 'Median NO2 Values for April 2019',
    hAxis: {title: 'Date'},
    vAxis: {title: 'NO2 Median'}
  });

var chart2020_NO2 = ui.Chart.feature.byFeature(feats2020_NO2, 'system:time_start')
  .setSeriesNames(['NO2 median for April 2020'])
  .setOptions({
    title: 'Median NO2 Values for April 2020',
    hAxis: {title: 'Date'},
    vAxis: {title: 'NO2 Median'}
  });

// Plot the feature collections for CO
var chart2019_CO = ui.Chart.feature.byFeature(feats2019_CO, 'system:time_start')
  .setSeriesNames(['CO median for April 2019'])
  .setOptions({
    title: 'Median CO Values for April 2019',
    hAxis: {title: 'Date'},
    vAxis: {title: 'CO Median'}
  });

var chart2020_CO = ui.Chart.feature.byFeature(feats2020_CO, 'system:time_start')
  .setSeriesNames(['CO median for April 2020'])
  .setOptions({
    title: 'Median CO Values for April 2020',
    hAxis: {title: 'Date'},
    vAxis: {title: 'CO Median'}
  });

// Plot the feature collections for aerosols
var chart2019_Aerosol = ui.Chart.feature.byFeature(feats2019_Aerosol, 'system:time_start')
  .setSeriesNames(['Aerosol median for April 2019'])
  .setOptions({
    title: 'Median Aerosol Values for April 2019',
    hAxis: {title: 'Date'},
    vAxis: {title: 'Aerosol Median'}
  });

var chart2020_Aerosol = ui.Chart.feature.byFeature(feats2020_Aerosol, 'system:time_start')
  .setSeriesNames(['Aerosol median for April 2020'])
  .setOptions({
    title: 'Median Aerosol Values for April 2020',
    hAxis: {title: 'Date'},
    vAxis: {title: 'Aerosol Median'}
  });

//---------------------------------------------------
Map.addLayer(y2019_SO2_clipped, {min: 0, max: 0.001, palette: ['yellow', 'orange', 'red', 'purple', 'blue', 'cyan', 'white']}, "April 2019 - SO2");
Map.addLayer(y2020_SO2_clipped, {min: 0, max: 0.001, palette: ['yellow', 'orange', 'red', 'purple', 'blue', 'cyan', 'white']}, "April 2020 - SO2");

Map.addLayer(y2019_NO2_clipped, {min: 0, max: 0.0002, palette: ['green', 'yellow', 'orange', 'red', 'purple', 'blue', 'white']}, "April 2019 - NO2");
Map.addLayer(y2020_NO2_clipped, {min: 0, max: 0.0002, palette: ['green', 'yellow', 'orange', 'red', 'purple', 'blue', 'white']}, "April 2020 - NO2");

Map.addLayer(y2019_CO_clipped, {min: 0, max: 0.01, palette: ['green', 'yellow', 'orange', 'red', 'purple', 'blue', 'white']}, "April 2019 - CO");
Map.addLayer(y2020_CO_clipped, {min: 0, max: 0.01, palette: ['green', 'yellow', 'orange', 'red', 'purple', 'blue', 'white']}, "April 2020 - CO");

Map.addLayer(y2019_Aerosol_clipped, {min: -1, max: 1, palette: ['blue', 'white', 'red']}, "April 2019 - Aerosol");
Map.addLayer(y2020_Aerosol_clipped, {min: -1, max: 1, palette: ['blue', 'white', 'red']}, "April 2020 - Aerosol");

//---------------------------------------------------
// Print the charts for SO2
print(chart2019_SO2, feats2019_SO2);
print(chart2020_SO2, feats2020_SO2);

// Print the charts for NO2
print(chart2019_NO2, feats2019_NO2);
print(chart2020_NO2, feats2020_NO2);

// Print the charts for CO
print(chart2019_CO, feats2019_CO);
print(chart2020_CO, feats2020_CO);

// Print the charts for aerosols
print(chart2019_Aerosol, feats2019_Aerosol);
print(chart2020_Aerosol, feats2020_Aerosol);
