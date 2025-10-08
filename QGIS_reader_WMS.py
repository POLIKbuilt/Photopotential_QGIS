from constants import *
from qgis.core import *
from qgis.gui import QgsMapCanvas
from pyproj import Transformer 

# WMS working, only needs correct data
wms_url = "crs=CRS:84&dpiMode=7&format=image/png&layers=0&styles&url=https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get"

def init_qgis_app(): 
    app = QgsApplication([], False)
    app.initQgis()
    return app

def wms_layer_load(): 
    wms_layer = QgsRasterLayer(wms_url, LAYER_NAME, "wms")
    if wms_layer.isValid():
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer.name() == LAYER_NAME:
                project.removeMapLayer(layer.id())
        print("Cleaning project...")
        project.addMapLayer(wms_layer)
        print("WMS loaded successfully")
        return wms_layer
    else:
        raise Exception("WMS layer loading failed")

def cords_to_xy(lat, lon): 
    trn = Transformer.from_crs("EPSG:4326", "CSR:84", always_xy = True)
    x, y = trn.transfrom(lon, lat)
    return x, y
    
def render_set(layer, azimuth, altitude):
    if layer and layer.isValid():
        print("Rerendering: ", layer.name())
    else:
        print("Layer is invalid or has been deleted.")
    input_layer = layer.dataProvider()
    renderer = QgsHillshadeRenderer(input_layer, 1, azimuth, altitude)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

def boxing(lat, lon, radius):
    center_x, center_y = cords_to_xy(lat, lon)
    half = radius / 2
    box = QgsRectangle(center_x - half, center_y - half, center_x + half, center_y + half)
    canvas = iface.mapCanvas()
    canvas.setExtent(box)
    canvas.refresh

def wms_run():
    dsm_layer = wms_layer_load()
    render_set(dsm_layer, 315, 45)
    boxing(ZONE_LAT, ZONE_LON, BOX_RADIUS)
