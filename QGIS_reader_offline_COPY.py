# Copy for in QGIS testing

import os
# import processing
from qgis.core import *


file_path = os.path.dirname(QgsProject.instance().fileName())

raster_path = os.path.join(file_path, "data/test_raster.tif")
layer_name = "first layer"
raster_layer = QgsRasterLayer(raster_path, layer_name)
vector_layer = QgsVectorLayer(raster_path, layer_name)

"""
sun_map = processing.run("grass7:r.sun", {
    'elevation': r"data/test_raster.tif",  # input DEM
    'aspect': None,
    'slope': None,
    'linke': None,
    'albedo': None,
    'latin': 45.0,   # latitude
    'longin': 7.0,   # longitude
    'day': 180,      # day of year
    'time': 12.0,    # solar time (hour)
    'step': 0.5,
    'nsteps': 1,
    'distance': 1,
    'output': r"data/sun_radiation.tif",  # output raster
    'GRASS_REGION_PARAMETER': None,
    'GRASS_REGION_CELLSIZE_PARAMETER': 0,
    'GRASS_RASTER_FORMAT_OPT': '',
    'GRASS_RASTER_FORMAT_META': ''
})
"""

def basic_layer_set(layer):
    layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
    layer.renderer().setOpacity(0.5)
    layer.resampleFilter().setZoomedInResampler(QgsBilinearRasterResampler())
    layer.resampleFilter().setZoomedOutResampler(QgsBilinearRasterResampler())

if raster_layer.isValid():
    main_layer = QgsProject.instance().addMapLayer(raster_layer)
    print("Raster layer loaded")
    basic_layer_set(main_layer)
else:
    print("Raster layer is not valid")



