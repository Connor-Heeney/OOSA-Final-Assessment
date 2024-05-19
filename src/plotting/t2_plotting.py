import os
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import argparse

def get_first_tif(directory):
    """
    Get the first .tif file from the specified directory.
    """
    for file in os.listdir(directory):
        if file.endswith('.tif'):
            return file
    raise FileNotFoundError("No .tif file found in the specified directory.")

def get_cmd_args():
    """
    Parse and return command line arguments for DEM plotting.
    If no input file is specified, the script will use the first .tif file found in the 't2_outputs' directory.
    """
    parser = argparse.ArgumentParser(description="Plot a DEM from a GeoTIFF file.")
    
    # Set the default path to the 't2_outputs' directory
    default_input_path = 'src/outputs/t2_outputs'
    default_input_file = get_first_tif(default_input_path)
    
    parser.add_argument("--input", type=str, default=os.path.join(default_input_path, default_input_file), help="Input GeoTIFF file")
    parser.add_argument("--output", type=str, default=os.path.join(default_input_path, 'DEM_plot.png'), help="Output plot filename")
    return parser.parse_args()

def plot_dem(input_file, output_file):
    """
    Plot the DEM from a GeoTIFF file and save it as an image.
    """
    with rasterio.open(input_file) as src:
        # Read the dataset's valid data mask as a ndarray.
        mask = src.dataset_mask()
        # Extract the easting and northing coordinates
        easting, northing = src.xy(mask.shape[0]//2, mask.shape[1]//2)
        
        fig, ax = plt.subplots(figsize=(10, 10))
        dem_data = src.read(1)
        
        show(dem_data, ax=ax, cmap='terrain', title=f'Digital Elevation Model\nEasting: {easting}m, Northing: {northing}m')
        plt.colorbar(mappable=plt.cm.ScalarMappable(cmap='terrain'), ax=ax, label='Elevation')
        plt.xlabel('Easting (m)')
        plt.ylabel('Northing (m)')
        
        plt.savefig(output_file)
        plt.show()
        print(f"DEM plot saved to {output_file}")

if __name__ == "__main__":
    args = get_cmd_args()
    
    # Ensure the output directory exists before saving the file
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Plot and save the DEM
    plot_dem(args.input, args.output)
