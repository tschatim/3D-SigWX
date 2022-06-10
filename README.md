# 3D-SigWX
This project represents a prototype of a visualisation possibility of aviation weather hazards in 3D. It is divided into two parts. On the one hand, the preprocessing of raw data from a numerical weather forecast model in NetCDF format. On the other hand, the visualisation of the data in a webapp. The geoprocessing workflows are located in the subfolder *3DSIGWX_workflows* and were implemented with `Python`. The webapp can be found in the subfolder 3DSIGWX_webapp. The 3D-SigWX concept is based on the use of the ArcGIS environment. The `ArcGIS API for Python`, `ArcPy` and the `ArcGIS API for JavaScript` were used for this purpose.


## 1. Prerequisites
For the application to work correctly, the following requirements must be met:
1. ArcGIS account with access to ArcGIS Online
2. Installation of ArcGIS Pro on the system (containing a Python package)
3. Valid key for the ArcGIS API for JavaScript

## 2. 3D-SigWX workflow
Before the workflow can be started, the configuration file `3DSIGWXconfig.yml` must be adapted accordingly.
Then the workflow can be executed with the main script `3DSIGWXWorkflow_Standalone.py`. The workflow runs automatically. The final result is the hosted Scene Layers in the ArcGIS Online Portal.

## 3. 3D-SigWX web app
The web app must be hosted via a server in order to function correctly and to display all objects of the aviation weather hazards. This can be done e.g. with the `Python` module `http.server`, which is included in the ArcGIS Pro Python package by default. To do this, first change to the directory with the web app files in the python command prompt:
```
cd *path_to_file_folder*
```
Then the local server can be started with the following command:
```
python3 -m http.server
```
The webapp can be started via the web browser under the following URL (adjust the port number if necessary):
```
http://localhost:8000/
```

## 4. Known Limitations
The following limitations are known for the current prototype:
- In the geoprocessing workflow it sometimes happens that the old layers in the ArcGIS Online Portal are not set to *private* after archiving when executing with new data. This can result in the web app still being able to access an outdated layer.
- Certain objects such as the clouds have an impact on the performance of the webapp. If, for example, a large area is covered with clouds, it is no longer possible to render all objects in the web app at the same time.


## 5. Usage
The code published here is the property of the authors and may not be reused without permission.
