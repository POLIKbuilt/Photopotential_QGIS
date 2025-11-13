from constants import *
from qgis.core import *
from qgis.analysis import *
from basic_raster_loader import *

import os

result_dir = r"data\result"
layer_dir = r"data\test_raster.tif"

def compute_slope_aspect(layer: QgsRasterLayer, output_dir: str):
    entry = QgsRasterCalculatorEntry()
    entry.ref = "raster@1"
    entry.raster = layer
    entry.bandNumber = 1
    entries = [entry]

    extent = layer.extent()
    width = layer.width()
    height = layer.height()

    slope_path = os.path.join(output_dir, "slope.tif")
    aspect_path = os.path.join(output_dir, "aspect.tif")

    #formula for slope and aspect (in radians)
    slope_expr = ""
    aspect_expr = ""

    slope_calc = QgsRasterCalculator(slope_expr, slope_path, "GTiff", extent, width, height, entries)
    aspect_calc = QgsRasterCalculator(aspect_expr, aspect_path, "GTiff", extent, width, height, entries)

    print("Calculating >>>")
    slope_result = slope_calc.processCalculation()
    aspect_result = aspect_calc.processCalculation()
    if slope_result == 0 or aspect_result == 0:
        print("Raster calculation completed successfully.")
    else:
        print(f"Raster calculation failed. Error ASPECT >>> {aspect_result} and SLOPE >>> {slope_result}")

    slope_layer = QgsRasterLayer(slope_path, "Roof_Tilt_(Slope)")
    aspect_layer = QgsRasterLayer(aspect_path, "Roof_Turn_(Aspect)")

    if slope_layer.isValid():
        QgsProject.instance().addMapLayer(slope_layer)
    if aspect_layer.isValid():
        QgsProject.instance().addMapLayer(aspect_layer)

    print(f"Slope saved >>> {slope_path}")
    print(f"Aspect saved >>> {aspect_path}")
    return slope_layer, aspect_layer

def apply_aspect_style(layer: QgsRasterLayer):
    """Apply circular color ramp for aspect visualization."""
    fcn = QgsColorRampShader()
    fcn.setColorRampType(QgsColorRampShader.Interpolated)
    fcn.setColorRampItemList([
        QgsColorRampShader.ColorRampItem(0, QColor(255, 0, 0), "North"),
        QgsColorRampShader.ColorRampItem(90, QColor(255, 255, 0), "East"),
        QgsColorRampShader.ColorRampItem(180, QColor(0, 255, 0), "South"),
        QgsColorRampShader.ColorRampItem(270, QColor(0, 0, 255), "West"),
        QgsColorRampShader.ColorRampItem(360, QColor(255, 0, 0), "North"),
    ])
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(fcn)
    renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

layer = layer_load(layer_dir)
slope_layer, aspect_layer = compute_slope_aspect(layer, result_dir)


