# -*- coding: utf-8 -*-


def nldas_variables():
    return [('Precipitation hourly total [kg/m^2]', 'APCP'),
            ('180-0 mb above ground Convective Available Potential Energy [J/kg]', 'CAPE'),
            ('Fraction of total precipitation that is convective [unitless]', 'CONVfrac'),
            ('Longwave radiation flux downwards (surface) [W/m^2]', 'DLWRF'),
            ('Shortwave radiation flux downwards (surface) [W/m^2]', 'DSWRF'),
            ('Potential evaporation hourly total [kg/m^2]', 'PEVAP'),
            ('Surface pressure [Pa]', 'PRES'),
            ('2-m above ground Specific humidity [kg/kg]', 'SPFH'),
            ('2-m above ground Temperature [K]', 'TMP'),
            ('10-m above ground Zonal wind speed [m/s]', 'UGRD'),
            ('10-m above ground Meridional wind speed [m/s]', 'VGRD')]


def wms_colors():
    return [('SST-36', 'sst_36'),
            ('Greyscale', 'greyscale'),
            ('Rainbow', 'rainbow'),
            ('OCCAM', 'occam'),
            ('OCCAM Pastel', 'occam_pastel-30'),
            ('Red-Blue', 'redblue'),
            ('NetCDF Viewer', 'ncview'),
            ('ALG', 'alg'),
            ('ALG 2', 'alg2'),
            ('Ferret', 'ferret')]


def geojson_colors():
    return [('White', '#ffffff'),
            ('Transparent', 'rgb(0,0,0,0)'),
            ('Red', '#ff0000'),
            ('Green', '#00ff00'),
            ('Blue', '#0000ff'),
            ('Black', '#000000'),
            ('Pink', '#ff69b4'),
            ('Orange', '#ffa500'),
            ('Teal', '#008080'),
            ('Purple', '#800080')]


def onion_creek_events():
    return [('2013 Event', '2013event'),
            ('2015 Event', '2015event'),
            ('2018 Event', '2018event')]
