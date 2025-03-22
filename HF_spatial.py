# -*- coding: utf-8 -*-
"""
Module for creating the Human Footprint maps of Peru and Ecuador.

Version 2041001 (Preprint)

This script will read spatial datasets of pressures, prepared them by
converting them all to a raster format with identical dimensions, then
score them to reflect their expected human influence.
The scored pressures will then be added to calculate a Human Footprint map.

The structure of the module requires the following:
    - HF_main.py to control the higher level of the process.
    - HF_settings to control the general settings.
    - HF_tasks to call all functions according to the HF workflow.
    - HF_spatial to provide all spatial functions and classes.
    - HF_scores to provide scores of humnan influence.
    - HF_layers for the settings related to layers (e.g. paths).

This is part of the project Life on Land, with UNDP, the Ministries of the
Environment of each country, and funded by NASA.

Created on Thu Jun 18 18:26:00 2020

@author: Jose Aragon-Osejo aragon@unbc.ca / jose.luis.aragon.ec@gmail.com

"""

import os
import copy
import math
# import sys
import numpy as np
# from math import sqrt
from osgeo import gdal, ogr, osr
import HF_scores
from HF_layers import layers_settings
from HF_layers import multitemporal_layers
import rasterio
import rioxarray as rxr
from skimage import graph
import xarray as xr
import geopandas as gpd
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.enums import Resampling
from datetime import datetime
import random
import shutil

ogr.UseExceptions()
today_date = datetime.today().strftime('%Y-%m-%d')

class RASTER():
    """
    Class for working with rasters.
    Currently only TIFFs are supported.
    """

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1].split('.')[-2]
        try:
            self.ds = gdal.Open(path, gdal.GA_Update)
        except:
            # Alternative opening method for Cloud Optimized GeoTiffs
            self.ds = gdal.OpenEx(path, gdal.GA_Update, open_options=["IGNORE_COG_LAYOUT_BREAK=YES"])
        self.XSize = self.ds.RasterXSize
        self.YSize = self.ds.RasterYSize
        self.bd = self.ds.GetRasterBand(1)
        self.nodata = self.bd.GetNoDataValue()
        self.geotrans = self.ds.GetGeoTransform()
        self.resX = self.geotrans[1]
        self.resY = - self.geotrans[5]
        self.projref = self.ds.GetProjectionRef()
        self.crs_authority = osr.SpatialReference(wkt=self.ds.GetProjection()).GetAttrValue('AUTHORITY', 1)
        self.dataType = self.bd.DataType
        self.dataType_name = gdal.GetDataTypeName(self.dataType)

    def get_array(self):
        """
        Initiates the array. The array is not initiated at __init__ to avoid
        memory issued if the array is not needed.

        Returns
        -------
        None.

        """
        self.array = self.bd.ReadAsArray()
        return self.array

    def close(self):
        """
        Closes the class instance. Needed to save changes.

        Returns
        -------
        None.

        """
        try:
            self.bd.ComputeStatistics(0)
        except:
            pass
        self.ds = None
        self.XSize = None
        self.YSize = None
        self.bd = None
        self.nodata = None
        # try:
        self.array = None
        # except:
        #     pass


class VECTOR():
    """
    Class for working with vectors.
    Currently only shapefiles are supported.
    """

    def get_geometry_type(self, layer):
        """
        Transforms grometry type in number format to name.
        WKB types supported by GDAL as shown here:
            http://portal.opengeospatial.org/files/?artifact_id=25355
            https://gis.stackexchange.com/questions/239289/gdal-ogr-python-getgeomtype-method-returns-integer-what-is-the-matching-geo

        Parameters
        ----------
        layer : ogr layer from which the type will be translated.

        Returns
        -------
        Geometry type as org name.

        """

        GeometryTypeToName_Translator = {
            1: ogr.wkbPoint,
            2: ogr.wkbLineString,
            3: ogr.wkbPolygon,
            4: ogr.wkbMultiPoint,
            5: ogr.wkbMultiLineString,
            6: ogr.wkbMultiPolygon,
        }
        layer_defn = layer.GetLayerDefn()
        return layer_defn.GetGeomType(), \
            GeometryTypeToName_Translator[layer_defn.GetGeomType()]

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1].split('.')[0]
        # self.driver = ogr.GetDriverByName("ESRI Shapefile")
        # self.ds = self.driver.Open(path, 1)  # 1 to read and write
        self.ds = ogr.Open(path, 1)  # 1 to read and write
        self.layer = self.ds.GetLayer()
        self.crs = self.layer.GetSpatialRef()
        self.extent = self.layer.GetExtent()
        self.crs_authority = self.crs.GetAttrValue('AUTHORITY', 1)
        self.geom_type_num, self.geom_type = self.get_geometry_type(self.layer)
        self.defn = self.layer.GetLayerDefn()
        self.schema = self.layer.schema

    def close(self):
        """
        Closes the class instance. Needed to save changes.

        Returns
        -------
        None.

        """
        self.ds = None
        self.layer = None
        self.crs = None
        self.geom_type = None


def compress(pressure_path):
    """
    Compresses a raster.
    More info at https://gdal.org/drivers/raster/cog.html
    Parameters
    ----------
    pressure_uncomp_path : uncompressed path of existing raster.
    pressure_path : compressed output raster.

    Returns
    -------
    None.

    """

    # Get new name for temporal uncompressed raster
    path0 = pressure_path.split('/')
    path1 = path0[-1].split(".")
    path1[0] = path1[0] + '_uncomp'
    path1 = '.'.join(path1)
    path0[-1] = path1
    pressure_uncomp_path = '/'.join(path0)

    # Copy raster to new name and delete original
    # command = f'gdalmanage copy  "{pressure_path}" "{pressure_uncomp_path}"'
    # os.system(command)
    shutil.copy2(pressure_path, pressure_uncomp_path)
    os.remove(pressure_path)

    # Compress and remove uncompressed
    creation_options = ["COMPRESS=LZW", "TILED=YES", "BIGTIFF=YES"]#, "stats=True"]  # , "PREDICTOR=3"]
    reduced_raster = gdal.Translate(pressure_path, pressure_uncomp_path, creationOptions=creation_options)
    reduced_raster = None
    os.remove(pressure_uncomp_path)


def create_base_raster(base_path, settings, res):
    """
    Creates a base raster from a extent shapefile.
    Depends on the resolution from settings.
    ALL rasters produced later on will follow the same settings.

    Based on
    https://gis.stackexchange.com/questions/212795/rasterizing-shapefiles-with-gdal-and-python
    Parameters
    ----------
    base_path : path for the base raster.
    settings : general settings from GENERAL_SETTINGS class.

    Returns
    -------
    None.

    """

    extent_polygon = VECTOR(settings.extent_Polygon)
    extent = extent_polygon.extent  # tuple(w,e,s,n)

    # Create command string
    command = [
        'gdal_rasterize',
        '-l', extent_polygon.name,
        '-burn', 1.0,
        '-tr', res, res,
        '-a_nodata', -9999.0,
        '-te', extent[0], extent[2], extent[1], extent[3],
        '-ot', 'Float32',
        '-of', 'GTiff',
        '-co', 'COMPRESS=DEFLATE', '-co', 'PREDICTOR=2', '-co', 'ZLEVEL=9',
        f'"{settings.extent_Polygon}"',
        f'"{base_path}"',]

    command = ' '.join(str(i) for i in command)

    # Execute command line
    os.system(command)


def clip_raster_by_extent(out_path, raster_to_clip, settings, base_path):
    # Open the raster datasets
    ds_to_clip = gdal.Open(raster_to_clip, gdal.GA_Update)
    ds_base = gdal.Open(base_path)

    # Read the raster bands
    band_to_clip = ds_to_clip.GetRasterBand(1)
    band_base = ds_base.GetRasterBand(1)

    # Get the NoData value of the base raster
    base_nodata = band_base.GetNoDataValue()
    to_clip_nodata = band_to_clip.GetNoDataValue()

    # Read the data as numpy arrays
    data_to_clip = band_to_clip.ReadAsArray()
    data_base = band_base.ReadAsArray()

    # Set NoData pixels in the raster_to_clip using base_nodata value
    data_to_clip[data_base == base_nodata] = to_clip_nodata

    # Write the updated data back to the raster_to_clip
    band_to_clip.WriteArray(data_to_clip)

    # Close the raster datasets
    ds_to_clip = None
    ds_base = None



def GetGeoInfo(base_raster):
    """
    Returns base raster settings
    NDV, xsize, ysize, GeoT, Projection, DataType

    https://gis.stackexchange.com/questions/57005/python-gdal-write-new-raster-using-projection-from-old
    """

    NDV = base_raster.bd.GetNoDataValue()
    if NDV == None: NDV = -9999
    xsize = base_raster.ds.RasterXSize
    ysize = base_raster.ds.RasterYSize
    GeoT = base_raster.ds.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(base_raster.ds.GetProjectionRef())
    DataType = base_raster.dataType_name

    return NDV, xsize, ysize, GeoT, Projection, DataType

def ParseType(type):
    """
    Returns datatype in GDAL format.
    https://github.com/USGS-Astrogeology/GDAL_scripts/blob/master/gdal_baseline_slope/gdal_baseline_slope.py
    """
    if type == 'Byte':
        return gdal.GDT_Byte
    elif type == 'Int16':
        return gdal.GDT_Int16
    elif type == 'UInt16':
        return gdal.GDT_UInt16
    elif type == 'Int32':
        return gdal.GDT_Int32
    elif type == 'UInt32':
        return gdal.GDT_UInt32
    elif type == 'Float32':
        return gdal.GDT_Float32
    elif type == 'Float64':
        return gdal.GDT_Float64
    elif type == 'CInt16':
        return gdal.GDT_CInt16
    elif type == 'CInt32':
        return gdal.GDT_CInt32
    elif type == 'CFloat32':
        return gdal.GDT_CFloat32
    elif type == 'CFloat64':
        return gdal.GDT_CFloat64
    else:
        return gdal.GDT_Byte


def CreateGeoTiff(path, Array, driver, NDV,
                  xsize, ysize, GeoT, Projection, DataType):
    """
    Creates a new raster from
    path, Array, driver, NDV, xsize, ysize, GeoT, Projection, DataType

    Function to write a new file
    https://gis.stackexchange.com/questions/57005/python-gdal-write-new-raster-using-projection-from-old
    """
    DataType = ParseType(DataType)
    DataSet = driver.Create(path, xsize, ysize, 1, DataType)
    # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection.ExportToWkt())
    # Write the array
    DataSet.GetRasterBand(1).WriteArray(Array)
    DataSet.GetRasterBand(1).SetNoDataValue(NDV)
    DataSet = None


def copy_raster(path, base_raster, Float=True, array=False):
    """
    Copies a raster to another path according to base raster.
    If array is provided, it will create a copy of base raster with new values.

    https://gis.stackexchange.com/questions/57005/python-gdal-write-new-raster-using-projection-from-old
    """

    # Open the original file
    if type(array) == bool:
        base_raster.get_array()
        array = base_raster.array

    # Get the raster info
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(base_raster)

    # Set up the GTiff driver
    driver = gdal.GetDriverByName('GTiff')

    # Change DataType to Float if necessary
    if Float:
        DataType = 'Float32'
    else:
        DataType = 'Int32'

    # Now turn the array into a GTiff.
    CreateGeoTiff(path, array, driver, NDV,
                  xsize, ysize, GeoT, Projection, DataType)


def createRasterFromCopy(fn, ds, data):
    """ Similar method as previous, merge """ #  TODO
    driver = gdal.GetDriverByName('GTiff')
    outds = driver.CreateCopy(fn, ds, strict=0)
    band_out = outds.GetRasterBand(1)
    band_out.WriteArray(data)
    band_out.ComputeStatistics(0)
    ds = None
    outds = None
    band_out = None


def warp_raster(layer, settings, base_path, pressure_path, scoring_template,
                scoring_method, main_folder):#, raster_list=False
    #  TODO don't use raster_list
    """
    Warps a raster to match base raster's settings.
    Special cases are considered.

    Parameters
    ----------
    layer : Layer name of the pressure/dataset.
    settings : general settings from GENERAL_SETTINGS class.
        base_path : path to base raster.
    pressure_path : path for the output warped raster.
    scoring_template : Name of the scoring template from HF_scores.
        E.g. 'GHF'.
    scoring_method : scoring method is a setting of each layer and will
        determine the type of preparing and scoring. Comes from HF_layers.
    main_folder : Name of folder in root for all analysis.
    raster_list : optional. The default is False.
        If more than one raster is to be warped, it returns a list.

    Returns
    -------
    new_in_paths : List of warped rasters, if necessary.

    """

    print(f'         Warping {layer}')
    country = settings.country

    # Search for pressure layer if exists
    # if scoring_method != 'GHS_BUILT_scores':
    in_paths = layers_settings[layer]["path"]
    in_paths = [f'{main_folder}{i}' for i in in_paths]
    # else:
    #     if country == 'Ecuador':
    #         in_paths =  layers_settings[layer]["path_Ec"]
    #     elif country == 'Peru':
    #         in_paths =  layers_settings[layer]["path_Pe"]
    #     in_paths = [f'{main_folder}{i}' for i in in_paths]
    # new_in_paths = [] # TODO check if necessary, and more than 1 path

    # Loop over each path in layer
    for in_path in in_paths:

        # Names
        # in_path_str = in_path.split('/')[-1].replace('.', '_')
        # layer_name = '_'.join(in_path_str.split('_')[:-1])
        # if not (len(in_paths) > 1):
        #     layer_name = layer

        final_path = pressure_path
        prepared_exists = os.path.isfile(final_path)

        if not prepared_exists:

            print(f'            Warping {layer}')
            # print(f'            Warping {layer_name}')

            # Get resampling mode for warping
            # if scoring_method == 'pop_scores_Fcbk':
            #     resampling_method = 'sum'  #TODO why here and not settings?
            # else:
            scores_full = getattr(HF_scores, settings.scoring_template)
            scores = scores_full[scoring_method]
            resampling_method = scores['resampling_method']

            if resampling_method == 'bilinear': rm = Resampling.bilinear
            if resampling_method == 'mode': rm = Resampling.mode

            # 
            base_raster = rxr.open_rasterio(base_path)
            # nd = base_raster.rio.nodata
            raster_to_warp = rxr.open_rasterio(in_path)
            raster_to_warp = raster_to_warp.astype('float32')
            nd_dataset = raster_to_warp.rio.nodata
            raster_to_warp = raster_to_warp.where(raster_to_warp != nd_dataset, 0)
            # raster_to_warp = raster_to_warp.where(raster_to_warp != -9999, -9998)
            warped_raster = raster_to_warp.rio.reproject_match(base_raster, resampling=rm, nodata=-9999)
            # if nd_dataset != np.float64('nan'): 
            #     print('y')
            #     warped_raster.rio.write_nodata(nd_dataset)
            warped_raster.rio.to_raster(final_path)


            # # If nodata value in warp is nan, replace with 0
            # in_raster = RASTER(in_path)
            # if in_raster.nodata and math.isnan(in_raster.nodata):
            #     final_raster = RASTER(final_path)
            #     final_raster.get_array()
            #     final_ar = final_raster.array.copy()
            #     final_ar[final_ar == nd] = 0
            #     save_array(final_raster.bd, final_ar)
            #     final_raster.close()
            # in_raster.close()

            # # If it's hab/pixel, transform to population density
            # # dividing array by km2 area
            # if scoring_method in ('pop_scores', 'pop_scores_Fcbk'):
            #     final_raster = RASTER(final_path)
            #     final_raster.get_array()
            #     final_ar = final_raster.array.copy()
            #     xres = abs(final_raster.resX) / 1000
            #     yres = abs(final_raster.resY) / 1000
            #     area = xres * yres
            #     final_ar = final_ar / area
            #     save_array(final_raster.bd, final_ar)
            #     final_raster.close()

        else:
            # Adding raster to list of rasters to return
            # new_in_paths.append(in_path)
            print(f'            {layer} already prepared')

    # if raster_list:
    #     return new_in_paths


def small_warp_raster(layer, base_path, in_path, out_path, settings, nd=99,
                      ratio=1):
    """

    """

    print(f'            Warping {layer}')


    rm = Resampling.bilinear

    base_raster = rxr.open_rasterio(base_path)
    raster_to_warp = rxr.open_rasterio(in_path)
    warped_raster = raster_to_warp.rio.reproject_match(base_raster, resampling=rm)
    warped_raster.rio.to_raster(out_path)

    # Compress
    compress(out_path)


def save_array(bd, array):
    """ Saves an array into a band and computes statistics. """
    bd.WriteArray(array)
    nodata = bd.GetNoDataValue()
    if nodata == 0:
        bd.SetNoDataValue(-9999)
    bd.ComputeStatistics(0)


def scores_to_0(value):
    """ Used for changing arrays to 0 values. """
    return 0


def reproject_shapefile(in_path, out_path, layer, settings):
    """
    Copies and or Reprojects a shapefile to match the coordinate system of the base layer.
    As defined here:
        https://gdal.org/programs/ogr2ogr.html

    Parameters
    ----------
    in_path : path to shapefile to reproject.
    out_path : path to new reprojected shapefile.
    layer : name of the layer
    settings : general settings from GENERAL_SETTINGS class.

    Returns
    -------
    None.

    """

    print('            Copying/Reprojecting ' + layer)

    # Search for pressure layer if exists
    out_exists = os.path.isfile(out_path)

    # Continue if does not exist
    if not out_exists:

        # Get geometry type from input layer
        pressure_vector = VECTOR(in_path)
        geom_type = pressure_vector.geom_type_num
        pressure_vector.close()

        if geom_type in (1, 4):
            geom_type = 'MULTIPOINT'
        elif geom_type in (2, 5):
            geom_type = 'MULTILINESTRING'
        elif geom_type in (3, 6):
            geom_type = 'MULTIPOLYGON'
        # print('geom_type', geom_type)

        # Create command string
        c1 = ['ogr2ogr','-f', '"GPKG"',
              '-t_srs', f'EPSG:{settings.crs_authority}',
              '-nlt', f'"{geom_type}"',
              ]
        if settings.clip_by_Polygon:
            c2 = ['-clipsrc',
            f'"{settings.extent_Polygon}"',]
        else:
            c2 = []
        c3 =[f'"{out_path}"', f'"{in_path}"',]

        command = ' '.join(str(i) for i in c1+c2+c3)

        # Execute command line
        os.system(command)

    else:
        print(f'               {layer} was already reprojected')


def rasterize_shapefile(in_path, out_path, layer, settings, base_path):
    """
    Burns a shapefile into a raster (rasterize).
    If Field is specified in layer settings, it burns a categorical value.

    Parameters
    ----------
    in_path : path to shapefile to rasterize.
    out_path : path to new raster.
    layer : name of the layer
    settings : general settings from GENERAL_SETTINGS class.
    base_path : path to base raster.

    Returns
    -------
    None.

    """

    print('            Rasterizing ' + layer)

    # Search for pressure layer if exists
    out_exists = os.path.isfile(out_path)

    # Continue if does not exist
    if not out_exists:

        # Vector layer as a raster
        clipped_vector = VECTOR(in_path)
        clipped_layer = clipped_vector.layer

        # Get field for rasterizing
        try:
            field = layers_settings[layer]['cat_field']
        except KeyError:
            field = None

        # Is field exists, check if it'a string field
        field_is_string = False
        if field:
            for i in clipped_vector.schema:
                if i.GetName() == field:
                    field_type = (i.GetFieldTypeName(i.GetType()))
                    if field_type == 'String':
                        field_is_string = True

        # If field is string, translate to numbers in a new field
        if field_is_string:

            # Import scoring methods to assign an integer to land use categories
            scoring_method = layers_settings[layer]['scoring']
            scores_full = getattr(HF_scores, settings.scoring_template)
            scores = scores_full[scoring_method]

            # Create new field
            # field_name = ogr.FieldDefn('Use_int', ogr.OFTInteger)
            field_name = ogr.FieldDefn('Use_int', ogr.OFTReal)
            field_name.SetPrecision(3)
            try:
                clipped_layer.CreateField(field_name)
                field_to_fill = True
            except RuntimeError:
                field_to_fill = False

            if field_to_fill:

                # Populate new field translating string to number categories
                # loop through the input features
                inFeature = clipped_layer.GetNextFeature()
                while inFeature:
                    value_int = None
                    value_str = inFeature.GetField(field)
                    for topic in scores['scores_by_categories']:
                        if value_str in scores['scores_by_categories'][topic][1]:
                            value_int = scores['scores_by_categories'][topic][0]

                    # Silly value to catch missing values
                    if value_int is None:
                        print(f'Problem string {value_str}')
                        value_int = 999
                    inFeature.SetField('Use_int', value_int)
                    clipped_layer.SetFeature(inFeature)
                    inFeature = clipped_layer.GetNextFeature()

        # Create a copy of base raster
        drv = gdal.GetDriverByName('GTiff')
        base_raster = RASTER(base_path)
        rasterized_template = drv.CreateCopy(out_path,
                                              base_raster.ds, strict=0)
        rasterized_template = None

        # Convert clipped raster's values to 0s and save
        rasterized_raster = RASTER(out_path)
        rasterized_array = rasterized_raster.get_array()
        rasterized_array[rasterized_array<1000] = 0
        rasterized_raster.bd.WriteArray(rasterized_array)
        rasterized_raster.close()

        # Rasterize vector layer to template raster
        rasterized_raster = RASTER(out_path)
        if field:
            gdal.RasterizeLayer(rasterized_raster.ds,
                                [1], clipped_layer,
                                options=["ATTRIBUTE=Use_int"])
        else:
            gdal.RasterizeLayer(rasterized_raster.ds, [1], clipped_layer,
                                None, None,  # transformation info not needed
                                [1],  # value to burn
                                ['ALL_TOUCHED=TRUE']  # burn all pixels touched
                                )

        # Close everything
        rasterized_raster.close()
        compress(out_path)
        base_raster.close()
        clipped_vector.close()

    else:
        print(f'               {layer} was already rasterized')


def proximity_raster(in_path, out_path, layer=''):
    """
    Creates a proximity raster form a rasterized shapefile.
    Returns values in meters.

    Parameters
    ----------
    in_path : path to rasterized layer.
    out_path : path to new proximity raster.
    layer : TYPE, optional
        Name of the layer. The default is ''.

    Returns
    -------
    None.

    """

    print('            Creating proximity raster ' + layer)

    # Search for pressure layer if exists
    out_exists = os.path.isfile(out_path)

    # Continue if does not exist
    if not out_exists:

        # Proximity raster path
        rasterized_raster = RASTER(in_path)
        rasterized_bd = rasterized_raster.bd

        # Create proximity raster and open a band
        drv = gdal.GetDriverByName('GTiff')
        proximity_ds = drv.Create(out_path,
                                  rasterized_raster.XSize,
                                  rasterized_raster.YSize,
                                  1, gdal.GetDataTypeByName('Int32'))
        proximity_ds.SetGeoTransform(rasterized_raster.geotrans)
        proximity_ds.SetProjection(rasterized_raster.projref)
        proximity_bd = proximity_ds.GetRasterBand(1)

        # Compute proximity raster
        gdal.ComputeProximity(rasterized_bd, proximity_bd, ['DISTUNITS=GEO', 'MAXDIST=20000'])

        # Close rasters
        proximity_bd.ComputeStatistics(0)
        proximity_ds = None
        rasterized_raster.close()

    else:
        print(f'               {layer} proximity raster existed already')


def create_proximity_raster(layer, settings, base_path, final_path,
                            scoring_template, main_folder, res):
    """
    Controls the process of creating a proximity raster.
    It will reproject, clip, rasterize and create the proximity raster.

    Parameters
    ----------
    layer : Layer name of the pressure/dataset to prepare
    settings : general settings from GENERAL_SETTINGS class.
    base_path : path to base raster.
    final_path : path for proximity raster.
    scoring_template : Name of the scoring template from HF_scores. E.g. 'GHF'.
    main_folder : Name of folder in root for all analysis.

    Returns
    -------
    None.

    """
    # Search for pressure layer if exists
    in_path = f'{main_folder}{layers_settings[layer]["path"][0]}'
    extent = settings.extent_Polygon
    extent_str = extent.split('/')[-1].split('.')[-2]
    out_path = in_path
    final_exists = os.path.isfile(final_path)

    if not final_exists:

        # Reproject shapefile
        out_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_{scoring_template}_clip_proj.gpkg'
        reproject_shapefile(in_path, out_path, layer, settings)

        # Rasterize reprojected and clipped shapefile
        in_path = out_path
        out_path = f'{main_folder}/HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_{res}m_rasterized.tif'
        rasterize_shapefile(in_path, out_path, layer, settings, base_path)

        # Create proximity raster
        in_path = out_path
        out_path = final_path
        proximity_raster(in_path, out_path, layer=layer)

    else:
        print(f'            {layer} already prepared')


def create_categorical_raster(layer, settings, base_path, final_path, main_folder, scoring_template):
    """
    Controls the process of creating a categorical raster.
    It will reproject, clip and rasterize.

    Parameters
    ----------
    layer : Layer name of the pressure/dataset to prepare
    settings : general settings from GENERAL_SETTINGS class.
    base_path : path to base raster.
    final_path : path for proximity raster.
    main_folder : Name of folder in root for all analysis.
    scoring_template : Name of the scoring template from HF_scores. E.g. 'GHF'.

    Returns
    -------
    None.

    """
    # Prepare in and out names
    in_path = f'{main_folder}{layers_settings[layer]["path"][0]}'
    extent = settings.extent_Polygon
    extent_str = extent.split('/')[-1].split('.')[-2]
    out_path = in_path

    # Search for pressure layer if exists
    final_exists = os.path.isfile(final_path)
    if not final_exists:

        # Reproject shapefile
        out_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_{scoring_template}_clip_proj.gpkg'
        reproject_shapefile(in_path, out_path, layer, settings)

        # Rasterize reprojected and clipped shapefile
        in_path = out_path
        out_path = final_path
        rasterize_shapefile(in_path, out_path, layer, settings, base_path)

    else:
        print(f'            {layer} already prepared')


def get_geo_coords(pixel, GT):
    # https://gdal.org/tutorials/geotransforms_tut.html
    GT0, GT1, GT3, GT5 = GT[0], GT[1], GT[3], GT[5]
    X_geo = GT0 + (pixel[1] + .5) * GT1
    Y_geo = GT3 + (pixel[0] + .5) * GT5
    return (X_geo, Y_geo)


def get_random_elements(lst, n):
    if n > len(lst):
        raise ValueError("The specified number of elements is greater than the length of the list.")

    random_indices = random.sample(range(len(lst)), n)
    random_elements = [lst[i] for i in random_indices]
    return random_elements

def get_source_pixels(built_path, sources_path):

    built_raster = RASTER(built_path)
    built_array = built_raster.get_array()

    rows = built_raster.YSize - 1
    cols = built_raster.XSize - 1

    track_built = copy.deepcopy(built_array)

    source_pixels_list = []

    for row in range(0, rows):
        for col in range(0, cols):
            if (track_built[row, col] != -2) and (built_array[row, col] == 1):

                track_built[row, col] = -2
                cluster = [(row, col)]
                big_pixels = [(row, col)]

                while big_pixels:

                    small_pixels = []

                    for big_neighb in big_pixels:

                        i = big_neighb[0]
                        j = big_neighb[1]

                        neighbs = {(i + 1, j): 'direct',
                                    (i - 1, j): 'direct',
                                    (i, j + 1): 'direct',
                                    (i, j - 1): 'direct',
                                    (i + 1, j + 1): 'diagonal',
                                    (i + 1, j - 1): 'diagonal',
                                    (i - 1, j + 1): 'diagonal',
                                    (i - 1, j - 1): 'diagonal', }

                        for n in neighbs:

                            try:
                                cond1 = track_built[n[0], n[1]] != -2
                                cond2 = built_array[n[0], n[1]] == 1
                            except IndexError:
                                cond1 = False
                                cond2 = False

                            if cond1 and cond2:
                                small_pixels.append((n[0], n[1]))
                                cluster.append((n[0], n[1]))
                                track_built[n[0], n[1]] = -2

                    big_pixels = list(set(small_pixels))

                unique_pixels = list(set(cluster))

                # Append a source pixel if it's a cluster of more than 1 pixel
                len_ = len(unique_pixels)
                if len_>1:
                    # Get number of source pixels according to size of cluster
                    if len_<50: # get 1
                        middle_index= int(np.floor(len_/2))
                        source_pixel = cluster[middle_index]
                        source_pixels_list.append(source_pixel)
                    else:
                        #  get 1 every 50 until 500 pixels, then every 100
                        div = 50 if len_<500 else 100
                        if len_>5000: div = 1000
                        n = int(len_/div)
                        source_pixel = get_random_elements(unique_pixels, n)
                        for i in source_pixel: source_pixels_list.append(i)

    GT = built_raster.geotrans
    source_pixels_list = [get_geo_coords(pixel, GT) for pixel in source_pixels_list]

    # Get authority of projection from base raster and close
    crs_authority = built_raster.crs_authority
    built_raster.close()
    built_array, track_built = None, None

    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    sources_path_shp = sources_path.replace('gpkg','shp')
    data_source = driver.CreateDataSource(sources_path_shp)

    # create the spatial reference, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(crs_authority))

    # create the layer
    layer = data_source.CreateLayer("sources", srs, ogr.wkbPoint)

    # Add the fields we're interested in
    layer.CreateField(ogr.FieldDefn("Id", ogr.OFTInteger))

    # Process the text file and add the attributes and features to the shapefile
    for count, pixel in enumerate(source_pixels_list):
        # create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        # Set the attributes using the values from the delimited text file
        feature.SetField("Id", count)
        # create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f)" %  (pixel[0], pixel[1])
        # Create the point from the Well Known Txt
        point = ogr.CreateGeometryFromWkt(wkt)
        # Set the feature geometry using the point
        feature.SetGeometry(point)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
        # Dereference the feature
        feature = None

    # Save and close the data source
    data_source = None

    # Convert to geopackage and remove shapefile
    command = f'ogr2ogr -f GPKG "{sources_path}" "{sources_path_shp}"'
    os.system(command)
    driver.DeleteDataSource(sources_path_shp)


def find_location_cells(destinations, cs):
    """find cell indices of destination locations
    Parameters
    ----------
    destinations: geopandas data frame containing locations
    cs: costsurface
    """

    print('               Finding locations', datetime.now().strftime("%H:%M:%S"))
    start_cells = []

    # Loop over all destination locations
    longs = cs.get_index('x')
    lats = cs.get_index('y')

    for location in destinations['geometry']:
        idx_i = longs.get_indexer([location.x], method='nearest')[0]
        idx_j = lats.get_indexer([location.y], method='nearest')[0]
        start_cells.append((0, idx_j, idx_i))

    return start_cells


def compute_cost_path(cost_raster_path, starting_points_gpkg_path, output_raster_path,
                      poly_mask=None):

    '''
    https://tretherington.blogspot.com/2017/01/least-cost-modelling-with-python-using.html
    '''

    with rxr.open_rasterio(cost_raster_path, masked=True) as costsurface:

        if not poly_mask:
            destinations = gpd.read_file(
                starting_points_gpkg_path,#)
                bbox=costsurface.rio.bounds())
        else:
            # Read polygon from geopackage
            # poly_gpkg_path = "path/to/polygon.gpkg"
            poly_gdf = gpd.read_file(poly_mask)

            # Read points from geopackage
            # points_gpkg_path = "path/to/points.gpkg"
            points_gdf = gpd.read_file(starting_points_gpkg_path)

            # Spatial join to get points within polygon
            # destinations = gpd.sjoin(points_gdf, poly_gdf, op="within")
            destinations = gpd.sjoin(points_gdf, poly_gdf, predicate="within")

        start_cells = find_location_cells(destinations, costsurface)

        del destinations

        print('               Getting cost surface', datetime.now().strftime("%H:%M:%S"))

        # find costs algorithm does not deal with np.NaN so change these
        # to -9999 in cost surface any negative values are ignored
        nd = -9999
        costsurface = costsurface.fillna(nd)

        # From the cost-surface create a 'landscape graph' object which can then be
        # analysed using least-cost modelling
        lg = graph.MCP_Geometric(costsurface.values, sampling=None)

        costs = xr.zeros_like(costsurface, dtype=np.float32)

        # Calculate the least-cost distance from the start cell to all other cells
        # [0] is returning the cumulative costs rather than the traceback
        costs.values = lg.find_costs(starts=start_cells)[0]

        del lg
        costs = xr.where(np.isfinite(costs), costs, nd)


    print('               Writing', datetime.now().strftime("%H:%M:%S"))
    with rasterio.open(cost_raster_path) as src:
        profile=src.profile

    costs = np.asarray(costs)
    with rasterio.open(output_raster_path, 'w', **profile) as dst:
        dst.nodata = nd
        dst.write(costs)


def split_raster(input_raster, output_path, polygon, name):

    # # Get list of polygon layers

    input_gdf = gpd.read_file(polygon)

    # Clip raster with geopandas GeoDataFrame
    clipped_raster, clipped_transform = \
        mask(input_raster, input_gdf.geometry,crop=True,indexes=1,all_touched=False)

    # Compute output profile
    output_profile = input_raster.profile.copy()
    output_profile.update({
        "width": clipped_raster.shape[1],
        "height": clipped_raster.shape[0],
        "transform": clipped_transform
    })

    # Write output raster
    with rasterio.open(output_path, "w", **output_profile) as output_raster:
        output_raster.write(clipped_raster, 1)


def merge_rasters(rasters_to_merge, final_path):
    
    print('   Merging', datetime.now().strftime("%H:%M:%S"))

    # # List of input rasters to merge
    for raster_path in rasters_to_merge:


        with rasterio.open(raster_path, 'r+') as src:
            nodata_value = src.nodata 
            new_nodata_value = -9999
            data = src.read(1)

            # Replace nodata pixel values with a new value
            data[~np.isfinite(data)] = new_nodata_value

            # Write the modified data to the original raster
            src.write(data, 1)


    # Merge rasters by minimum value
    merged, merged_transform = merge(rasters_to_merge,method="min")
    merged[merged==new_nodata_value] = nodata_value

    # Compute output profile
    output_profile = rasterio.open(rasters_to_merge[0]).profile.copy()
    output_profile.update({
        "width": merged.shape[2],
        "height": merged.shape[1],
        "transform": merged_transform,
        "nodata": nodata_value,     # Ensure the nodata value is set
        "BIGTIFF": "YES"            # Enable BigTIFF for large files
    })

    # Write output raster
    with rasterio.open(final_path, "w", **output_profile) as output_raster:
        output_raster.write(merged[0,:,:], 1)



def create_proximity_raster_from_pixels(layer, year, settings, base_path,
                                        final_path, scoring_template, purpose,
                                        results_folder, main_folder, res,
                                        scoring_method, multitemp):
    """
    Controls the creation of a raster of proximity from human influenced
    sections of rivers.
    It consideres built environments as starting points. Built environments
    have a maximum distance to rivers.
    It propagates the distance from this contact points up and dowm, up to a
    maximum distance.
    It creates a proximity raster from these sections of human influenced
    rivers.
    """

    # Prepare in and out names
    in_path_rivers = f"{main_folder}{layers_settings[layer]['path'][0]}"
    extent = settings.extent_Polygon
    extent_str = extent.split('/')[-1].split('.')[-2]
    year_txt = f'{year}_' if multitemp else ''
    purp = f'{purpose}_' if scoring_method in ('indirect_scores') else ''
    out_path = in_path_rivers

    # Search for pressure layer if exists
    final_exists = os.path.isfile(final_path)

    if not final_exists:

        # Algorithm needs the following rasters: rivers, flooded areas,
        # crops areas, built areas, elevation, slopes

        # Get crops raster
        in_path = f'{main_folder}HF_maps/b05_Added_pressures/p_Land_Cover_{extent_str}_{purpose}_{year}_{scoring_template}_{res}m.tif'
        crops_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_crops_{year_txt}{purp}{res}m.tif'
        exists = os.path.isfile(crops_path)

        if not exists:
            # Copy and Reclassify values
            print('         Preparing crops')
            # command = f'gdalmanage copy  "{in_path}" "{crops_path}"'
            # os.system(command)
            
            shutil.copy2(in_path, crops_path)
            
            
            crops_raster = RASTER(crops_path)
            crops_array = crops_raster.get_array()
            results_array = np.where((6 > crops_array) & (crops_array >= 5),1,0)
            crops_raster.bd.WriteArray(results_array)
            crops_raster.close()
            compress(crops_path)
            crops_array, results_array = None, None
            del crops_array, results_array

        # Get built areas raster
        in_path = f'{main_folder}HF_maps/b05_Added_pressures/p_Built_Environments_{extent_str}_{purpose}_{year}_{scoring_template}_{res}m.tif'
        built_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_built_{year_txt}{purp}{res}m.tif'
        exists = os.path.isfile(built_path)
        if not exists:

            print('            Preparing built areas')
            # Copy and Reclassify values
            # command = f'gdalmanage copy  "{in_path}" "{built_path}"'
            # os.system(command)
            
            shutil.copy2(in_path, built_path)
            
            built_raster = RASTER(built_path)
            built_array = built_raster.get_array()
            results_array = np.where((15 > built_array) & (built_array >= 6),1,0)
            built_raster.bd.WriteArray(results_array)
            built_raster.close()
            compress(built_path)
            results_array, built_array = None, None

        # Get rivers raster
        print('         Preparing rivers')
        # Reproject shapefile
        out_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_{scoring_template}_clip_proj.gpkg'
        reproject_shapefile(in_path_rivers, out_path, layer, settings)
        rivers_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_rivers_{res}m_rasterized.tif'
        rasterize_shapefile(out_path, rivers_path, layer, settings, base_path)

        # Get flooded areas raster
        in_path = main_folder + settings.flooded_path
        flooded_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_flooded_{res}m.tif'
        exists = os.path.isfile(flooded_path)
        if not exists:
            print('         Preparing flooded')
            small_warp_raster('Flooded raster', base_path, in_path,
                          flooded_path, settings)

        # Get roads in different levels
        in_path_l1, in_path_l2, in_path_l3 = None, None, None
        for layer_roads in settings.purpose_layers[purpose]['pressures']['Roads_Railways']['datasets']:
            if layers_settings[layer_roads]['scoring'] == 'road_scores_l1':
                in_path_l1 = f'{main_folder}/HF_maps/b03_Prepared_pressures/{extent_str}_{layer_roads}_{res}m_rasterized.tif'
            if layers_settings[layer_roads]['scoring'] == 'road_scores_l2':
                in_path_l2 = f'{main_folder}/HF_maps/b03_Prepared_pressures/{extent_str}_{layer_roads}_{res}m_rasterized.tif'
            if layers_settings[layer_roads]['scoring'] == 'road_scores_l3':
                in_path_l3 = f'{main_folder}/HF_maps/b03_Prepared_pressures/{extent_str}_{layer_roads}_{res}m_rasterized.tif'

        # Get coastline
        in_path = main_folder + settings.coast_path
        coast_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_coast_{res}m.tif'
        exists = os.path.isfile(coast_path)
        if not exists:
            print('         Preparing coastline')
            # Reproject shapefile
            out_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_coast_clip_proj.gpkg'
            reproject_shapefile(in_path, out_path, layer, settings)
            # Rasterize reprojected and clipped shapefile
            rasterize_shapefile(out_path, coast_path, layer, settings, base_path)

        # Get elevation raster
        in_path = main_folder + settings.elev_path
        elev_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_elevation_{res}m.tif'
        exists = os.path.isfile(elev_path)
        if not exists:
            print('         Preparing elevation')
            small_warp_raster('Elevation raster', base_path, in_path,
                          elev_path, settings)

        # # Get slopes raster
        in_path = main_folder + settings.slope_path
        slope_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_slope_{res}m.tif'
        exists = os.path.isfile(slope_path)
        if not exists:
            small_warp_raster('Slope raster', base_path, in_path,
                          slope_path, settings)

        # Calculate speeds raster from inputs and Rodrigo Sierra's
        # speeds research in Ecuador
        times_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_times10s_{year_txt}{purp}{res}m.tif'#.replace("\\","/").replace("//","/")
        exists = os.path.isfile(times_path)
        if not exists:

            print('            Calculating times surface')
            ave_walking = 4 #  average walking speed in km/h

            # Calculate speed based on conditions
            # print('flooded t')
            base_raster = RASTER(base_path)
            base_array = base_raster.get_array()
            nd = base_raster.nodata
            slope = RASTER(slope_path).get_array()
            slope[slope<=1.8] = 1.8 #  Minimum slope measured
            slope[slope>1000] = 1000 #  Maximum slope considered
            slope = slope.astype(int)
            flooded = RASTER(flooded_path).get_array().astype(int)
            speed_ar = np.where(base_array != 1, nd,
                np.where(flooded == 2, .5*(-0.975931*np.log(slope) + 6.761258),
                np.where((flooded == 0)  | (flooded == 1) , -0.975931*np.log(slope) + 6.761258,
                         ave_walking)))
            RASTER(flooded_path).close()
            base_raster.close()
            flooded, base_array = None, None

            # print('crops t')
            crops = RASTER(crops_path).get_array().astype(int)
            speed_ar = np.where(crops == 1, 10.560326*np.power(slope,-0.199553),speed_ar)
            RASTER(crops_path).close()
            crops = None

            # print('rivers t')
            elevation = RASTER(elev_path).get_array().astype(int)
            elevation[elevation<0] = 0
            rivers = RASTER(rivers_path).get_array().astype(int)

            # speed_ar()
            speed_ar[np.where((rivers==1) & ((0>slope) | (slope>1000)))] = 1000
            speed_ar[np.where((rivers==1) & ((0>elevation) | (elevation>10000)))] = 5000,
            speed_ar[np.where((rivers==1) & (0<=elevation) & (elevation<=450) & (0<=slope) & (slope<=5))] = 15
            speed_ar[np.where((rivers==1) & (0<=elevation) & (elevation<=450) & (5<slope) & (slope<=10))] = 7.5
            speed_ar[np.where((rivers==1) & (0<=elevation) & (elevation<=450) & (10<slope) & (slope<=15))] = 3.8
            speed_ar[np.where((rivers==1) & (0<=elevation) & (elevation<=450) & (15<slope) & (slope<=25))] = 1.9
            speed_ar[np.where((rivers==1) & (0<=elevation) & (elevation<=450) & (25<slope) & (slope<=1000))] = 1.4
            speed_ar[np.where((rivers==1) & (450<elevation) & (elevation<=700) & (0<=slope) & (slope<=5))] = 7.5
            speed_ar[np.where((rivers==1) & (450<elevation) & (elevation<=700) & (5<slope) & (slope<=10))] = 3.9
            speed_ar[np.where((rivers==1) & (450<elevation) & (elevation<=700) & (10<slope) & (slope<=15))] = 2.7
            speed_ar[np.where((rivers==1) & (450<elevation) & (elevation<=700) & (15<slope) & (slope<=25))] = 1.9
            speed_ar[np.where((rivers==1) & (450<elevation) & (elevation<=700) & (25<slope) & (slope<=1000))] = 1.4
            speed_ar[np.where((rivers==1) & (700<elevation) & (elevation<=1800) & (0<=slope) & (slope<=5))] = 3.8
            speed_ar[np.where((rivers==1) & (700<elevation) & (elevation<=1800) & (5<slope) & (slope<=10))] = 2.7
            speed_ar[np.where((rivers==1) & (700<elevation) & (elevation<=1800) & (10<slope) & (slope<=15))] = 2.0
            speed_ar[np.where((rivers==1) & (700<elevation) & (elevation<=1800) & (15<slope) & (slope<=25))] = 1.7
            speed_ar[np.where((rivers==1) & (700<elevation) & (elevation<=1800) & (25<slope) & (slope<=1000))] = 1.4
            speed_ar[np.where((rivers==1) & (1800<elevation) & (elevation<=2800) & (0<=slope) & (slope<=5))] = 1.9
            speed_ar[np.where((rivers==1) & (1800<elevation) & (elevation<=2800) & (5<slope) & (slope<=10))] = 1.9
            speed_ar[np.where((rivers==1) & (1800<elevation) & (elevation<=2800) & (10<slope) & (slope<=15))] = 1.7
            speed_ar[np.where((rivers==1) & (1800<elevation) & (elevation<=2800) & (15<slope) & (slope<=25))] = 1.4
            speed_ar[np.where((rivers==1) & (1800<elevation) & (elevation<=2800) & (25<slope) & (slope<=1000))] = 1.3
            speed_ar[np.where((rivers==1) & (2800<elevation) & (elevation<=10000) & (0<=slope) & (slope<=5))] = 1.4
            speed_ar[np.where((rivers==1) & (2800<elevation) & (elevation<=10000) & (5<slope) & (slope<=10))] = 1.4
            speed_ar[np.where((rivers==1) & (2800<elevation) & (elevation<=10000) & (10<slope) & (slope<=15))] = 1.4
            speed_ar[np.where((rivers==1) & (2800<elevation) & (elevation<=10000) & (15<slope) & (slope<=25))] = 1.3
            speed_ar[np.where((rivers==1) & (2800<elevation) & (elevation<=10000) & (25<slope) & (slope<=1000))] = 1.2

            RASTER(rivers_path).close()
            RASTER(slope_path).close()
            RASTER(elev_path).close()
            rivers, elevation, slope = None, None, None

            # print('coast t')
            coast = RASTER(coast_path).get_array().astype(int)
            speed_ar = np.where(coast == 1, 20, speed_ar)
            RASTER(coast_path).close()
            coast = None

            if in_path_l3:
                # print('roads3 t')
                roads3 = RASTER(in_path_l3).get_array().astype(int)
                speed_ar = np.where(roads3 == 1, 30, speed_ar)
                RASTER(in_path_l3).close()
                roads3 = None

            if in_path_l2:
                # print('roads2 t')
                roads2 = RASTER(in_path_l2).get_array().astype(int)
                speed_ar = np.where(roads2 == 1, 40, speed_ar)
                RASTER(in_path_l2).close()
                roads2 = None

            if in_path_l1:
                # print('roads1 t')
                roads1 = RASTER(in_path_l1).get_array().astype(int)
                speed_ar = np.where(roads1 == 1, 60, speed_ar)
                RASTER(in_path_l1).close()
                roads1 = None

            # print('built t')
            built = RASTER(built_path).get_array().astype(int)
            speed_ar = np.where(built == 1, 0, speed_ar)
            RASTER(built_path).close()
            built = None

            # If a value is negative (happens on edges with voids of data),
            # change to 4 as average walking speed
            # print('               Changing issues to average walking')
            bads = speed_ar<0
            speed_ar[bads] = ave_walking
            bads = None
            # Change speeds to time that takes to cross each pixel horizontally
            # or vertically
            print('               Changing speeds to times')
            xdist = base_raster.resX #  m
            ydist = base_raster.resY #  m
            diredist = (xdist + ydist) / 2
            # Change only if there is a value of speed
            goods = ~np.logical_or(speed_ar == nd, speed_ar == 0)
            # Converts
            # Multiplying by 36 to calculate times in 10s
            # (or speed are exagerated 10 times)
            # allows to keep one extra digit with ushort type
            speed_ar[goods] = np.divide(diredist*36, speed_ar[goods]).astype(int)

            # speed_ar[goods] = np.multiply(speed_ar[goods], )
            goods = None
            del goods

            # Save to raster
            print('               Saving times array to raster')
            copy_raster(times_path, RASTER(base_path), Float=True, array=speed_ar.astype(int))
            compress(times_path)
            speed_ar = None

        # Get a list of source built pixels to start propagating the distances
        sources_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_sources_{year_txt}{purp}{res}m.gpkg'#.replace("\\","/").replace("//","/")
        exists = os.path.isfile(sources_path)
        if not exists:
            print('            Getting source pixels for cost surface')
            get_source_pixels(built_path, sources_path)

        # Propagate travel as time from built areas
        # using speeds raster and a max daily distance
        print('               Starting', datetime.now().strftime("%H:%M:%S"))

        try:
        # if True:
            compute_cost_path(times_path, sources_path, final_path)
            compress(final_path)

        except MemoryError:
        # if True:

            # Get list of polygon layers
            print()
            print('*****************************************')
            print('MemoryError: splitting accessibility area')
            polygons = []
            split_folder = main_folder + settings.split_folder
            polygons += [split_folder+each for each in os.listdir(split_folder)]# if each.endswith('.gpkq')]

            rasters_to_merge = []
            with rasterio.open(times_path) as input_raster:

                for polygon_path in polygons:
                    
                    file_name_with_ext = os.path.basename(polygon_path)
                    name = os.path.splitext(file_name_with_ext)[0]
                    # name = polygon.split('.')[0][-2:]
                    print(f'   Processing {name}')

                    # Split times raster by previously created polygons
                    time_part_path = times_path.replace('.tif', f'_{name}.tif')
                    split_raster(input_raster, time_part_path, polygon_path, name)

                    # Calculate least_path and save split raster
                    out_path = final_path.replace('prepared', f'prepared_{name}')
                    rasters_to_merge.append(out_path)
                    compute_cost_path(time_part_path, sources_path, out_path, poly_mask=polygon_path)

            # Merge rasters parts
            merge_rasters(rasters_to_merge, final_path)
            compress(final_path)
            print('*****************************************')
            print()

    else:
        print(f'            {layer} already prepared')


def combineRasters(pressure, year, layers, settings, base_path, purpose, res,
                    scoring_template, results_folder, main_folder):
    """
    Takes all datasets of a pressure and combines them by maximum value.

    Parameters
    ----------
    pressure : Name of the pressure.
    year : year of HF map.
    layers : [datasets to be combined, are they multitemporal or not?].
    settings : general settings from GENERAL_SETTINGS class.
    base_path : path to base raster.
    purpose : Purpose of the Human footprint maps. Will match purpose_layers
        in Class GENERAL_SETTINGS.
    scoring_template : Name of the scoring template from HF_scores. E.g. 'GHF'.
    results_folder : Folder in root for all results.
    main_folder : Name of folder in root for all analysis.

    Returns
    -------
    None.

    """
    print()
    print(f'      Combining {pressure} {year}')

    num = 0
    extent = settings.extent_Polygon
    extent_str = extent.split('/')[-1].split('.')[-2]
    added_path = f'{main_folder}/HF_maps/b05_Added_pressures/p_{pressure}_{extent_str}_{purpose}_{year}_{scoring_template}_{res}m.tif'
    exists = os.path.isfile(added_path)

    if not exists:

        for layer in layers:

            multitemp = False
            for source in multitemporal_layers:
                if layer[0] in multitemporal_layers[source]['datasets']:
                    multitemp = True

            # Get scoring method
            scoring_method = layers_settings[layer[0]]['scoring']

            # If it's Navigable_Waterways, it's multitemporal anyway
            if scoring_method in ('indirect_scores'): multitemp = True

            year_txt = f'{year}_' if multitemp else ''
            purp = f'{purpose}_' if scoring_method in ('indirect_scores') else ''

            # Get path of scored layer and of copy in results folder
            press_path = f'{main_folder}/HF_maps/b04_Scored_pressures/{extent_str}_{layer[0]}_{purp}{year_txt}{scoring_template}_{res}m_scored.tif'

            # Get pressure raster array masked by NoData value
            press_raster = RASTER(press_path)
            nodata = press_raster.nodata
            press_raster.get_array()
            press_array = np.ma.masked_equal(press_raster.array, nodata)


            # Create and add pressures to final map
            if num == 0:
                datout = press_array
                fn1 = press_path
            else:
                if datout.dtype != np.float64 and press_array.dtype in (np.float64, np.float32):
                    datout = datout.astype(np.float64)
                    fn1 = press_path
                np.maximum(datout, press_array, out=datout)
 
            # Close pressure raster
            press_raster.close()
            press_array = None

            # Add 1 to num
            num += 1


        # Add rasters if there's at list one layer
        if num > 0:

            press_raster = RASTER(fn1)
            createRasterFromCopy(added_path, press_raster.ds, datout)
            press_raster.close()
            datout = None

            # Compress result and delete previous version
            compress(added_path)

    else:
        print(f'         {pressure} {year} was already combined')


def addRasters(year, settings, results_folder, purpose, scoring_template, res, main_folder):
    """
    Adds pressure maps to the final HF map for a given year.

    Parameters
    ----------
    year : year of HF map.
    settings : general settings from GENERAL_SETTINGS class.
    results_folder : Folder in root for all results.
    purpose : Purpose of the Human footprint maps. Will match purpose_layers
        in Class GENERAL_SETTINGS.
    scoring_template : Name of the scoring template from HF_scores. E.g. 'GHF'.

    Returns
    -------
    None.

    """

    print('   Copying pressure rasters')

    num = 0
    extent = settings.extent_Polygon
    extent_str = extent.split('/')[-1].split('.')[-2]

    # results_folder = r'G:\Conservation Solution Lab\People\Jose\OneDrive - UNBC\LoL_Data\Peru_HH\HF_maps\b05_HF_maps\Pe_20230605_183825_SDG15_Peru_IGN//'

    for pressure in settings.purpose_layers[purpose]['pressures']:

        # Continue if there are layers in pressures
        if settings.purpose_layers[purpose]['pressures'][pressure]['datasets']:

            # Get path of scored layer and of copy in results folder
            press_path = f'{main_folder}/HF_maps/b05_Added_pressures/p_{pressure}_{extent_str}_{purpose}_{year}_{scoring_template}_{res}m.tif'

            # Make a copy of the pressures in the results folder
            press_path_results = f'{results_folder}/p_{pressure}_{extent_str}_{purpose}_{year}_{scoring_template}_{res}m.tif'
            shutil.copy2(press_path, press_path_results)

            # Get pressure array annd add to HF
            press_raster = RASTER(press_path)

            # Get pressure raster array masked by NoData value
            nodata = press_raster.nodata
            press_raster.get_array()
            press_array = np.ma.masked_equal(press_raster.array, nodata)

            # Create and add pressures to final map
            if num != 0:
                datout = datout + press_array

            else:
                datout = press_array
                fn1 = press_path

            # Close pressure raster
            press_raster.close()
            press_array = None

            # Add 1 to num
            num += 1

    # Create the raster of added pressures if at least one topic was processed
    if num > 0:
        print('   Adding pressures')
        country = settings.country
        added_path = f'{results_folder}/HF_{country}_{extent_str}_{purpose}_{year}_{scoring_template}_{res}m.tif'
        # added_path_uncomp = f'{results_folder}/HF_{country}_{year}_{scoring_template}_{res}m_uncomp.tif'
        press_raster = RASTER(fn1)
        copy_raster(added_path, press_raster, Float=True, array=datout)
        press_raster.close()
        datout = None

        # Compress result and delete previous version
        compress(added_path)
        # os.remove(added_path_uncomp)

    return added_path


def preparing_folder(results_folder, settings, main_folder, res):

    print()
    print("""Masking water as no data, rounding to 2 decimals, 
adding metadata and creating pyramids""")

    # Open the river raster
    country_txt= settings.country[:2]
    extent = settings.extent_Polygon
    extent_str = extent.split('/')[-1].split('.')[-2]
    rivers_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{country_txt}_indirect_rivers_{res}m_rasterized.tif'
    river_raster = gdal.Open(rivers_path, gdal.GA_ReadOnly)
    if river_raster is None:
        print("Failed to open river raster.")
        return

    river_array = river_raster.GetRasterBand(1).ReadAsArray()
    goods = np.equal(river_array, 1)


    # Loop through all TIF files in the folder
    for file_name in os.listdir(results_folder):
        if file_name.endswith(".tif"):
            
            print(f'   {file_name}')
            tif_path = os.path.join(results_folder, file_name)

            # Mask water
            # Open the TIF raster
            tif_raster = gdal.Open(tif_path, gdal.GA_Update)
            if tif_raster is None:
                print(f"Failed to open TIF raster: {tif_path}")
                continue

            # Get the nodata value of the river raster
            nodata_value = tif_raster.GetRasterBand(1).GetNoDataValue()
            if nodata_value is None:
                print("Failed to retrieve nodata value from raster.")
                river_raster = None
                return

            # Get the number of raster bands
            num_bands = tif_raster.RasterCount

            # Loop through all bands in the TIF raster
            for band_index in range(1, num_bands + 1):
                band = tif_raster.GetRasterBand(band_index)
                # Read the band as a NumPy array
                array = band.ReadAsArray()
                # Modify the pixels based on the river raster
                array[goods] = nodata_value
                # Write the modified array back to the band
                band.WriteArray(array)

            tif_raster = None

            # Round to 2 decimals
            round_ = False
            with rasterio.open(tif_path, 'r+') as dataset:
                if dataset.dtypes[0] == 'float32':
                    round_ = True
                    # print(tif_path)
                    data = dataset.read(1)

                    # Round the array values to 2 decimal places
                    rounded_data = np.round(data, decimals=2)

                    # Create a new output file
                    profile = dataset.profile.copy()
                    profile.update(dtype=rasterio.float32)
            if round_:
                # Write the rounded data to the same file
                with rasterio.open(tif_path, 'w', **profile) as dst:
                    dst.write(rounded_data, 1)
                    
            # Add metadata
            with rasterio.open(tif_path, 'r+') as src:
                
                # Update the metadata tags
                src.update_tags(
                    Project="Maintaining Life on Land (SDG15) under Scenarios of Land Use and Climate Change in Colombia, Ecuador, and Peru",
                    Funding="NASA Biodiversity and Ecological Forecasting Program",
                    Institution="University of Northern British Columbia",
                    Title="Human Footprint series for SDG15",
                    License="CC-BY 4.0 license",
                    Cite='Before article publication please use: Jose Aragon-Osejo et al. (2024) Human Footprint maps for SDG15 indicators',
                    Date=datetime.today().strftime('%Y-%m-%d'),
                    Version='Preprint',
                    Author="Jose Aragon-Osejo",
                    Contact='aragon@unbc.ca / jose.luis.aragon.ec@gmail.com'
                )
                
            # Create pyramids
            with rasterio.open(tif_path, 'r+') as dataset:
                # if dataset.dtypes[0] == 'float32':
                #     resampling_method = rasterio.enums.Resampling.nearest
                # else:
                #     resampling_method = rasterio.enums.Resampling.nearest

                # dataset.build_overviews([2, 4, 8, 16], resampling=resampling_method)
                dataset.build_overviews([2, 4, 8, 16], resampling=rasterio.enums.Resampling.nearest)


    river_raster = None

