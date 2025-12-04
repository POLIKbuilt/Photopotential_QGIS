# Copy for in QGIS testing
import os
import csv
import numpy as np
from qgis.core import *
from qgis.utils import *
from constants import *
from osgeo import gdal

lat1, lon1 = 48.1549554,17.1650823
lat2, lon2 = 48.1555931,17.1642535

file_path = os.path.dirname(QgsProject.instance().fileName())
raster_path = os.path.join(file_path, "data/test_raster.tif")
raster_layer = QgsRasterLayer(raster_path, LAYER_NAME)
slope_path = os.path.join(file_path, "data/tmp/slope.tif")
aspect_path = os.path.join(file_path, "data/tmp/aspect.tif")
csv_path = os.path.join(file_path, "data/tmp/aspect_points.csv")


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

def glob_rad_check(layer, time_step, day, year, feedback):
    params = {
        'elevation': layer,  # input raster
        'aspect': layer,
        'slope': layer,
        'linke': None,
        'albedo': None,
        'start_hour': 0,
        'end_hour': 24,
        'time_step': time_step,
        'day': day,
        'year': year,
        'glob_rad': 'TEMPORARY_OUTPUT', # Set to TEMP for QGIS to auto-generate output
        'insol_time': 'TEMPORARY_OUTPUT',
        'GRASS_REGION_PARAMETER': layer.extent(),
        'GRASS_REGION_CELLSIZE_PARAMETER': layer.rasterUnitsPerPixelX()
    }
    result = processing.run("grass7:r.sun.insoltime", params, feedback=feedback)
    output_raster = result['glob_rad']
    sol_raster = QgsRasterLayer(output_raster, "glob_rad_output")
    if not sol_raster.isValid():
        raise Exception("Output raster is not valid: " + output_raster)
    QgsProject.instance().addMapLayer(sol_raster)
    print("Finished: Insolation time raster added to QGIS.")

def gdal_aspect_aspect(raster_path, aspect_path, slope_path):
    gdal.DEMProcessing(slope_path, raster_path, "slope", format="GTiff", computeEdges=True, slopeFormat="degree")
    gdal.DEMProcessing(aspect_path, raster_path, "aspect", format="GTiff", computeEdges=True)
    slope_rlayer = QgsRasterLayer(slope_path, "slope")
    aspect_rlayer = QgsRasterLayer(aspect_path, "aspect")
    if slope_rlayer.isValid() and aspect_rlayer.isValid():
        QgsProject.instance().addMapLayer(slope_rlayer)
        QgsProject.instance().addMapLayer(aspect_rlayer)
        print("Slope and Aspect Rasters added to QGIS.")
    else:
        raise Exception("Slope and Aspect Rasters not valid")
    slope_ds = gdal.Open(slope_path)
    aspect_ds = gdal.Open(aspect_path)
    slope = slope_ds.GetRasterBand(1).ReadAsArray()
    aspect = aspect_ds.GetRasterBand(1).ReadAsArray()
    rows, cols = slope.shape
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "col", "slope", "aspect"])
        for r in range(rows):
            for c in range(cols):
                writer.writerow([r, c, float(slope[r, c]), float(aspect[r, c])])
    print("CSV file created:", csv_path)

def overpassAPI_query(layer):
    result = processing.run(
        "quickosm:extract",
        {
            'INPUT': layer,
            'KEY': 'building:part',
            'VALUE': 'roof',
            'OUTPUT': 'memory:'  # create new memory layer
        }
    )
    roof_layer = result['OUTPUT']
    QgsProject.instance().addMapLayer(roof_layer)
    print("Roof polygons loaded from OSM.")

def slope_calc(dem, file_path, feedback):
    slope_result = processing.run("qgis:slope", {'INPUT': dem, 'Z_FACTOR': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'}, feedback=feedback)
    slope_raster = slope_result['OUTPUT']
    slope_points = processing.run("qgis:rastersampling", {'INPUT': dem, 'RASTERCOPY': slope_raster, 'COLUMN_PREFIX': 'slope_', 'OUTPUT': 'TEMPORARY_OUTPUT'}, feedback=feedback)['OUTPUT']
    output_slope_csv = os.path.join(file_path, "data/tmp/slope_points.csv")
    processing.run("native:exporttodelimitedtext",{'INPUT': slope_points,'LAYER_OPTIONS': '','FILE_OPTIONS': '','OUTPUT': output_slope_csv},feedback=feedback)
    print("Slope imported as csv >>> ")

if raster_layer.isValid():
    project = QgsProject.instance()
    for layer in project.mapLayers().values():
        if layer.name() == LAYER_NAME:
            project.removeMapLayer(layer.id())
    print("Cleaning project...")
    main_layer = project.addMapLayer(raster_layer)
    feedback = QgsProcessingFeedback()
    print("Raster layer loaded successfully")
    print("DSM CRS:", raster_layer.crs().authid())
    render_set(main_layer, 315, 45)
    # glob_rad_check(main_layer, 1, 125, 2020, feedback)
    # slope_calc(main_layer, file_path, feedback)
    # overpassAPI_query(main_layer)
    gdal_aspect_aspect(raster_path, aspect_path, slope_path)
else:
    print("Raster layer is not valid")



