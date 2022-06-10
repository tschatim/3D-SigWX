'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  HorizontalWindWorkflow
 Source Name:       HorizontalWindWorkflowStandalone.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file(s)
                    NetCDF Variable Name for U,V and Geometric Height 
                    NetCDF x and y Dimension (longitude, latitude)
                    Current work Geodatabase
                    Temporary Folder to save intermediate files
                    Vertical height Interpolation parameters

 Description:       Geoprocessing Workflow to create a hosted Scene Layer containing 
                    Horizontal Wind speeds and the wind direction at each grid point 
                    based on the "U" and "V" Variable in the COSMO-1E Numerical 
                    Weather Prediction Model Output Data.
                    
  
----------------------------------------------------------------------------------'''

#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset as NetCDFFile
import netCDF4
from importlib import reload
import traceback

# Import Geoprocessing Modules
from HeightAssignment import *
from MergeNetCDF import *
from CreateSceneLayer import *
from ShareSceneLayer import *
from HorizontalWindClassification import *
from arcpy import env

def HorizontalWindWorkflow(inNetCDFFileNames, ncVarNames, current_geodatabase, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, Timestamp, descriptionDate,
                            username_arcgis, password_arcgis, timeEnabled = False):
    """
        Function Description:   Geoprocessing Workflow to create a hosted Scene Layer containing 
                                Horizontal Wind speeds and the wind direction at each grid point 
                                based on the "U" and "V" Variable in the COSMO-1E Numerical 
                                Weather Prediction Model Output Data.
         
        Parameters
        ----------
        InNetCDFFileNames: array
            Array containing paths to NetCDF files
        ncVarNames: array
            NetCDF variable names
        current_geodatabase: string
            Path to work GDB
        current_folder: string
            Path to Folder, where GDB is stored
        tempLayerFolder: string
            Path to Folder, where temporary Scene Layer files are stored
        AmountofLayers: int
            Number of Layers in new vertical coordinate system
        MaxHeight: int
            Heighest interpolated Layer in new vert. coord. system
        Timestamp: string
            Timestamp of the current NetCDF file 
            (used to later identify the correct layers in the web app)
        descriptionDate: string
            Date of the processed NetCDF file
            (used to display the correct date in the web app)
        username_arcgis: string
            Username to ArcGIS account
        password_arcgis: string
            Password of ArcGIS account
        timeEnabled: bool
            If true, time dimension is added to the feature layer
        
        Returns
        -------
    """

    # Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"


    try:

        LayerName = "HorizontalWind"    # Name for Output NetCDF File


        counter = 0
        file_names = [] # List to store all the output files from the CloudClassification routine for merging in MergeNetCDF
        for InFileName in inNetCDFFileNames:
            arcpy.AddMessage('\nStarting with file ' + str(counter))
    
            # 1. HeightAssignment
            ncVarName_HeightAssign = ['U', 'V']  # variable to be interpolated
            height_assigned_file_UV = HeightAssignment(InFileName, ncVarName_HeightAssign, current_folder, AmountofLayers, MaxHeight, LayerName, Timestamp)
    
            # 2. CloudClassification
            [HorizontalWind_file, HorizontalWind_VarNames] = HorizontalWindClassification(height_assigned_file_UV, current_folder, LayerName, Timestamp)

            file_names.append(HorizontalWind_file)
            
            counter += 1
        
        # 3. Merging Files
        [merged_NetCDFfileName, DimensionNames_mergedFile] = MergeNetCDFFunction(file_names, current_folder, LayerName, Timestamp)

        # 4. Create NetCDF Feature Layer (.lyrx file)
        HorizontalWind_VarNames.append("LayerLevel")    # Additional Variable Name indicating the Layer Levels (integer 0-maxHeight)
        outFeatureLayerName = CreateNetCDFFeatureLayer(merged_NetCDFfileName, DimensionNames_mergedFile, HorizontalWind_VarNames, current_geodatabase, 
                                                        current_folder, tempLayerFolder, LayerName, Timestamp, timeEnabled)
        
        # 5. Share NetCDF Feature Layer (hosting on ArcGIS Online)
        #       Creates .slpk package file and shares package to ArcGIS Online
        ShareSceneLayerFunction(outFeatureLayerName, tempLayerFolder, LayerName, Timestamp, descriptionDate, username_arcgis, password_arcgis)



        arcpy.AddMessage('SUCCESS: Horizontal Wind Workflow ended without interruptions')
    


    
    except Exception as error:
        arcpy.AddError(f"Exception occured:  {error}, {type(error)},\n\n{traceback.format_exc()}")
        


