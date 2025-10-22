from constants import *
from qgis.core import *
from pyproj import Transformer
from osgeo import gdal

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

def qgis_cropping(x1, y1, x2, y2, layer, output_file):
    crop_box = QgsRectangle(y1, x1, y2, x2)
    src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
    dst_crs = layer.crs()
    xfrom = QgsCoordinateTransform(src_crs, dst_crs, None)
    box_proj = xfrom.transform(crop_box)
    pipe = QgsRasterPipe()
    pipe.set(layer.renderer())
    provider = layer.dataProider()
    if not pipe.set(provider.clone()):
        raise Exception("Failed to provide cropping layer")
    save = QgsRasterFileWriter(output_file)
    save.setOutputFormat("GTiff")
    save.writeRaster(pipe, layer.width(), layer.height(), box_proj, layer.crs())
    print(f"DSM/qgis saved to: {output_file}")

def gdal_cropping(box):
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
    print(f"DSM/gdal saved to: {OUTPUT_LAYER}")

def rgrass_cropping(x1, y1, x2, y2, layer, output_file):
    gisdb = os.path.join(os.getcwd(), "grassdata")
    os.makedirs(gisdb, exist_ok=True)
    location = "temp_location"
    mapset = "PERMANENT"
    src = layer.dataProvider().dataSourceUri()
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x_min, y_min = transformer.transform(x1, y1)
    x_max, y_max = transformer.transform(x2, y2)
    gsetup.init(gisdb, location, mapset)
    gscript.run_command("g.proj", epsg=3857)
    gscript.run_command("r.in.gdal", input=src, output="raster_in", overwrite=True)
    gscript.run_command("g.region", n=y_max, s=y_min, e=x_max, w=x_min)
    gscript.run_command("r.mapcalc", expression="raster_crop = raster_in", overwrite=True)
    gscript.run_command("r.out.gdal", input="raster_crop", output=output_file, format="GTiff", createopt="COMPRESS=LZW", overwrite=True)
    print(f"DSM/rgrass saved to: {output_file}")

def load_output(layer_path):
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
    gdal_cropping(box)
    load_output(OUTPUT_LAYER)

wms_run()