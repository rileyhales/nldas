from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting
from tethys_sdk.app_settings import SpatialDatasetServiceSetting


class Nldas(TethysAppBase):
    """
    Tethys app class for NLDAS Data Tool.
    """

    name = 'NLDAS Data Tool'
    index = 'nldas:home'
    icon = 'nldas/images/nldaslogo.png'
    package = 'nldas'
    root_url = 'nldas'
    color = '#478cfc'
    description = 'A tool providing animated mapping, timeseries chart generation, and api access to NLDAS data as ' \
                  'subset from the NASA GESDISC repository.'
    tags = ''
    enable_feedback = False
    feedback_emails = []
    githublink = 'https://github.com/rileyhales/nldas'
    docslink = 'https://nldas-data-tool.readthedocs.io/en/latest/api.html'
    datawebsite = 'https://disc.gsfc.nasa.gov/datasets/NLDAS_FORA0125_H_002/summary?keywords=nldas'
    version = 'v3 Sep19'

    def url_maps(self):
        """
        Add controllers
        """
        urlmap = url_map_maker(self.root_url)

        return (
            # url maps to navigable pages
            urlmap(
                name='home',
                url='nldas',
                controller='nldas.controllers.home'
            ),

            # url maps for ajax calls
            urlmap(
                name='getChart',
                url='nldas/ajax/getChart',
                controller='nldas.ajax.getchart',
            ),
            urlmap(
                name='uploadShapefile',
                url='nldas/ajax/uploadShapefile',
                controller='nldas.ajax.uploadshapefile',
            ),

            # url maps for api calls
            # urlmap(
            #     name='helpme',
            #     url='nldas/api/help',
            #     controller='nldas.api.helpme',
            # ),
            # urlmap(
            #     name='timeseries',
            #     url='nldas/api/timeseries',
            #     controller='nldas.api.timeseries',
            # ),
        )

    def custom_settings(self):
        return (
            CustomSetting(
                name='thredds_path',
                type=CustomSetting.TYPE_STRING,
                description="Local file path to datasets (same as used by Thredds) (e.g. /home/thredds/myDataFolder/)",
                required=True,
            ),
            CustomSetting(
                name='thredds_url',
                type=CustomSetting.TYPE_STRING,
                description="URL to the nldas folder on the thredds server (e.g. http://[host]/thredds/nldas/)",
                required=True,
            )
        )

    def spatial_dataset_service_settings(self):
        """
        Example spatial_dataset_service_settings method.
        """
        return (
            SpatialDatasetServiceSetting(
                name='geoserver',
                description='Geoserver for serving user uploaded shapefiles',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True,
            ),
        )