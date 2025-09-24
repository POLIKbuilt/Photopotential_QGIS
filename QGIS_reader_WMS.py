from qgis.core import (
    QgsApplication,
    QgsRasterLayer,
    QgsProject
)

qgs = QgsApplication([], False)
qgs.initQgis()

wms_url = "To be added"

wms_layer = QgsRasterLayer(wms_url, "WMS Example", "wms")

if not wms_layer.isValid():
    print("MWS Failed")
else:
    QgsProject.instance().addMapLayer(wms_layer)
    print("WMS Loaded")

qgs.exitQgis()
