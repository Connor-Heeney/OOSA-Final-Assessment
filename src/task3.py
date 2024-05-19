import os
import argparse
from glob import glob
from lvisClass import lvisData
import osgeo.gdal as gdal
from lvisCompleteExample import plotLVIS
import numpy as np

def getCmdArgs():
    """
    Parse command-line arguments for the DEM processing script.

    Parameters:
        1. input_folder (str): Directory containing the input HDF5 files.
        2. output_folder (str): Directory where the output DEMs will be saved.
        3. step_divisor (int): Divisor to determine the step size for processing.
        4. resolution (int): Spatial resolution for the output DEMs.
    """

    parser = argparse.ArgumentParser(description="Process LVIS files into DEM and mosaic into a single GeoTIFF.")
    parser.add_argument("--input_folder", type=str, default='/geos/netdata/oosa/assignment/lvis/2015/', help="Input folder containing HDF5 files")
    parser.add_argument("--output_folder", type=str, default='src/outputs/t3_outputs', help="Output folder for individual DEM GeoTIFFs and final mosaic")
    parser.add_argument("--mosaic_name", type=str, default='mosaic_2015', help="Base name for the output mosaic files")
    parser.add_argument("--step_divisor", type=int, default=16, help="Divisor for the step size to split the input files into tiles")
    parser.add_argument("--resolution", type=int, default=200, help="Resolution for the output DEM")
    return parser.parse_args()

def process_files_to_dem(input_folder, output_folder, step_divisor, resolution):
    """
    Process LVIS HDF5 files into DEMs and store them in the specified output folder.

    Iterates through files in the input folder, converts each to a DEM based on the specified resolution and tiling strategy,
    and saves them to the output folder for later mosaic creation.

    Parameters:
        1. input_folder (str): Directory containing the input HDF5 files.
        2. output_folder (str): Directory where the output DEMs will be saved.
        3. step_divisor (int): Divisor to determine the step size for processing.
        4. resolution (int): Spatial resolution for the output DEMs.
    """
    file_list = glob(input_folder + '/*.h5') # glob pullfiles from input_folder with a suffix of .h5

    for file in file_list[:]:  # Processing all images.
        b = plotLVIS(file, onlyBounds=True)
        step = (b.bounds[2] - b.bounds[0]) / step_divisor
        
        for x0 in np.arange(b.bounds[0], b.bounds[2], step):
            x1 = x0 + step
            for y0 in np.arange(b.bounds[1], b.bounds[3], step):
                y1 = y0 + step
                print("Tile between", x0, y0, "to", x1, y1)

                lvis = plotLVIS(file, minX=x0, minY=y0, maxX=x1, maxY=y1, setElev=True)
                if lvis.nWaves == 0:
                    continue

                lvis.reprojectLVIS(3031)  # reprojects the data to EPSG:3031
                lvis.estimateGround()
                outName = os.path.join(output_folder, f"lvisDEM.x.{x0}.y.{y0}.tif")
                lvis.writeDEM(resolution, outName)

def create_mosaic(output_folder, mosaic_name):
    """
    Create a mosaic from individual DEM GeoTIFFs located in the output folder.

    Uses GDAL to compile the generated DEM tiles into a single VRT and then converts it to a GeoTIFF.

    Parameters:
        1. output_folder (str): Directory containing the individual DEM GeoTIFFs.
        2. mosaic_name (str): Base name for the output mosaic file.
    """
    input_folder = output_folder
    mosaic_tifs = glob(input_folder + '/*.tif') # glob pulls all files in input_folder with .tif as suffix

    vrt_options = gdal.BuildVRTOptions(resolution='highest') # Creates a virtual raster to align the individual rasters
    vrt_ds = gdal.BuildVRT(f"{os.path.join(output_folder, mosaic_name)}.vrt", mosaic_tifs, options=vrt_options)

    # Convert virtual raster to a single TIFF file
    gdal.Translate(f'{os.path.join(output_folder, mosaic_name)}.tif', vrt_ds)

if __name__ == "__main__":
    args = getCmdArgs()
    
    # Making sure output directory actually exists
    os.makedirs(args.output_folder, exist_ok=True)
    
    # Creating a mosaic
    process_files_to_dem(args.input_folder, args.output_folder, args.step_divisor, args.resolution)
    create_mosaic(args.output_folder, args.mosaic_name)
