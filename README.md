## Rooftop Photovoltaic Potential Estimation Tool for QGIS

## Required Tools and Libs
### Tools
- Python 3.12 or higher 
- QGIS Desktop 3.34 or higher
- Installed QGIS plugins: GRASS 7, QuickOSM
### Python libs
- os (loading and saving data files)
- csv (table data output)
- qgis.core (main API for contacting qgis)
- qgis.utils (Canvas tools API)
- osgeo (gdal tools) 
- grass.scripts && grass.scrips.setup

## Code Structure

```
HV_Transmission_Line_Analysis/
├── main.py                     # main execution script
├── constants.py                # Static Data and Strings  *on check for refactor*
├── basic_raster_loader.py      # script for loading raster into QGIS *marked for called method*
├── QGIS_reader_offline.py      # reader of offline raster *marked to Class based file* 
├── QGIS_reader_WMS.py          # reader of online raster *marked for refactor*
├── roof_analysis.py            # script for roof dividing *marked for refactor*
└── data/
    ├── test_raster.tif         # testing input file
    └── tmp/                    
        ├── aspect.tif          # updatable raster of aspect
        ├── output.tif          # output variant of file
        ├── slope.tif           # updatable raster of slope
        ├── aspect_points.csv   # updatable table of aspect *marked for refactor*
        └── slope_points.csv    # updatable table of slope *marked for refactor*
```

### Main methods

#### **Render_Set** Method
Method applies more efficient render style for loaded layer.

#### **glob_rad_check** Method
Method uses grass region parameters to apply sun insolation simulation for choosen date and time.

#### **overpassApi_roof_finder** Method
Method applies OverpassAPI to find and separate roof detected on the loaded layer.

#### **roof_pv_check** Method
This method applies and calculates all the nessecary conditions for detected roofs. (flat, slope and aspect)

### Actual tasks: 
1. Process automated loading of rasters into QGIS via Python script (completed on 01/10/2025)
    - as an offline file.
    - via WMS service.
2. Add coordinate boxing for online WMS raster. (working only manually 12/11/2025)
   - Basic tools >>> failed;
   - GDAL >>> null pointer in output; 
   - GRASS environment >>> testing;
   - Cropping offline WMS dataset; 
   - Reloading WMS to offline dataset; 
3. Analysis of tilt and turn of roof parcels in boxing zone. (Completed on 3/12/2025)
   - Global radiation analysis (slope and aspect) via **r.sun.insoltime**; 
   - Roof angle analysis output to cvs; 
4. Differentiation of roof vectors via QuickOSM. (completed on 15/12/2025)
   - Installed QuickOSM plugin;
   - Created *'roof_finder'* method, that downloads and creates roof polygons via OverpassAPI;
   - Implemented roof rastering and cutting out to *'roof_finder'*;
   - Refactored *gdal_aspect_slope* into *roof_pv_check* due to easier calculation;
   - Added flat roof check;
   - Implemented PV suitability check for roofs;
5. Complete PV analysis and structured output. (in process)
   - Coloring of suitable roofs;
   - Table/CSV output;
