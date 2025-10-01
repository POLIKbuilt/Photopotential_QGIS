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
    project.addMapLayer(raster_layer)
    print("Raster layer loaded successfully")
    print("DSM CRS:", raster_layer.crs().authid())
    rsun_apply(raster_path)
    # basic_layer_set(main_layer)
else:
    print("Raster layer is not valid")



