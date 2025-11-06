# Copy for in QGIS testing
import os
from qgis.core import *
from qgis.utils import *
from constants import *

lat1, lon1 = 48.1549554,17.1650823
lat2, lon2 = 48.1555931,17.1642535

file_path = os.path.dirname(QgsProject.instance().fileName())
raster_path = os.path.join(file_path, "data/test_raster.tif")
raster_layer = QgsRasterLayer(raster_path, LAYER_NAME)
vector_layer = QgsVectorLayer(raster_path, LAYER_NAME) # dont't work, not shp file

def render_set(layer, azimuth, altitude):
    if layer and layer.isValid():
        print("Rerendering: ", layer.name())
    else:
        print("Layer is invalid or has been deleted.")
    input_layer = layer.dataProvider()
    renderer = QgsHillshadeRenderer( input_layer, 1, azimuth, altitude)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

def basic_layer_set(layer):
    layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
    layer.renderer().setOpacity(0)
    layer.resampleFilter().setZoomedInResampler(QgsBilinearRasterResampler())
    layer.resampleFilter().setZoomedOutResampler(QgsBilinearRasterResampler())

def zoom_and_crop_qgis(lat1, lon1, lat2, lon2, layer, output_path="output.tif"):
    src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
    dst_crs = layer.crs()
    transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
    rect_wgs84 = QgsRectangle(lon1, lat1, lon2, lat2)
    rect_proj = transform.transform(rect_wgs84)
    try:
        iface.mapCanvas().setExtent(rect_proj)
        iface.mapCanvas().refresh()
        print("zoom to coordinates")
    except Exception:
        print("running outside QGIS; skipping zoom")
    provider: QgsRasterDataProvider = layer.dataProvider()
    pipe = QgsRasterPipe()
    if not pipe.set(provider.clone()):
        raise Exception("failed to initialize pipe")
    extent = layer.extent()
    width = layer.width()
    height = layer.height()
    pixel_width = extent.width() / width
    pixel_height = extent.height() / height

    new_width = int(rect_proj.width() / pixel_width)
    new_height = int(rect_proj.height() / pixel_height)
    writer = QgsRasterFileWriter(output_path)
    writer.setOutputFormat("GTiff")
    result = writer.writeRaster(
        pipe,
        new_width,
        new_height,
        rect_proj,
        layer.crs()
    )
    if result != QgsRasterFileWriter.NoError:
        raise Exception(f"Raster writing failed >>> Code: {result}")
    cropped_layer = QgsRasterLayer(output_path, "Cropped (PyQGIS)")
    if cropped_layer.isValid():
        QgsProject.instance().addMapLayer(cropped_layer)
        print(f"cropped raster saved >>> {output_path}")
    else:
        print(f"file created but not loaded >>> {output_path}")
    return output_path

if raster_layer.isValid():
    project = QgsProject.instance()
    for layer in project.mapLayers().values():
        if layer.name() == LAYER_NAME:
            project.removeMapLayer(layer.id())
    print("Cleaning project...")
    main_layer = project.addMapLayer(raster_layer)
    print("Raster layer loaded successfully")
    print("DSM CRS:", raster_layer.crs().authid())
    # print("Sun layer check", rsun_apply(raster_path)['output'])
    # basic_layer_set(main_layer)
    render_set(main_layer, 315, 45)

    layer = project.mapLayersByName(LAYER_NAME)[0]
    zoom_and_crop_qgis(lat1, lon1, lat2, lon2, layer, r"data\output.tif")
else:
    print("Raster layer is not valid")



