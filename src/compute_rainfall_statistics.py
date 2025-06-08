
from pathlib import Path
import logging
import ee
from raster_utils import compute_rainfall_statistics
from settings import DATA_FOLDER

logging.basicConfig(level=logging.INFO)


google_earth_engine_project_name = "rainfallanalysis-462313"

def main():

    logging.info(f"Authenticate to google earth engine...")

    ee.Authenticate()
    ee.Initialize(project=google_earth_engine_project_name)

    boundaries_gpkg = DATA_FOLDER / "Naucalpan.gpkg"

    logging.info(f"Starting rainfall statistics on boundaries: {boundaries_gpkg}")

    compute_rainfall_statistics(boundaries_gpkg)

if __name__ == "__main__":
    main()
