from qgis.core import *
import os

file_path = os.path.dirname(QgsProject.instance().fileName())
input_raster = os.path.join(file_path, "data/test_raster.tif")    # Your DSM/DTM
output_raster = os.path.join(file_path, "data/output.tif")

dsm = QgsRasterLayer(input_raster, "dsm")
if not dsm.isValid():
    raise Exception("Could not load raster!")
QgsProject.instance().addMapLayer(dsm)


# Run r.sun (simple mode: only direct irradiance, no additional maps)
params = {
    "elevation": input_raster,     # DEM
    "linke": None,                 # optional
    "albedo": None,                # optional
    "aspect": None,                # auto-calculated if None
    "slope": None,                 # auto-calculated if None
    "day": 180,                    # day of year (example: 180 = June 29)
    "time": 12.0,                  # solar time (hours)
    "incidout": output_raster,     # output solar irradiation raster
    "beam_rad": None,
    "diff_rad": None,
    "refl_rad": None,
    "global_rad": None,
    "insol_time": None,
    "verbose": False,
    "GRASS_REGION_PARAMETER": None,
    "GRASS_REGION_CELLSIZE_PARAMETER": 0,
    "GRASS_RASTER_FORMAT_OPT": "",
    "GRASS_RASTER_FORMAT_META": ""
}

result = processing.run("grass7:r.sun", params)
print("r.sun finished. Output saved to:", output_raster)