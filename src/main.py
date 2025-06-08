
from pathlib import Path
import logging
import ee
from raster_utils import export_dem_to_drive

logging.basicConfig(level=logging.INFO)
data_folder = Path(__file__).parents[1] / "data"

google_earth_engine_project_name = "sdgai-407909"

def main():

    logging.info(f"Authenticate to google earth engine...")

    ee.Authenticate()
    ee.Initialize(project=google_earth_engine_project_name)

    naucalpan_gpkg = data_folder / "Naucalpan.gpkg"

    logging.info(f"Starting to load earth engine DEM data to drive with boundaries based on vector {naucalpan_gpkg}")

    export_dem_to_drive(naucalpan_gpkg)

if __name__ == "__main__":
    main()
