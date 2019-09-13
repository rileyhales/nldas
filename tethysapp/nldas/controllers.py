from django.shortcuts import render
from tethys_sdk.gizmos import SelectInput, RangeSlider

from .app import Nldas as App
from .options import nldas_variables, wms_colors, geojson_colors, onion_creek_events
from .utilities import new_id


def home(request):
    """
    Controller for the app home page.
    """
    variables = SelectInput(
        display_text='Select NLDAS Variable',
        name='variables',
        multiple=False,
        original=True,
        options=nldas_variables(),
    )
    events = SelectInput(
        display_text='Pick an Event',
        name='events',
        multiple=False,
        original=True,
        options=onion_creek_events(),
    )

    colorscheme = SelectInput(
        display_text='NLDAS Color Scheme',
        name='colorscheme',
        multiple=False,
        original=True,
        options=wms_colors(),
        initial='rainbow'
    )

    opacity = RangeSlider(
        display_text='NLDAS Layer Opacity',
        name='opacity',
        min=.5,
        max=1,
        step=.05,
        initial=1,
    )

    gj_color = SelectInput(
        display_text='Boundary Border Colors',
        name='gjClr',
        multiple=False,
        original=True,
        options=geojson_colors(),
        initial='#ffffff'
    )

    gj_opacity = RangeSlider(
        display_text='Boundary Border Opacity',
        name='gjOp',
        min=0,
        max=1,
        step=.1,
        initial=1,
    )

    gj_weight = RangeSlider(
        display_text='Boundary Border Thickness',
        name='gjWt',
        min=1,
        max=5,
        step=1,
        initial=2,
    )

    gj_fillcolor = SelectInput(
        display_text='Boundary Fill Color',
        name='gjFlClr',
        multiple=False,
        original=True,
        options=geojson_colors(),
        initial='rgb(0,0,0,0)'
    )

    gj_fillopacity = RangeSlider(
        display_text='Boundary Fill Opacity',
        name='gjFlOp',
        min=0,
        max=1,
        step=.1,
        initial=.5,
    )

    context = {
        # data options
        'variables': variables,
        'events': events,

        # display options
        'colorscheme': colorscheme,
        'opacity': opacity,
        'gjClr': gj_color,
        'gjOp': gj_opacity,
        'gjWt': gj_weight,
        'gjFlClr': gj_fillcolor,
        'gjFlOp': gj_fillopacity,

        # metadata
        'app': App.package,
        'githublink': App.githublink,
        'datawebsite': App.datawebsite,
        'version': App.version,
        'thredds_url': App.get_custom_setting('thredds_url'),
        'instance_id': new_id(),
    }

    return render(request, 'nldas/home.html', context)
