from qgis.core import *

qgs = QgsApplication([], False)
qgs.initQgis()

wms_url = (
    "contextualWMSLegend=0&"
    "crs=EPSG:3857&"
    "format=image/png&"
    "layers=ne:NE1_HR_LC_SR_W_DR&"
    "url=https://zbgisws.skgeodesy.sk/zbgis_wms_featureinfo/service.svc/get"
)

wms_layer = QgsRasterLayer(wms_url, "WMS Example", "wms")

if wms_layer.isValid():
    QgsProject.instance().addMapLayer(wms_layer)
    print("WMS done")
else:
    print("WMS failed")

qgs.exitQgis()
