import rasterio
import matplotlib.pyplot as plt

raster_file = 'src/outputs/t3_outputs/mosaic_2015.tif'

# Open the raster file
with rasterio.open(raster_file) as src:
    # Read the data
    data = src.read(1)

    # Get the affine transformation for the raster
    transform = src.transform
    
    # Calculate the extent of the plotted data using transform
    (width, height) = data.shape
    x_start, y_start = transform * (0, 0)
    x_end, y_end = transform * (width, height)
    extent = [x_start, x_end, y_end, y_start]

    # Plot the data
    plt.figure(figsize=(10, 10))
    plt.imshow(data, cmap='viridis', extent=extent)  # Use the 'extent' to scale axes
    plt.colorbar(label='Elevation')
    plt.title('Mosaic DEM with Northing and Easting')
    plt.xlabel('Easting')
    plt.ylabel('Northing')
    plt.savefig('src/outputs/t3_outputs/2015_mosaic_plot.png')
    plt.show()



