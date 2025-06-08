
from pathlib import Path
import logging
import ee
from raster_utils import export_dem_to_drive

logging.basicConfig(level=logging.INFO)
data_folder = Path(__file__).parents[1] / "data"

google_earth_engine_project_name = "rainfallanalysis-462313"

def main():

    logging.info(f"Authenticate to google earth engine...")

    ee.Authenticate()
    ee.Initialize(project=google_earth_engine_project_name)

    boundaries_gpkg = data_folder / "Frankfurt.gpkg"

    logging.info(f"Starting to load earth engine DEM data to drive with boundaries based on vector {boundaries_gpkg}")

    export_dem_to_drive(boundaries_gpkg)

if __name__ == "__main__":
    main()
