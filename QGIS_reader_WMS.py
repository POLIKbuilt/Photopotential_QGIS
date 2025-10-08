from constants import *
from qgis.core import *
from qgis.gui import QgsMapCanvas
from pyproj import Transformer 

# WMS working, only needs correct data
wms_url = "crs=CRS:84&dpiMode=7&format=image/png&layers=0&styles&url=https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get"
wms_layer = QgsRasterLayer(wms_url, LAYER_NAME, "wms")

def init_qgis_app(): 
    app = QgsApplication([], False)
    app.initQgis()
    return app

def cords_to_xy(lon, lat): 
    transformer = Transformer.from_crs("EPSG:4326", "CSR:84", always_xy = True)
    x, y = transfromer.transfrom(lon, lat)
    return x, y
    
def render_set(layer, azimuth, altitude):
    if layer and layer.isValid():
        print("Rerendering: ", layer.name())
    else:
        print("Layer is invalid or has been deleted.")
    input_layer = layer.dataProvider()
    renderer = QgsHillshadeRenderer( input_layer, 1, azimuth, altitude)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

def coordinate_boxing(xMin, xMax, yMin, yMax):
    extender = QgsRectangle(xMin, yMin, xMax, yMax)
    iface.mapCanvas().setExtent(extender)
    iface.mapCanvas().refresh()


if wms_layer.isValid():
    project = QgsProject.instance()
    for layer in project.mapLayers().values():
        if layer.name() == layer_name:
            project.removeMapLayer(layer.id())
    print("Cleaning project...")
    working_layer = project.addMapLayer(wms_layer)
    print("WMS loaded successfully")
    render_set(working_layer, 315, 45)
    coordinate_boxing(823000, 5930000, 833000, 5940000)
else:
    print("WMS failed")

