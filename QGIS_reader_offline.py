import os
from qgis.core import *

qgs = QgsApplication([], False)
qgs.initQgis()

file_path = os.path.dirname(os.path.realpath(__file__))
raster_path = os.path.join(file_path, "data/test_raster.tif")

raster_layer = QgsRasterLayer(raster_path, "Elevation")

if raster_layer.isValid():
    QgsProject.instance().addMapLayer(raster_layer)
    print("Raster layer loaded")
else:
    print("Raster layer is not valid")

qgs.exitQgis()


