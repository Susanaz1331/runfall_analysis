
from pathlib import Path
import logging
import ee
from raster_utils import compute_rainfall_statistics_daily, compute_rainfall_statistics_monthly
from settings import DATA_FOLDER

logging.basicConfig(level=logging.INFO)


google_earth_engine_project_name = "rainfallanalysis-462313"

def main():

    logging.info(f"Authenticate to google earth engine...")

    ee.Authenticate()
    ee.Initialize(project=google_earth_engine_project_name)

    boundaries_gpkg = DATA_FOLDER / "Toluca.gpkg"

    logging.info(f"Starting rainfall statistics on boundaries: {boundaries_gpkg}")

    compute_rainfall_statistics_monthly(boundaries_gpkg)

    compute_rainfall_statistics_daily(boundaries_gpkg)

if __name__ == "__main__":
    main()
