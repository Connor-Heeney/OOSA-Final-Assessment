

'''
A class to handle geotiffs
'''

#######################################################
# import necessary packages

from pyproj import Proj, transform # package for reprojecting data
from osgeo import gdal             # package for handling geotiff data
from osgeo import osr              # package for handling projection information
from gdal import Warp
import numpy as np


#######################################################

class tiffHandle():
  '''
  Class to handle geotiff files
  '''

  ########################################

  def __init__(self,filename):
    '''
    Class initialiser
    Does nothing as this is only an example
    '''


  ########################################
  def writeTiff(data,x,y,res,filename="lvis_image.tif",epsg=4326):
    '''
    Make a geotiff from an array of points
    '''

    # determine bounds
    minX=np.min(x)
    maxX=np.max(x)
    minY=np.min(y)
    maxY=np.max(y)

    # determine image size
    nX=int((maxX-minX)/res+1)
    nY=int((maxY-minY)/res+1)

    # pack in to array
    imageArr=np.full((nY,nX),-999.0)        # make an array of missing data flags

    # calculate the raster pixel index in x and y
    xInds=np.array(np.floor((x-np.min(x))/res),dtype=int)   # need to force to int type
    yInds=np.array(np.floor((np.max(y)-y)/res),dtype=int)
    # floor rounds down. y is from top to bottom

    # this is a simple pack which will assign a single footprint to each pixel
    imageArr[yInds,xInds]=data

    # set geolocation information (note geotiffs count down from top edge in Y)
    geotransform = (minX, res, 0, maxY, 0, -res)

    # load data in to geotiff object
    dst_ds = gdal.GetDriverByName('GTiff').Create(filename, nX, nY, 1, gdal.GDT_Float32)

    dst_ds.SetGeoTransform(geotransform)    # specify coords
    srs = osr.SpatialReference()            # establish encoding
    srs.ImportFromEPSG(epsg)                # WGS84 lat/long
    dst_ds.SetProjection(srs.ExportToWkt()) # export coords to file
    dst_ds.GetRasterBand(1).WriteArray(imageArr)  # write image to the raster
    dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
    dst_ds.FlushCache()                     # write to disk
    dst_ds = None

    print("Image written to",filename)
    return


  def writeTiff2(self,data,filename="chm.tif",epsg=27700):
    '''
    Write a geotiff from a raster layer
    '''

    # set geolocation information (note geotiffs count down from top edge in Y)
    geotransform = (self.minX, self.res, 0, self.maxY, 0, -1*self.res)

    # load data in to geotiff object
    dst_ds = gdal.GetDriverByName('GTiff').Create(filename, self.nX, self.nY, 1, gdal.GDT_Float32)

    dst_ds.SetGeoTransform(geotransform)    # specify coords
    srs = osr.SpatialReference()            # establish encoding
    srs.ImportFromEPSG(epsg)                # WGS84 lat/long
    dst_ds.SetProjection(srs.ExportToWkt()) # export coords to file
    dst_ds.GetRasterBand(1).WriteArray(data)  # write image to the raster
    dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
    dst_ds.FlushCache()                     # write to disk
    dst_ds = None

    print("Image written to",filename)
    return


  ########################################

  def readTiff(self,filename):
    '''
    Read a geotiff in to RAM
    '''

    # open a dataset object
    ds=gdal.Open(filename)
    # could use gdal.Warp to reproject if wanted?

    # read data from geotiff object
    self.nX=ds.RasterXSize             # number of pixels in x direction
    self.nY=ds.RasterYSize             # number of pixels in y direction
    # geolocation tiepoint
    transform_ds = ds.GetGeoTransform()# extract geolocation information
    self.xOrigin=transform_ds[0]       # coordinate of x corner
    self.yOrigin=transform_ds[3]       # coordinate of y corner
    self.pixelWidth=transform_ds[1]    # resolution in x direction
    self.pixelHeight=transform_ds[5]   # resolution in y direction
    # read data. Returns as a 2D numpy array
    self.data=ds.GetRasterBand(1).ReadAsArray(0,0,self.nX,self.nY)


#######################################################

