## Rooftop Photovoltaic Potential Estimation Automatization via QGIS
### Actual tasks: 
1. Process automated loading of rasters into QGIS via Python script (complited on 01/10/2025)
    - as an offline file 
    - via WMS service
2. Add coordinate boxing for online WMS raster
   - Basic tools >>> failed 
   - GDAL >>> null pointer in output
   - GRASS environment >>> testing
   - Reloading WMS to offline dataset 
   - Cropping offline WMS dataset
4. Analysis of tilt and turn of roof parcels in boxing zone.
5. Differentiation of roof vectors via QuickOSM (OverpassAPI) 

## Required libs and tools
### Tools
- Python 3.12 or higher 
- QGIS Desktop 3.34 or higher
### Python libs
- os (loading and saving results)
- qgis.core (main API for contacting qgis)
- numpy (mathematics)
- pyproj (for coordinate transforming)
- osgeo (gdal)
- grass.scripts && grass.scrips.setup 
