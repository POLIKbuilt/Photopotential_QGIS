from qgis.core import *
import os

def layer_load(file: str) -> QgsVectorLayer:
    file_path = os.path.dirname(QgsProject.instance().fileName())
    raster_path = os.path.join(file_path, file)
    file_name = os.path.basename(raster_path)
    layer = QgsRasterLayer(raster_path, file_name)
    if layer.isValid():
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer.name() == file_name:
                project.removeMapLayer(layer.id())
        print("Cleaning project from previous layers")
        loaded_layer = project.addMapLayer(layer)
        print("Raster loaded successfully")
        return loaded_layer
    else:
        raise Exception("Raster loading failed")
