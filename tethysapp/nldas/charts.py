"""
Author: Riley Hales, 2018
Copyright: Riley Hales, RCH Engineering, 2019
Description: Functions for generating timeseries and simple statistical
    charts for netCDF data for point, bounding box, or shapefile geometries
"""
import calendar
import datetime as dt
import os
import shutil
import requests
import json

import rasterio
import rasterstats
import shapefile
import netCDF4
import numpy
import pandas as pd

from .options import nldas_variables
from .app import Nldas as App


def newchart(data):
    """
    Determines the environment for generating a timeseries chart. Call this function
    """
    # response metadata items
    meta = {
        'variable': data['variable'],
        'loc_type': data['loc_type']
    }
    for item in nldas_variables():
        if item[1] == data['variable']:
            meta['name'] = item[0]
            break

    # list then filter the available netcdfs
    path = os.path.join(App.get_custom_setting('thredds_path'), 'raw')
    allfiles = os.listdir(path)
    files = [i for i in allfiles if i.endswith('.nc4')]
    files.sort()

    # get the timeseries, units, and message based on location type
    if data['loc_type'] == 'Point':
        values, meta['units'], meta['seriesmsg'] = pointchart(data['variable'], data['coords'], path, files)
    elif data['loc_type'] == 'Polygon':
        values, meta['units'], meta['seriesmsg'] = polychart(data['variable'], data['coords'], path, files)
    else:  # loc_type == 'VectorGeometry':
        values, meta['units'], meta['seriesmsg'] = vectorchart(data['variable'], data['vectordata'], path,
                                                               files, data['instance_id'])

    if data['stats']:
        return {
            'meta': meta,
            'timeseries': values,
            'stats': makestatplots(values, data['time']),
        }
    else:
        return {
            'meta': meta,
            'timeseries': values,
        }


def geojson_to_shape(vectordata, savepath):
    # get the geojson data from esri
    base = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/'
    if vectordata.startswith('regions-'):
        vectordata = vectordata.replace('regions-', '')
        url = base + 'World_Regions/FeatureServer/0/query?f=pgeojson&outSR=4326&where=REGION+%3D+%27' + \
            vectordata + '%27'
    else:  # vectordata.startswith('countries-'):
        vectordata = vectordata.replace('countries-', '')
        url = base + 'World__Countries_Generalized_analysis_trim/FeatureServer/0/query?f=pgeojson&outSR=4326&' \
                     'where=NAME+%3D+%27' + vectordata + '%27'

    req = requests.get(url=url)
    geojson = json.loads(req.text)

    # create the shapefile
    fileobject = shapefile.Writer(target=savepath, shpType=shapefile.POLYGON, autoBalance=True)

    # label all the columns in the .dbf
    geomtype = geojson['features'][0]['geometry']['type']
    if geojson['features'][0]['properties']:
        for attribute in geojson['features'][0]['properties']:
            fileobject.field(str(attribute), 'C', '30')
    else:
        fileobject.field('Name', 'C', '50')

    # add the geometry and attribute data
    for feature in geojson['features']:
        if geomtype == 'Polygon':
            fileobject.poly(polys=feature['geometry']['coordinates'])
        elif geomtype == 'MultiPolygon':
            for i in feature['geometry']['coordinates']:
                fileobject.poly(polys=i)
        if feature['properties']:
            fileobject.record(**feature['properties'])
        else:
            fileobject.record(vectordata)

    # create a prj file
    with open(savepath + '.prj', 'w') as prj:
        prj.write('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
                  'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]')

    fileobject.close()
    return


def pointchart(var, coords, path, files):
    # return items
    timeseries = []

    # get a list of the lat/lon and units using a reference file
    nc_obj = netCDF4.Dataset(os.path.join(path, files[0]), 'r')
    nc_lons = nc_obj['lon'][:]
    nc_lats = nc_obj['lat'][:]
    units = nc_obj[var].__dict__['units']
    # get the index number of the lat/lon for the point
    lon_indx = (numpy.abs(nc_lons - round(float(coords[0]), 2))).argmin()
    lat_indx = (numpy.abs(nc_lats - round(float(coords[1]), 2))).argmin()
    nc_obj.close()

    # extract values at each timestep
    for nc in files:
        # get the time value for each file
        nc_obj = netCDF4.Dataset(os.path.join(path, nc), 'r')
        time = dt.datetime.strptime(nc, "NLDAS_FORA0125_H.A%Y%m%d.%H00.002.grb.SUB.nc4")
        print(time)
        # slice the array at the area you want
        val = float(nc_obj[var][0, lat_indx, lon_indx].data)
        timeseries.append((time, val))
        nc_obj.close()

    return timeseries, units, 'Values at a Point'


def polychart(var, coords, path, files):
    # return items
    values = []

    # get a list of the latitudes and longitudes and the units
    nc_obj = netCDF4.Dataset(os.path.join(path, str(files[0])), 'r')
    nc_lons = nc_obj['lon'][:]
    nc_lats = nc_obj['lat'][:]
    units = nc_obj[var].__dict__['units']
    # get a bounding box of the rectangle in terms of the index number of their lat/lons
    minlon = (numpy.abs(nc_lons - round(float(coords[0][1][0]), 2))).argmin()
    maxlon = (numpy.abs(nc_lons - round(float(coords[0][3][0]), 2))).argmin()
    maxlat = (numpy.abs(nc_lats - round(float(coords[0][1][1]), 2))).argmin()
    minlat = (numpy.abs(nc_lats - round(float(coords[0][3][1]), 2))).argmin()
    nc_obj.close()

    # extract values at each timestep
    for nc in files:
        # set the time value for each file
        nc_obj = netCDF4.Dataset(os.path.join(path, nc), 'r')
        time = dt.datetime.strptime(nc, "NLDAS_FORA0125_H.A%Y%m%d.%H00.002.grb.SUB.nc4")
        # slice the array, drop nan values, get the mean, append to list of values
        array = nc_obj[var][0, minlat:maxlat, minlon:maxlon].data
        array[array < -5000] = numpy.nan  # If you have fill values, change the comparator to git rid of it
        array = array.flatten()
        array = array[~numpy.isnan(array)]
        values.append((time, float(array.mean())))

        nc_obj.close()

    return values, units, 'In a Bounding Box'


def vectorchart(var, vectordata, path, files, instance_id=None):
    # return items
    values = []

    # open the netcdf and get metadata
    nc_obj = netCDF4.Dataset(os.path.join(path, files[0]), 'r')
    lat = nc_obj.variables['lat'][:]
    lon = nc_obj.variables['lon'][:]
    units = nc_obj[var].__dict__['units']
    affine = rasterio.transform.from_origin(lon.min(), lat.max(), lat[1] - lat[0], lon[1] - lon[0])
    nc_obj.close()

    # file paths and settings
    if vectordata == 'customshape':
        type_message = 'Average in user\'s shapefile'
        dirpath = os.path.join(os.path.dirname(__file__), 'workspaces', 'user_workspaces', instance_id)
        shp = [i for i in os.listdir(dirpath) if i.endswith('.shp')]
        vectorpath = os.path.join(dirpath, shp[0])
    else:  # vectordata.startswith('esri-'):
        type_message = 'Average for ' + vectordata.replace('esri-countries-', '').replace('esri-regions-', '')
        vectordata = vectordata.replace('esri-', '')
        dirpath = os.path.join(os.path.dirname(__file__), 'workspaces', 'user_workspaces', instance_id)
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.mkdir(dirpath)
        vectorpath = os.path.join(dirpath, instance_id)
        geojson_to_shape(vectordata, vectorpath)
        vectorpath += '.shp'

    # extract the timeseries by iterating over each netcdf
    for nc in files:
        # open the netcdf and get the data array
        nc_obj = netCDF4.Dataset(os.path.join(path, nc), 'r')
        time = dt.datetime.strptime(nc, "NLDAS_FORA0125_H.A%Y%m%d.%H00.002.grb.SUB.nc4")

        var_data = nc_obj.variables[var][:]  # this is the array of values for the nc_obj
        array = numpy.asarray(var_data)[0, :, :]  # converting the data type
        array[array < -9000] = numpy.nan  # use the comparator to drop nodata fills
        array = array[::-1]  # vertically flip array so tiff orientation is right (you just have to, try it)

        stats = rasterstats.zonal_stats(vectorpath, array, affine=affine, nodata=numpy.nan, stats="mean")
        tmp = [i['mean'] for i in stats if i['mean'] is not None]
        values.append((time, sum(tmp) / len(tmp)))

        nc_obj.close()

    return values, units, type_message


def makestatplots(values, time):
    df = pd.DataFrame(values, columns=['timestamp', 'values']).set_index('timestamp')
    months = dict((n, m) for n, m in enumerate(calendar.month_name))
    yearmulti = []
    monthmulti = []
    yearbox = []
    monthbox = []

    if time == 'alltimes':
        ref_yr = 1948
        numyears = int(dt.datetime.now().strftime("%Y")) - ref_yr + 1  # +1 because we want the first year also
    else:
        ref_yr = int(time.replace('s', ''))
        numyears = 10
    years = [str(i + ref_yr) for i in range(numyears)]

    for i in range(1, 13):
        tmp = df[df.index.month == i]['values']
        ymin = min(tmp)
        ymax = max(tmp)
        mean = sum(tmp) / len(tmp)
        monthbox.append((months[i], tmp.to_list()))
        monthmulti.append((months[i], ymin, mean, ymax))
    for year in years:
        tmp = df[year]['values']
        ymin = min(tmp)
        ymax = max(tmp)
        mean = sum(tmp) / len(tmp)
        yearbox.append((year, tmp.to_list()))
        yearmulti.append((year, ymin, mean, ymax))

    return yearmulti, monthmulti, yearbox, monthbox
