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

def create_extent(x1, y1, x2, y2):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x_min, y_min = transformer.transform(y2, x2)  # note swapped order lon,lat
    x_max, y_max = transformer.transform(y1, x1)
    return [x_min, y_max, x_max, y_min]

def wms_layer_load(layer):
    data_layer = QgsRasterLayer(layer, LAYER_NAME, "wms")
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

def cropping(box):
    # center_x, center_y = cords_to_xy(lat, lon)
    # half = radius / 2
    # box = QgsRectangle(center_x - half, center_y - half, center_x + half, center_y + half)
    src = "WMS:https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get"
    ds = gdal.Open(src)
    if ds is None:
        raise RuntimeError("Failed to open WMS source. Check URL and GDAL WMS driver.")
    else:
        print("WMS connection successful:", ds.RasterXSize, ds.RasterYSize)
    crop = gdal.Translate(destName = OUTPUT_LAYER, srcDS = src, projWin = box, projWinSRS="EPSG:3857", format = "GTiff")
    if crop is None:
        raise RuntimeError("GDAL failed (NULL pointer)!!!")
    crop = None
    print(f"DSM saved to: {OUTPUT_LAYER}")

def load_layer(layer_path):
    data_layer = QgsRasterLayer(layer_path, "output.tif")
    if data_layer.isValid():
        QgsProject.instance().addMapLayer(data_layer)
        print("output.tif loaded >>>")
    else:
        raise Exception(f"Layer is invalid!!! Check layer file {OUTPUT_LAYER}")


def wms_run():
    wms_layer_load(wms_url)
    box = [X1, Y1, X2, Y2]
    print("Box (EPSG:3857):", box)
    cropping(box)
    load_layer(OUTPUT_LAYER)

wms_run()