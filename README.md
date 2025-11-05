## Rooftop Photovoltaic Potential Estimation Automatization via QGIS
### Actual tasks: 
1. Process automated loading of rasters into QGIS via Python script (completed on 01/10/2025)
    - as an offline file 
    - via WMS service
2. Add coordinate boxing for online WMS raster
   - Basic tools >>> failed (failed on 12/10/2025)
   - GDAL >>> null pointer in output (failed on 16/10/2025)
   - GRASS environment >>> testing (failed on 19/10/2025)
   - Cropping offline WMS dataset (completed on 05/11/2025)
   - Reloading WMS to offline dataset 
4. Analysis of tilt and turn of roof parcels in boxing zone.
5. Differentiation of roof vectors via QuickOSM (OverpassAPI) 

## Required libs and tools
### Tools
- Python 3.12 or higher 
- QGIS Desktop 3.34 or higher
### Python libs
- os (loading and saving results)
- qgis.core (main API for contacting qgis)
- qgis.utils (API woking with canvas)
- numpy (mathematics)
- pyproj (for coordinate transforming)
- osgeo (gdal)
- grass.scripts && grass.scrips.setup 
