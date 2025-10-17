# Copy for in QGIS testing
import os
from qgis.core import *
from constants import *

file_path = os.path.dirname(QgsProject.instance().fileName())
raster_path = os.path.join(file_path, "data\output.tif")
raster_layer = QgsRasterLayer(raster_path, LAYER_NAME)
vector_layer = QgsVectorLayer(raster_path, LAYER_NAME) # dont't work, not shp file

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
        if layer.name() == LAYER_NAME:
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



