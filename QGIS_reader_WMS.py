from constants import *
from qgis.core import *
from pyproj import Transformer
from osgeo import gdal

# WMS working, only needs correct data
wms_url = "crs=EPSG:4326&dpiMode=7&format=image/png&layers=0&styles&url=https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get"
# wms_url = "crs=EPSG:3857&dpiMode=7&format=image/png&layers=0&styles&url=https://ags.nrc.sk/arcgis/services/Rastry/DMR5G/MapServer/WMSServer?"

def init_qgis_app(): 
    app = QgsApplication([], True)
    app.initQgis()
    print("QGIS app initialized")
    return app

def wms_layer_load(layer):
    data_layer = QgsRasterLayer(layer, LAYER_NAME)
    if data_layer.isValid():
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer.name() == LAYER_NAME:
                project.removeMapLayer(layer.id())
        print("Cleaning project...")
        project.addMapLayer(data_layer)
        print("WMS loaded successfully")
        return data_layer
    else:
        raise Exception("WMS layer loading failed")
    
def render_set(layer, azimuth, altitude):
    if layer and layer.isValid():
        print("Rerendering: ", layer.name())
    else:
        print("Layer is invalid or has been deleted.")
    input_layer = layer.dataProvider()
    renderer = QgsHillshadeRenderer(input_layer, 1, azimuth, altitude)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

def boxing(lat, lon, radius, layer, output):
    center_x, center_y = cords_to_xy(lat, lon)
    half = radius / 2
    box = QgsRectangle(center_x - half, center_y - half, center_x + half, center_y + half)
    src = layer.dataProvider().dataSourceUri()
    gdal.Translate(destName = output, srcDS = src, projWin = [box.xMinimum(), box.yMinimum(), box.xMaximum(), box.yMaximum()], format = "GTiff")
    print(f"DSM saved to: {output}")

def wms_run():
    dsm_layer = wms_layer_load(wms_url)
    render_set(dsm_layer, 315, 45)
    boxing(ZONE_LAT, ZONE_LON, 5000, dsm_layer, OUTPUT_LAYER)
    cut_layer = wms_layer_load(OUTPUT_LAYER, LAYER_NAME)

wms_run()