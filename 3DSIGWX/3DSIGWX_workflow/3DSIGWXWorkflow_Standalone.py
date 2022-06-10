'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  3DSigWXWorkflow
 Source Name:       3DSIGWXWorkflow.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         Configuration File (config.yml)
                    NetCDF Files

 Description:       This is the main file of the geoprocessing workflows. It is 
                    used to prepare all the layers that will finally be displayed 
                    in the web app. Ensure that you have read the README.md file 
                    before starting the workflow.
                    
  
----------------------------------------------------------------------------------'''
#Import required modules
import arcpy
import numpy as np
import sys, os, copy, tempfile
from netCDF4 import Dataset as NetCDFFile
import netCDF4
import yaml
from os import listdir
import glob
from babel.dates import format_datetime
import datetime


# Import Workflows
from CloudWorkflowStandalone import *
from ThunderstormWorkflowStandalone import *
from VerticalWindWorkflowStandalone import *
from ClipNetCDFMultiVar import *
from HorizontalWindWorkflowStandalone import *
from IcingWorkflowStandalone import *

def feedRoutine():
    """
        Function Description:   Main Geoprocessing Workflow to preprocess and prepare the raw COSMO
                                NetCDF files and create the layers to later visualise in the 3D-SigWX
                                web app.
        
        Parameters
        ----------
        
        Returns
        -------
        
    """
    # 1. Configuration
    current_directory = os.path.abspath(os.path.dirname(__file__))
    configFilePath = os.path.join(current_directory, '3DSIGWXconfig.yml')
    config = read_yaml(configFilePath)

    # 1.1 Assign Config parameters to variables
    xyExtent = config["APP"]["EXTENT"]
    xDimension = config["APP"]["XDIMENSION"]
    yDimension = config["APP"]["YDIMENSION"]
    varNames = config["APP"]["VARIABLES"]
    AmountofLayers = config["APP"]["ZLAYERS"]
    MaxHeight = config["APP"]["MAXHEIGHT"]
    TimeAvailable = config["APP"]["TIMEAVAILABLE"]

    COSMOFilesFolder = config["DATABASE"]["COSMOFILES"]
    workGDB = config["DATABASE"]["WORKGDB"]
    
    username_arcgis = config["ARCGIS"]["USERNAME"]
    password_arcgis = config["ARCGIS"]["PASSWORD"]



    # 2. Setting up the Environment: 
    # 2.1 Define Default GDB in the location specified by workGDB, 
    arcpy.env.workspace = workGDB
    arcpy.env.overwriteOutput = True    # Allow to overwrite FeatureClasses and Files in the GDB
    if arcpy.Exists(arcpy.env.workspace):
        for feat in arcpy.ListFeatureClasses("Clouds_*"):      # Delete all FeatureClasses in WorkGDB starting with "Clouds_"   
            arcpy.management.Delete(feat)
    else:
        arcpy.management.CreateFileGDB(os.path.dirname(workGDB), os.path.basename(workGDB))

    # 2.2 Define TempLayerFolder to temporary store Layers to Share/Host via ArcGIS Online
    current_folder = os.path.dirname(workGDB)
    arcpy.AddMessage("\nSaving output NetCDF files to: " + str(current_folder))
    tempLayerFolder = os.path.join(current_folder, "TempLayerFolder")      

    # 2.3 Log into ArcGIS Online Portal
    arcpy.SignInToPortal(arcpy.GetActivePortalURL(), username_arcgis, password_arcgis)
    
    # 2.4. Define path to Input NetCDF Files for the desired timestamps 0500UTC, 0800UTC, 1100UTC, 1400UTC and 1700UTC
    inNetCDFFiles_dict = get_inNetCDFFiles(COSMOFilesFolder)



    # 3. Geoprocessing Workflows
    if not TimeAvailable:
        # 3.1 Variant 1: A single layer per meteorological parameter and timepoint (05UTC, 08UTC, 11UTC, 14UTC, 17UTC) 
        # -> Workaround for simplified time-dynamic visualisation in the webapp
        for key in inNetCDFFiles_dict:
            if "Path" in key: 
                if inNetCDFFiles_dict[key] != "null":
                    timestamp = key[0:5]
                    descriptionDate_raw = os.path.basename(inNetCDFFiles_dict[key])[3:11]
                    descriptionDate_raw = datetime.datetime.strptime(str(descriptionDate_raw), "%Y%m%d")
                    descriptionDate = format_datetime(descriptionDate_raw, "dd. MMMM Y", locale='en')
                    
                    # 3.1.1 Clip netCDF
                    clipped_file = ClipNetCDFMultiVar(inNetCDFFiles_dict[key], varNames, xDimension, yDimension, xyExtent, current_folder, timestamp)
                    
                    # 3.1.2 Geoprocessing Workflows
                    CloudWorkflow([clipped_file], varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate,username_arcgis, password_arcgis)
                    StormWorkflow([clipped_file], workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis)
                    VerticalWindWorkflow([clipped_file], varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis) 
                    HorizontalWindWorkflow([clipped_file], varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis)  
                    IcingWorkflow([clipped_file], varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis)

    elif TimeAvailable:
        # 3.2 Variant 2: A single layer per meteorological parameter. Time is included as SceneLayer Attribute 
        # (Currently not working in the webapp -> unkown error with "time" field)
        # 3.3.1. Clip netCDF
        StartEndFile_idx = [5 , 6]  # Nr. indicates the time in UTC
        ncFilePaths = glob.glob(os.path.join(COSMOFilesFolder, "*.nc"))[StartEndFile_idx[0]:StartEndFile_idx[1]+1]       # List all/selected .nc files in Directory
        FirstNcFileName = glob.glob(os.path.join(COSMOFilesFolder, "*.nc"))[0]
        descriptionDate_raw = FirstNcFileName[-13:-5]
        descriptionDate_raw = datetime.datetime.strptime(str(descriptionDate_raw), "%Y%m%d")
        descriptionDate = format_datetime(descriptionDate_raw, "ddMMMY", locale='en')
        timestamp = descriptionDate+"_TimeEnabled"
        clipped_file_names = []
        for InFileName in ncFilePaths:
            clipped_file = ClipNetCDFMultiVar(InFileName, varNames, xDimension, yDimension, xyExtent, current_folder, timestamp)
            clipped_file_names.append(clipped_file)
        
        # 3.2.2. Geoprocessing Workflows
        timestamp = timestamp.split("_")[1]     # Change Timestamp for later archiving the correct layers in the Portal
        CloudWorkflow(clipped_file_names, varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis, TimeAvailable)
        StormWorkflow(clipped_file_names, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis, TimeAvailable)
        VerticalWindWorkflow(clipped_file_names, varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis, TimeAvailable)   
        HorizontalWindWorkflow(clipped_file_names, varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis, TimeAvailable)  
        IcingWorkflow(clipped_file_names, varNames, workGDB, current_folder, tempLayerFolder, AmountofLayers, MaxHeight, timestamp, descriptionDate, username_arcgis, password_arcgis, TimeAvailable)
    else:
        arcpy.AddMessage("\nWARNING: Please select in the config file if the ''time'' Attribute is available in the webapp."+
                        "This will automatically choose the appropriate workflow.\n")

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def get_inNetCDFFiles(COSMO_folder):
    Timestamps_dict = {
        "05UTCPath":        "null",
        "05UTCFilename":    "null",
        "08UTCPath":        "null",
        "08UTCFilename":    "null",
        "11UTCPath":        "null",
        "11UTCFilename":    "null",
        "14UTCPath":        "null",
        "14UTCFilename":    "null",
        "17UTCPath":        "null",
        "17UTCFilename":    "null"
    }

    ncFilePaths = glob.glob(os.path.join(COSMO_folder, "*.nc"))       # List all .nc files in Directory
    for file in ncFilePaths:       
        # Compare the time information in the nc filename (last two strings before .nc suffix). 
        # Assign the File Paths for the desired UTC times                     
        if os.path.basename(file)[-5:-3] == "05":        
            Timestamps_dict["05UTCPath"] = file
            Timestamps_dict["05UTCFilename"] = os.path.basename(file)
        elif os.path.basename(file)[-5:-3] == "08":        
            Timestamps_dict["08UTCPath"] = file
            Timestamps_dict["08UTCFilename"] = os.path.basename(file)
        elif os.path.basename(file)[-5:-3] == "11":        
            Timestamps_dict["11UTCPath"] = file
            Timestamps_dict["11UTCFilename"] = os.path.basename(file)
        elif os.path.basename(file)[-5:-3] == "14":        
            Timestamps_dict["14UTCPath"] = file
            Timestamps_dict["14UTCFilename"] = os.path.basename(file)
        elif os.path.basename(file)[-5:-3] == "17":        
            Timestamps_dict["17UTCPath"] = file
            Timestamps_dict["17UTCFilename"] = os.path.basename(file)
        else:
            pass
    
    return Timestamps_dict


if __name__ == "__main__":
    feedRoutine()

