from qgis.core import (
    QgsApplication,
    QgsRasterLayer,
    QgsProject
)

qgs = QgsApplication([], False)
qgs.initQgis()

raster_path = "../data/test_raster.tif"

raster_layer = QgsRasterLayer(raster_path, "Elevation")

if not raster_layer.isValid():
    print("Raster layer is not valid")
else:
    QgsProject.instance().addMapLayer(raster_layer)
    print("Raster layer loaded")

qgs.exitQgis()


