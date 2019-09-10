////////////////////////////////////////////////////////////////////////  MAP FUNCTIONS
function map() {
    // create the map
    return L.map('map', {
        zoom: 3,
        minZoom: 2,
        zoomSnap: .5,
        boxZoom: true,
        maxBounds: L.latLngBounds(L.latLng(0.0, -140.0), L.latLng(60.0, -40.0)),
        center: [39.5, -105],
        timeDimension: true,
        timeDimensionControl: true,
        timeDimensionControlOptions: {
            position: "bottomleft",
            autoPlay: true,
            loopButton: true,
            backwardButton: true,
            forwardButton: true,
            timeSliderDragUpdate: true,
            minSpeed: 2,
            maxSpeed: 6,
            speedStep: 1,
        },
    });
}

function basemaps() {
    // create the basemap layers
    let esri_imagery = L.esri.basemapLayer('Imagery');
    let esri_terrain = L.esri.basemapLayer('Terrain');
    let esri_labels = L.esri.basemapLayer('ImageryLabels');
    return {
        "ESRI Imagery (No Label)": L.layerGroup([esri_imagery]).addTo(mapObj),
        "ESRI Imagery (Labeled)": L.layerGroup([esri_imagery, esri_labels]),
        "ESRI Terrain": L.layerGroup([esri_terrain, esri_labels])
    }
}

////////////////////////////////////////////////////////////////////////  GLDAS LAYERS
function newGLDAS() {
    let layer = $("#variables").val();
    let cs_rng = bounds[layer];
    if ($("#use_csrange").is(":checked")) {
        cs_rng = String($("#cs_min").val()) + ',' + String($("#cs_max").val())
    }

    let wmsLayer = L.tileLayer.wms(threddsbase, {
        // version: '1.3.0',
        layers: layer,
        dimension: 'time',
        useCache: true,
        crossOrigin: false,
        format: 'image/png',
        transparent: true,
        opacity: $("#opacity_raster").val(),
        BGCOLOR: '0x000000',
        styles: 'boxfill/' + $('#colorscheme').val(),
        colorscalerange: cs_rng,
    });

    return L.timeDimension.layer.wms(wmsLayer, {
        name: 'time',
        requestTimefromCapabilities: true,
        updateTimeDimension: true,
        updateTimeDimensionMode: 'replace',
        cache: 20,
    }).addTo(mapObj);
}

////////////////////////////////////////////////////////////////////////  GEOJSON STYLING CONTROLS
let chosenRegion = ''; // tracks which region is on the chart for updates not caused by the user picking a new region
getStyle = function() {return {color: $("#gjClr").val(), opacity: $("#gjOp").val(), weight: $("#gjWt").val(), fillColor: $("#gjFlClr").val(), fillOpacity: $("#gjFlOp").val()}};
function styleGeoJSON() {
    usershape.setStyle(getStyle());
}

////////////////////////////////////////////////////////////////////////  USER'S CUSTOM UPLOADED SHAPEFILE
// gets the geojson layers from geoserver wfs and updates the layer
let usershape = L.geoJSON(false);
function getGeoServerGJ(gsworksp, shpname, gsurl) {
    let parameters = L.Util.extend({
        service: 'WFS',
        version: '1.0.0',
        request: 'GetFeature',
        typeName: gsworksp + ':' + shpname,
        maxFeatures: 10000,
        outputFormat: 'application/json',
        parseResponse: 'getJson',
        srsName: 'EPSG:4326',
        crossOrigin: 'anonymous'
    });
    $.ajax({
        async: true,
        jsonp: false,
        url: gsurl + L.Util.getParamString(parameters),
        contentType: 'application/json',
        success: function (data) {
            usershape.clearLayers();
            mapObj.removeLayer(drawnItems);
            usershape.addData(data).addTo(mapObj);
            styleGeoJSON();
            mapObj.flyToBounds(usershape.getBounds());
        },
    });
}

////////////////////////////////////////////////////////////////////////  LEGEND DEFINITIONS
let legend = L.control({position: 'topright'});
legend.onAdd = function () {
    let layer = $("#variables").val();
    let cs_rng = bounds[layer];
    if ($("#use_csrange").is(":checked")) {
        cs_rng = String($("#cs_min").val()) + ',' + String($("#cs_max").val())
    }

    let div = L.DomUtil.create('div', 'legend');
    let url = threddsbase + "?REQUEST=GetLegendGraphic&LAYER=" + layer + "&PALETTE=" + $('#colorscheme').val() + "&COLORSCALERANGE=" + cs_rng;
    div.innerHTML = '<img src="' + url + '" alt="legend" style="width:100%; float:right;">';
    return div
};

let latlon = L.control({position: 'bottomleft'});
latlon.onAdd = function () {
    let div = L.DomUtil.create('div', 'well well-sm');
    div.innerHTML = '<div id="mouse-position" style="text-align: center"></div>';
    return div;
};

////////////////////////////////////////////////////////////////////////  MAP CONTROLS AND CLEARING
// the layers box on the top right of the map
function makeControls() {
    return L.control.layers(basemapObj, {
        'Earth Observation': layerGLDAS,
        'Drawing': drawnItems,
        'Uploaded Shapefile': usershape,
        'Region Boundaries': layerRegion,
    }).addTo(mapObj);
}

// you need to remove layers when you make changes so duplicates dont persist and accumulate
function clearMap() {
    controlsObj.removeLayer(layerGLDAS);
    mapObj.removeLayer(layerGLDAS);
    controlsObj.removeLayer(usershape);
    controlsObj.removeLayer(layerRegion);
    mapObj.removeControl(controlsObj);
}
