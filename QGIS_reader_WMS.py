from qgis.core import *

wms_url = "crs=CRS:84&dpiMode=7&format=image/png&layers=2&styles&url=https://zbgisws.skgeodesy.sk/zbgis_administrativne_hranice_wms_featureinfo/service.svc/get"
wms_layer = QgsRasterLayer(wms_url, "WMS Example", "wms")

if wms_layer.isValid():
    QgsProject.instance().addMapLayer(wms_layer)
    print("WMS done")
else:
    print("WMS failed")

