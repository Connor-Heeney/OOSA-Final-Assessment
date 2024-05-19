import rasterio
import numpy as np
import matplotlib.pyplot as plt

class DEMAnalysis:
    def __init__(self, dem_file_2009, dem_file_2015):
        self.dem_2009 = self.read_geotiff(dem_file_2009)
        self.dem_2015 = self.read_geotiff(dem_file_2015)

    def read_geotiff(self, file_path):
        """
        Read a GeoTIFF file and return its data and profile.

        - file_path: Path to the GeoTIFF file to be read.
        - Return a tuple which contains raster data and metadata.
        """
        with rasterio.open(file_path) as src:
            return src.read(1), src.profile

    def calculate_volume_change(self):
        """
        Calculate the total volume change between the two DEMs.
        Returns the total volume change computed by integrating the elevation differences over the area.
        """
        elevation_change = self.dem_2015[0] - self.dem_2009[0]
        volume_change = np.sum(elevation_change) * self.dem_2009[1]['transform'][0] * self.dem_2009[1]['transform'][4]
        return volume_change

    def create_change_map(self, output_file, show_map=True):
        """
        Create a GeoTIFF map that visualises the elevation change between two DEMs and optionally display it.
        """
        elevation_change = self.dem_2015[0] - self.dem_2009[0]
        with rasterio.open(output_file, 'w', **self.dem_2009[1]) as dst:
            dst.write(elevation_change, 1)

        if show_map:
            plt.figure(figsize=(10, 10))
            plt.imshow(elevation_change, cmap='coolwarm', vmin=np.nanmin(elevation_change), vmax=np.nanmax(elevation_change))
            plt.colorbar(label='Elevation Change (m)')
            plt.title('Elevation Change 2009 - 2015')
            plt.show()

# Define output directory
output_directory = "src/outputs/t5_outputs/"
output_file = output_directory + "elevation_change.tif"

# Ensure output directory exists
import os
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Execute analysis with updated paths
dem_analysis = DEMAnalysis("src/outputs/t4_outputs/filled_2009_DEM.tif", "src/outputs/t4_outputs/filled_2015_DEM.tif")
volume_change = dem_analysis.calculate_volume_change()
print(f"Total Volume Change: {volume_change}")
dem_analysis.create_change_map(output_file)

