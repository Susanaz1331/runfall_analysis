import ee
import geopandas as gpd
from shapely.ops import unary_union
from pathlib import Path

def export_dem_to_drive(polygon_location_file: Path):
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