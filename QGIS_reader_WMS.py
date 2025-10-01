from qgis.core import *
from QGIS_reader_offline import render_set

# WMS working, only needs correct data
layer_name = "WMS_layer"
wms_url = "crs=CRS:84&dpiMode=7&format=image/png&layers=0&styles&url=https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get"
wms_layer = QgsRasterLayer(wms_url, layer_name, "wms")

if wms_layer.isValid():
    project = QgsProject.instance()
    for layer in project.mapLayers().values():
        if layer.name() == layer_name:
            project.removeMapLayer(layer.id())
    print("Cleaning project...")
    working_layer = project.addMapLayer(wms_layer)
    print("WMS loaded successfully")
    render_set(working_layer, 315, 45)
else:
    print("WMS failed")

