import os
from constants import *
from qgis.core import *
from pyproj import Transformer
from osgeo import gdal
import grass.script as gscript
import grass.script.setup as gsetup

from qgis.PyQt.QtGui import QImage
from qgis.PyQt.QtCore import QSize

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

def qgis_cropping(x1, y1, x2, y2, layer):
    bbox = (y1, x1, y2, x2)
    clipbox = QgsRectangle(bbox[0], bbox[1], bbox[2], bbox[3])
    layer.setExtent(clipbox)
    QgsProject.instance().addMapLayer(layer)

def raster_to_tif(layer_name, output_path):
    project = QgsProject.instance()
    layers = project.mapLayersByName(layer_name)
    if not layers:
        raise Exception(f"Layer '{layer_name}' not found")
    layer = layers[0]

    if not layer.isValid():
        raise Exception("Layer is not valid")
    print(f"Found >>> {layer.name()}")

    provider = layer.dataProvider()
    print("Width", provider.xSize())
    pipe = QgsRasterPipe()
    if not pipe.set(provider.clone()):
        raise Exception("WMS provider >>> Raster pipe failed")
    writer = QgsRasterFileWriter(output_path)
    writer.setOutputFormat("GTiff")
    extent = layer.extent()
    crs = layer.crs()
    print(f"Layer CRS >>> {crs.authid()}")
    print(f"Extent >>> {extent.toString()}")
    width = 1024
    height = 1024
    print(f"Raster dimensions >>> {width} x {height}")
    result = writer.writeRaster( pipe, width, height, extent, QgsCoordinateReferenceSystem(crs))
    if result != QgsRasterFileWriter.NoError:
        raise Exception(f"Raster writing failed >>> Code: {result}")
    print(f"Layer saved to >>> {output_path}")

def load_output(layer_path):
    data_layer = QgsRasterLayer(layer_path, "output")
    if data_layer.isValid():
        QgsProject.instance().addMapLayer(data_layer)
        print("output.tif loaded >>>")
    else:
        raise Exception(f"Layer is invalid!!! Check layer file >>> {OUTPUT_LAYER}")

def save_visible_map_to_tif(output_path: str, width: int = 2048, height: int = 2048):
    """
    Saves the currently visible map area in QGIS (what's on screen)
    to a GeoTIFF file using QgsRasterFileWriter.
    No cropping, no GDAL, no processing — just the visible view.

    Parameters
    ----------
    output_path : str
        Path to output GeoTIFF file
    width : int
        Image width in pixels
    height : int
        Image height in pixels
    """
    # ----------------------------
    # 1️⃣ Access current QGIS project and layers
    # ----------------------------
    project = QgsProject.instance()
    layers = [lyr for lyr in project.mapLayers().values() if lyr.isValid()]

    if not layers:
        raise Exception("❌ No valid layers loaded in the project.")

    print(f"✅ Found {len(layers)} valid layers to render.")

    # ----------------------------
    # 2️⃣ Prepare map settings (matches map canvas)
    # ----------------------------
    iface = globals().get("iface", None)
    if iface:
        extent = iface.mapCanvas().extent()
        crs = iface.mapCanvas().mapSettings().destinationCrs()
    else:
        # fallback: use project extent and CRS
        extent = project.layerTreeRoot().extent()
        crs = QgsCoordinateReferenceSystem("EPSG:4326")

    map_settings = QgsMapSettings()
    map_settings.setLayers(layers)
    map_settings.setExtent(extent)
    map_settings.setOutputSize(QSize(width, height))
    map_settings.setDestinationCrs(crs)
    print("🗺️ Map settings prepared for rendering.")

    # ----------------------------
    # 3️⃣ Render visible map to QImage
    # ----------------------------
    job = QgsMapRendererParallelJob(map_settings)
    job.start()
    job.waitForFinished()
    img = job.renderedImage()
    print("🖼️ Visible map rendered to image.")
    img.save(output_path, "tif")


def wms_run():
    wms_layer = wms_layer_load(wms_url)
    qgis_cropping(X1, Y1, X2, Y2, wms_layer)
    raster_to_tif(LAYER_NAME, OUTPUT_LAYER)
    # save_visible_map_to_tif(OUTPUT_LAYER)
    load_output(OUTPUT_LAYER)
    render_set(wms_layer, 315, 45)

wms_run()
