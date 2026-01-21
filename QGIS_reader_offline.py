# imported libs
import os
import csv
from qgis.core import *
from qgis.utils import *
from constants import *

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
        print("ERROR >>> Layer is invalid or has been deleted.")
    input_layer = layer.dataProvider()
    renderer = QgsHillshadeRenderer( input_layer, 1, azimuth, altitude)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

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
        raise Exception("ERROR >>> Output raster is not valid: " + output_raster)
    QgsProject.instance().addMapLayer(sol_raster)
    print("Finished: Insolation time raster added to QGIS.")

def overpassAPI_roof_finder(layer):
    extent = layer.extent()
    params = {
        'KEY': 'building',
        'VALUE': '',
        'TYPE_MULTI_REQUEST': '',
        'EXTENT': extent,
        'TIMEOUT': 120,
        'SERVER': 'https://overpass-api.de/api/interpreter',
        'OUTPUT': 'TEMPORARY_OUTPUT'
    }
    result = processing.run("quickosm:downloadosmdataextentquery", params)
    # print(result)
    roofs_vector = QgsProject.instance().addMapLayer(result['OUTPUT_MULTIPOLYGONS'])
    roofs_proj = processing.run("native:reprojectlayer",{'INPUT': roofs_vector,'TARGET_CRS': layer.crs(),'OUTPUT': 'memory:roofs_proj'})['OUTPUT']
    # QgsProject.instance().addMapLayer(roofs_proj)
    px_x = layer.rasterUnitsPerPixelX()
    px_y = layer.rasterUnitsPerPixelY()
    rasterize_params = {
        'INPUT': roofs_proj,
        'FIELD': None,
        'BURN': 1,  # roof = 1
        'UNITS': 1,  # map units
        'WIDTH': px_x,
        'HEIGHT': px_y,
        'EXTENT': extent,
        'NODATA': 0,  # non-roof = 0
        'DATA_TYPE': 5,  # UInt16
        'INIT': 0,
        'INVERT': False,
        'EXTRA': '',
        'OUTPUT': 'TEMPORARY_OUTPUT'
    }
    roof_raster  = processing.run("gdal:rasterize", rasterize_params)
    # print("Rasterizing >>>", roof_raster)
    roof_layer = QgsRasterLayer(roof_raster['OUTPUT'], "roof_raster")
    QgsProject.instance().addMapLayer(roof_layer)
    dsm_roofs = processing.run(
        "gdal:rastercalculator",
        {
            'INPUT_A': layer,
            'BAND_A': 1,
            'INPUT_B': roof_layer,
            'BAND_B': 1,
            'FORMULA': 'A * B',
            'NO_DATA': -9999,
            'RTYPE': 5,
            'OUTPUT': 'memory:dsm_roofs'
        }
    )['OUTPUT']
    dsm_roofs_layer = QgsRasterLayer(dsm_roofs, 'dsm_roofs')
    QgsProject.instance().addMapLayer(dsm_roofs_layer)
    print("QUICK OSM FINISHED!!! Final layer >>> dsm_roofs")
    return dsm_roofs_layer

def roof_pv_check(dsm_roofs):
    #----------------SLOPE-------------------------
    roof_slope = processing.run("gdal:slope",
        {
            'INPUT': dsm_roofs,
            'BAND': 1,
            'SCALE': 1,
            'AS_PERCENT': False,
            'COMPUTE_EDGES': True,
            'ZEVENBERGEN': False,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
    )['OUTPUT']
    roof_slope_layer = QgsRasterLayer(roof_slope, 'roof_slope')
    # QgsProject.instance().addMapLayer(roof_slope_layer)
    print("Roof Slope analyse finished without ERRORs. >>> 'roof_slope' loaded to QGIS")
    #-------------FLAT ROOFS CHECK (< 5)--------------------
    flat_roofs = processing.run("gdal:rastercalculator",
        {
            'INPUT_A': roof_slope,
            'BAND_A': 1,
            'FORMULA': 'A <= 5',
            'RTYPE': 5,
            'NO_DATA': 0,
            'OUTPUT': 'memory:flat_roofs'
        }
    )['OUTPUT']
    flat_roofs_layer = QgsRasterLayer(flat_roofs, 'flat_roofs')
    # QgsProject.instance().addMapLayer(flat_roofs_layer)
    print("Flat roofs check analyse finished without ERRORs. >>> 'flat_roofs' loaded to QGIS")
    #--------------ASPECT (0-360)-----------------------------
    roof_aspect = processing.run("gdal:aspect",
        {
            'INPUT': dsm_roofs,
            'BAND': 1,
            'TRIG_ANGLE': False,
            'ZERO_FOR_FLAT': True,
            'COMPUTE_EDGES': True,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
    )['OUTPUT']
    roof_aspect_layer = QgsRasterLayer(roof_aspect, 'roof_aspect')
    QgsProject.instance().addMapLayer(roof_aspect_layer)
    print("Roof aspect analyse finished without ERRORs. >>> 'roof_aspect' loaded to QGIS")
    #--------------Suitability Check----------------------------
    pv_roofs = processing.run("gdal:rastercalculator",
        {
            'INPUT_A': roof_aspect,
            'BAND_A': 1,
            'INPUT_B': roof_slope,
            'BAND_B': 1,
            'FORMULA': '((A>=135 AND A<=225) AND (B>=0 AND B<=35))',
            'RTYPE': 5,
            'NO_DATA': 0,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
    )['OUTPUT']
    pv_roofs_layer = QgsRasterLayer(pv_roofs, 'pv_roofs')
    QgsProject.instance().addMapLayer(pv_roofs_layer)
    print("PV roofs analyse finished without ERRORs. >>> 'pv_roofs' loaded to QGIS")

#-----------------------MAIN--------------------------------
if raster_layer.isValid():
    project = QgsProject.instance()
    project.removeAllMapLayers()
    print("Cleaning project...")
    main_layer = project.addMapLayer(raster_layer)
    feedback = QgsProcessingFeedback()
    print("Raster >>>", LAYER_NAME,">>> loaded successfully")
    print("DSM CRS:", raster_layer.crs().authid())
    render_set(main_layer, 315, 45)
    # glob_rad_check(main_layer, 1, 255, 2015, feedback)
    # slope_calc(main_layer, file_path, feedback)
    # gdal_aspect_slope(raster_path, aspect_path, slope_path)
    roof = overpassAPI_roof_finder(main_layer)
    roof_pv_check(roof)

else:
    raise Exception("ERROR >>> Raster layer is not valid")



