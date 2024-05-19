import argparse
import numpy as np
import rasterio
from rasterio.fill import fillnodata
import geopandas as gpd
from rasterio.mask import mask
from rasterio.mask import mask as rio_mask


def get_cmd_args():
    """
    Parses the command-line arguments provided to the script.

    Returns:
        - argparse.Namespace: An object containing all the parsed command-line arguments with attributes:
            1. input (str): Path to the input GeoTIFF file with no-data values.
            2. output (str): Path for the output GeoTIFF file where no-data values are filled and clipped.
            3. nodata_value (float): The value representing no-data in the input file.
            4. new_nodata_value (float): The new no-data value to set in the output file.
            5. max_search_distance (int): The maximum distance to search for valid values for interpolation.
            6. smoothing_iterations (int): The number of iterations for smoothing after filling no-data values.
            7. boundary_shapefile (str): Path to the shapefile used for clipping the output raster.
    """
    parser = argparse.ArgumentParser(description="Fill no-data values in a DEM and clip to a boundary shapefile.")
    parser.add_argument("--input", type=str, default='src/outputs/t3_outputs/mosaic_2009.tif', help="Input GeoTIFF file with no-data values")
    parser.add_argument("--output", type=str, default='src/outputs/t4_outputs/filled_2009_DEM.tif', help="Output GeoTIFF file with no-data values filled and clipped to boundary")
    parser.add_argument("--nodata_value", type=float, default=-999.0, help="Value representing no-data in the input file")
    parser.add_argument("--new_nodata_value", type=float, default=0.0, help="New no-data value to set in the output file")
    parser.add_argument("--max_search_distance", type=int, default=110, help="Maximum number of cells to search for valid values to interpolate")
    parser.add_argument("--smoothing_iterations", type=int, default=0, help="Number of smoothing iterations to run after filling no-data values")
    parser.add_argument("--boundary_shapefile", type=str, default = 'additional/boundary.shp', help="Path to the boundary shapefile for clipping the output")
    return parser.parse_args()


def clip_and_fill(input_file, boundary_shapefile, output_file, nodata_value, max_search_distance, smoothing_iterations):
    """
        Clips the input raster to a given boundary and fills no-data values within the clipped region.

        Parameters:
            1. input_file (str): Path to the input GeoTIFF file.
            2. boundary_shapefile (str): Path to the boundary shapefile for clipping the raster.
            3. output_file (str): Path where the processed GeoTIFF will be saved.
            3. nodata_value (float): The no-data value in the input file to identify areas to fill.
            4. max_search_distance (int): The maximum search distance in pixels for interpolation.
            5. smoothing_iterations (int): The number of iterations applied to smooth the filled raster.

        The function reads the input raster, applies a mask based on the boundary shapefile to clip it,
        then fills the no-data values within this clipped region, optionally smoothing the result before saving.
    """
    with rasterio.open(input_file) as src:
        meta = src.meta.copy()  # Copy the metadata while the file is open
        data = src.read(1)

    # Continue processing outside the 'with' block
    boundary = gpd.read_file(boundary_shapefile)
    boundary = boundary.to_crs(meta['crs'])
    shapes = [feature.geometry for feature in boundary.itertuples()]

    
    with rasterio.open(input_file) as src:
        out_image, out_transform = rio_mask(src, shapes, crop=True, nodata=meta['nodata'])
        meta.update({"height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})

        valid_data_mask = (out_image != nodata_value)

    # Assuming out_image might have an incorrect shape, adjust it.
        if out_image.shape[0] == 1:
            out_image = np.squeeze(out_image, axis=0)


        # Then write the adjusted image to the file.
        with rasterio.open(output_file, 'w', **meta) as dst:
            dst.write(out_image, 1)






if __name__ == "__main__":
    args = get_cmd_args()
    clip_and_fill(args.input, args.boundary_shapefile, args.output, args.nodata_value, args.max_search_distance, args.smoothing_iterations)