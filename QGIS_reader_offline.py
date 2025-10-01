# Copy for in QGIS testing

import os
import processing
from qgis.core import *


file_path = os.path.dirname(QgsProject.instance().fileName())
raster_path = os.path.join(file_path, "data/test_raster.tif")
layer_name = "test layer"
raster_layer = QgsRasterLayer(raster_path, layer_name)
vector_layer = QgsVectorLayer(raster_path, layer_name) # dont't work, not shp file

def rsun_apply(rpath):
    sun_map = processing.run("grass7:r.sun", {
        'elevation': rpath,  # input DSM
        'day': 180,      # day of year
        'time': 12.0,    # solar time (hour)
        'latitude': 45.0,
        'longitude': 7.0,
        'output': r"data/sun_radiation.tif",  # output raster
        'GRASS_REGION_PARAMETER': None,
        'GRASS_REGION_CELLSIZE_PARAMETER': 0,
        'GRASS_RASTER_FORMAT_OPT': None,
        'GRASS_RASTER_FORMAT_META': 0
    })
    return sun_map

def render_set(layer, azimuth, altitude):
    if layer and layer.isValid():
        print("Rerendering: ", layer.name())
    else:
        print("Layer is invalid or has been deleted.")
    input_layer = layer.dataProvider()
    renderer = QgsHillshadeRenderer( input_layer, 1, azimuth, altitude)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

def basic_layer_set(layer):
    layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
    layer.renderer().setOpacity(0)
    layer.resampleFilter().setZoomedInResampler(QgsBilinearRasterResampler())
    layer.resampleFilter().setZoomedOutResampler(QgsBilinearRasterResampler())

if raster_layer.isValid():
    project = QgsProject.instance()
    for layer in project.mapLayers().values():
        if layer.name() == layer_name:
            project.removeMapLayer(layer.id())
    print("Cleaning project...")
    main_layer = project.addMapLayer(raster_layer)
    print("Raster layer loaded successfully")
    print("DSM CRS:", raster_layer.crs().authid())
    # print("Sun layer check", rsun_apply(raster_path)['output'])
    # basic_layer_set(main_layer)
    render_set(main_layer, 315, 45)
else:
    print("Raster layer is not valid")



