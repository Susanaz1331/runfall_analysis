import datetime
from typing import List
import pandas as pd
import ee
import geopandas as gpd
from shapely.ops import unary_union
from pathlib import Path

from settings import DATA_FOLDER

def export_dem_to_drive(polygon_location_file: Path) -> None:
    nasadem = ee.Image('NASA/NASADEM_HGT/001')

    polygon_location = gpd.read_file(polygon_location_file)
    polygon_location = polygon_location.geometry.to_list()[0]
    merged_polygon = unary_union(polygon_location)
    coords = list(merged_polygon.exterior.coords)

    ee_polygon = ee.Geometry.Polygon(coords)

    # Select the band
    elevation = nasadem.select('elevation')

    clipped_dem = elevation.clip(ee_polygon)

    task = ee.batch.Export.image.toDrive(
        image=clipped_dem,
        description='NASA_DEM_Export',           # Task description
        folder='FieldFactorsProject',            # Drive folder name
        fileNamePrefix=f'nasa_dem_elevation_{polygon_location_file.name}',     # File name prefix
        scale=30,                               # Resolution in meters (NASADEM is 30m)
        region=ee_polygon,
        maxPixels=1e9,                         # Maximum pixel value to export
        crs='EPSG:4326',                       # Coordinate reference system
        fileFormat='GeoTIFF'
    )

    task.start()


def monthly_sum(year:str, month:str, ee_image_data, band:str)-> List[ee.image.Image]:
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, 'month')
    month_images = ee_image_data.filterDate(start, end)
    total_precip = month_images.select(band).sum().set({
        'year': year,
        'month': month,
        'date': start.format('YYYY-MM')
    })
    return total_precip


def compute_rainfall_statistics(polygon_location_file: Path):

    end_date = datetime.date.today()
    start_date = end_date.replace(year=end_date.year - 10)


    polygon_location = gpd.read_file(polygon_location_file)
    polygon_location = polygon_location.geometry.to_list()[0]
    merged_polygon = unary_union(polygon_location)
    coords = list(merged_polygon.exterior.coords)

    ee_polygon = ee.Geometry.Polygon(coords)

    rainfall_bounded = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
    .filterDate(str(start_date), str(end_date)) \
    .filterBounds(ee_polygon)

    dates = []
    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            if year == end_date.year and month > end_date.month:
                break
            dates.append((year, month))

    monthly_images = [monthly_sum(y, m, rainfall_bounded, band="precipitation") for (y, m) in dates]
    monthly_ic = ee.ImageCollection(monthly_images)


    def reduce_to_feature(img):
        buffered = ee_polygon.buffer(3000)

        stats = img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=buffered,
            scale=5566, # cf pixel size see https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY#bands
            maxPixels=1e9
        )
        return ee.Feature(None, stats).set('date', img.get('date'))
    
    reduced = monthly_ic.map(reduce_to_feature)

    features = reduced.getInfo()['features']
    values = [f['properties'] for f in features]

    df = pd.DataFrame(values)
    df['date'] = pd.to_datetime(df['date'])
    df = df.rename(columns={'precipitation': 'monthly_precipitation_mm'})

    # Save to CSV
    df.to_csv(DATA_FOLDER/f"monthly_precipitation_{polygon_location_file.name}.csv", index=False)
    print("CSV saved.")
