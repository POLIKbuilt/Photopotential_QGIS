import os
from constants import *
from qgis.core import *
from pyproj import Transformer
from osgeo import gdal
import grass.script as gscript
import grass.script.setup as gsetup

# WMS working, only needs correct data
wms_url = "crs=EPSG:4326&dpiMode=7&format=image/png&layers=0&styles&url=https://zbgisws.skgeodesy.sk/zbgis_dmr_wms/service.svc/get"
# wms_url = "crs=EPSG:3857&dpiMode=7&format=image/png&layers=0&styles&url=https://ags.nrc.sk/arcgis/services/Rastry/DMR5G/MapServer/WMSServer?"

# new boxing coordinates (two points)
X1, Y1 = 48.126167, 17.085511
X2, Y2 = 48.114157, 17.095793

def init_qgis_app(): 
    app = QgsApplication([], True)
    app.initQgis()
    print("QGIS app initialized")
    return app

def wms_layer_load(layer):
    data_layer = QgsRasterLayer(layer, LAYER_NAME, "wms")
    if data_layer.isValid():
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer.name() == LAYER_NAME:
                project.removeMapLayer(layer.id())
        print("Cleaning project...")
        # project.addMapLayer(data_layer)
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

def qgis_cropping(x1, y1, x2, y2, layer, output_path, crs = "EPSG:4326"):
    bbox = (y1, x1, y2, x2)
    clipbox = QgsRectangle(bbox[0], bbox[1], bbox[2], bbox[3])
    layer.setExtent(clipbox)
    QgsProject.instance().addMapLayer(layer)
    crs_obj = QgsCoordinateReferenceSystem(crs)
    provider = layer.dataProvider()
    pipe = QgsRasterPipe()
    pipe.set(provider.clone())
    writer = QgsRasterFileWriter(output_path)
    writer.setOutputFormat("GTiff")
    result = writer.writeRaster(pipe, provider.xSize(), provider.ySize(), provider.extent() ,crs_obj)
    if result != QgsRasterFileWriter.NoError:
        raise Exception(f"Raster writing failed >>> Code: {result}")

def load_output(layer_path):
    data_layer = QgsRasterLayer(layer_path, "output")
    if data_layer.isValid():
        QgsProject.instance().addMapLayer(data_layer)
        print("output.tif loaded >>>")
    else:
        raise Exception(f"Layer is invalid!!! Check layer file >>> {OUTPUT_LAYER}")

def wms_run():
    wms_layer = wms_layer_load(wms_url)
    qgis_cropping(X1, Y1, X2, Y2, wms_layer, OUTPUT_LAYER)
    render_set(wms_layer, 315, 45)
    load_output(OUTPUT_LAYER)

wms_run()
