def qgis_cropping(x1, y1, x2, y2, layer, output_file):
    crop_box = QgsRectangle(y1, x1, y2, x2)
    src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
    dst_crs = layer.crs()
    xfrom = QgsCoordinateTransform(src_crs, dst_crs, None)
    box_proj = xfrom.transform(crop_box)
    pipe = QgsRasterPipe()
    pipe.set(layer.renderer())
    provider = layer.dataProvider()
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
    src = "data/test_raster.tif"
    ds = gdal.Open(src)
    if ds is None:
        raise RuntimeError("Failed to open WMS source. Check URL and GDAL WMS driver.")
    else:
        print("WMS connection successful:", ds.RasterXSize, ds.RasterYSize)
    crop = gdal.Translate(destName = OUTPUT_LAYER, srcDS = src, projWin = box, projWinSRS="EPSG:4326", format = "GTiff")
    if crop is None:
        raise RuntimeError("GDAL failed (NULL pointer)!!!")
    crop = None
    print(f"DSM/gdal saved to: {OUTPUT_LAYER}")

def rgrass_cropping(x1, y1, x2, y2, layer, output_file):
    gisdb = os.path.join(os.getcwd(), "grassdata")
    location = "D:IT\Fotopotencial_QGIS\data"
    mapset = "PERMANENT"
    location_path = os.path.join(gisdb, location)
    mapset_path = os.path.join(location_path, mapset)
    os.makedirs(gisdb, exist_ok=True)
    src = layer.dataProvider().dataSourceUri()
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x_min, y_min = transformer.transform(x1, y1)
    x_max, y_max = transformer.transform(x2, y2)
    gsetup.init(gisdb, location, mapset)
    if not os.path.exists(mapset_path) or not os.path.exists(os.path.join(location_path, "PERMANENT", "DEFAULT")):
        gscript.run_command("g.proj", epsg=3857, location=location, flags="c")
    gscript.run_command("r.in.gdal", input=src, output="raster_in", overwrite=True)
    gscript.run_command("g.region", n=y_max, s=y_min, e=x_max, w=x_min)
    gscript.run_command("r.mapcalc", expression="raster_crop = raster_in", overwrite=True)
    gscript.run_command("r.out.gdal", input="raster_crop", output=output_file, format="GTiff", createopt="COMPRESS=LZW", overwrite=True)
    print(f"DSM/rgrass saved to: {output_file}")

def save_wms_to_tif(wms_url, output_path, bbox, crs="EPSG:4326"):
    wms_layer = wms_layer_load(wms_url)
    extent = wms_layer.extent()
    crs_obj = QgsCoordinateReferenceSystem(crs)
    print("Full WMS >>>", extent.toString())
    provider = wms_layer.dataProvider()
    pipe = QgsRasterPipe()
    if not pipe.set(provider.clone()):
        raise Exception("WMS provider >>> Raster pipe failed")
    width = wms_layer.width()
    height = wms_layer.height()
    writer = QgsRasterFileWriter(output_path)
    writer.setOutputFormat("GTiff")
    result = writer.writeRaster(
        pipe,
        width,
        height,
        extent,
        crs_obj
    )
    if result != QgsRasterFileWriter.NoError:
        raise Exception(f"Raster writing failed >>> Code: {result}")
    print(f"WMS saved to >>> {output_path}")
    layer_out = QgsRasterLayer(output_path, "WMS_Saved")
    if layer_out.isValid():
        QgsProject.instance().addMapLayer(layer_out)
        print("Offline WMS file added to project")
    else:
        print(f"Saved TIF but not added >>> {output_path}")
    return layer_out

def create_extent(x1, y1, x2, y2):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x_min, y_min = transformer.transform(y2, x2)  # note swapped order lon,lat
    x_max, y_max = transformer.transform(y1, x1)
    return [x_min, y_max, x_max, y_min]


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
