import logging
import numpy as np
import rasterio
from scipy.ndimage import uniform_filter
import matplotlib.pyplot as plt

from settings import DATA_FOLDER

logging.basicConfig(level=logging.INFO)

from numpy.lib.stride_tricks import sliding_window_view

def average_dem(dem_array, size=30):
    # Convert 0 to NaN
    dem_array = np.where(dem_array == 0, np.nan, dem_array)

    # Use sliding windows to apply nanmean manually
    pad = size // 2
    padded = np.pad(dem_array, pad_width=pad, mode='constant', constant_values=np.nan)
    windows = sliding_window_view(padded, (size, size))
    averaged = np.nanmean(windows, axis=(-2, -1))
    return averaged


def map_flow_direction(dem_array, transform, output_path, step=10):
    import numpy as np
    import matplotlib.pyplot as plt

    # Fill NaNs temporarily to compute gradient
    dem_filled = np.nan_to_num(dem_array, nan=0.0)
    dy, dx = np.gradient(dem_filled)
    magnitude = np.sqrt(dx**2 + dy**2)

    # Downsample for quiver
    x = np.arange(0, dem_array.shape[1], step)
    y = np.arange(0, dem_array.shape[0], step)
    X, Y = np.meshgrid(x, y)

    scale_factor = 100
    U = -dx[::step, ::step] * scale_factor
    V = -dy[::step, ::step] * scale_factor
    M = magnitude[::step, ::step]

    # Mask only valid data
    mask = ~np.isnan(dem_array[::step, ::step])

    plt.figure(figsize=(12, 10))
    im = plt.imshow(np.where(np.isnan(dem_array), np.nan, dem_array), cmap='terrain')
    plt.colorbar(im, label='Elevation (m)')

    # Plot arrows only on valid data
    plt.quiver(X[mask], Y[mask], U[mask], V[mask],
               M[mask], scale=5, scale_units='xy', angles='xy', cmap='Blues')

    plt.title("Flow Direction Map (Arrow Size = Slope Intensity)")
    plt.xlabel("X (pixels)")
    plt.ylabel("Y (pixels)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def main():
    import logging
    from pathlib import Path

    dem_file = DATA_FOLDER / "nasa_dem_elevation_Frankfurt.gpkg.tif"
    

    with rasterio.open(dem_file) as src:
        dem = src.read(1).astype(float)
        transform = src.transform

    size = 30
    logging.info(f"Averaging {dem_file} with size {size} pixels")
    averaged_dem = average_dem(dem, size=size)

    logging.info(f"Mapping flow direction")
    output_path = DATA_FOLDER / f"{dem_file.name}_flow_direction.png"
    map_flow_direction(averaged_dem, transform, output_path)


if __name__ == "__main__":
    main()
