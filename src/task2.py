import argparse
from processLVIS import lvisGround
from lvisCompleteExample import writeTiff
from pyproj import Proj, transform
import numpy as np

def getCmdArgs():
    '''
    Parse command-line arguments for the DEM processing script.

    Parameters:
        1. input (str): The file used to create the DEM.
        2. outRoot (str): The output file name.
        3. projection (int): The projection that you want to use.
        4. Resolution (int): The resolution of the image to be ouput.
        5. output-dir (str): The minimum x-coordinate you want to choose.
        6. min-x (float): The minimum y-coordinate you want to choose.
        7. min-y (float): The maximum x-coordinate you want to choose.
        8. max-x (float): The maximum y-coordinate you want to choose.
        9. step-size (float): The step size you want to take over the image.
    '''
    p = argparse.ArgumentParser(description=("An argument parser to define the projection, resolution, bounds, and step size."))
    p.add_argument("--input", dest="inName", type=str, default='/geos/netdata/oosa/assignment/lvis/2009/ILVIS1B_AQ2009_1020_R1408_049700.h5', help=("Input filename"))
    p.add_argument("--outRoot", dest="outRoot", type=str, default='DEM', help=("Output filename root"))
    p.add_argument("--projection", dest="projection", type=int, default=3031, help=("EPSG code for the output projection"))
    p.add_argument("--resolution", dest="resolution", type=int, default=30, help=("Resolution size for the output DEM"))
    p.add_argument("--output-dir", dest="output_dir", type=str, default='src/outputs/t2_outputs', help=("Output directory"))
    p.add_argument("--min-x", dest="min_x", type=float, default=None, help=("Minimum x-coordinate"))
    p.add_argument("--min-y", dest="min_y", type=float, default=None, help=("Minimum y-coordinate"))
    p.add_argument("--max-x", dest="max_x", type=float, default=None, help=("Maximum x-coordinate"))
    p.add_argument("--max-y", dest="max_y", type=float, default=None, help=("Maximum y-coordinate"))
    p.add_argument("--step-size", dest="step_size", type=float, default=1.0, help=("Step size for spatial subsets"))
    return p.parse_args()

class plotLVIS(lvisGround):
    def reprojectLVIS(self, outEPSG):
        """
        Reproject the LVIS data points from their original geographic coordinate system (EPSG:4326)
        to the specified output coordinate system.

        - outEPSG: The target coordinate system for reprojection.
        """
        inProj = Proj("epsg:4326")
        outProj = Proj("epsg:" + str(outEPSG))
        self.x, self.y = transform(inProj, outProj, self.lat, self.lon)

    def writeDEM(self, outName):
        """
        Write the processed LVIS ground elevation data to a GeoTIFF file.

        - outName: The filename for the output GeoTIFF containing the DEM.
        """
        writeTiff(self.zG, self.x, self.y, self.resolution, filename=outName, epsg=self.projection)

if __name__ == "__main__":
    cmd = getCmdArgs()
    filename = cmd.inName
    outRoot = cmd.outRoot

    b = plotLVIS(filename, onlyBounds=True)
    step = cmd.step_size

    for x0 in np.arange(cmd.min_x or b.bounds[0], cmd.max_x or b.bounds[2], step):
        x1 = x0 + step
        for y0 in np.arange(cmd.min_y or b.bounds[1], cmd.max_y or b.bounds[3], step):
            y1 = y0 + step
            print("Tile between", x0, y0, "to", x1, y1)
            lvis = plotLVIS(filename, minX=x0, minY=y0, maxX=x1, maxY=y1, setElev=True)
            if lvis.nWaves == 0:
                continue

            lvis.reprojectLVIS(cmd.projection)
            lvis.estimateGround()
            outName = f"{cmd.output_dir}/lvisDEM.x.{x0}.y.{y0}.tif"
            lvis.resolution = cmd.resolution  # User passes resolution from command line arguments
            lvis.projection = cmd.projection  # User passes projection from command line arguments
            lvis.writeDEM(outName)