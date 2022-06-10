'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  CreateSceneLayer
 Source Name:       CreateSceneLayer.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file 
                    Output Temporary SceneLayer

 Description:       Function to Create a NetCDF Feature Layer and then a Scene Layer
                    File (.lyrx)
                    
  
----------------------------------------------------------------------------------'''


#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset
import netCDF4


def CreateNetCDFFeatureLayer (InNetCDFFileName, DimensionNames, VariableName, current_geodatabase, current_projectfolder, temporary_LayerFolder, LayerName, Timestamp, 
                                timeEnabled=False):
    """
        Function Description:   Creates first a NetCDF Feature Layer. Then based on the 
                                Feature Layer a Scene Layer File (.lyrx) is generated.
         

        Parameters
        ----------
        InNetCDFFileNames: array
            Array containing paths to NetCDF files
        DimensionNames: list
            List of all NetCDF Dimensions
        VariableName: list
            List of Variables
        current_geodatabase: string
            Path to work GDB
        current_projectfolder: string
            Path to Folder, where GDB is stored
        temporary_LayerFolder: string
            Path to Folder, where temporary Scene Layer files are stored
        LayerName: string
            Name of Layer (corresponds to Meteorological Parameter)
        Timestamp: string
            Timestamp of the current NetCDF file 
        timeEnabled: bool
            If true, time dimension is added to the feature layer
        
        Returns
        -------
        outFeatureLayerPath: string
            Path to Scene Layer Package
    """

    arcpy.AddMessage("\nSTART Create Scene Layer")

    # 1. Store Dimension Names in Variables
    timeDimension = DimensionNames[0]
    zDimension = DimensionNames[1]
    yDimension = DimensionNames[2]
    xDimension = DimensionNames[3]
    
    # 2. Create Input Variables for MakeNetCDFFeatureLayer Function
    inVariables = VariableName
    inXVariable = xDimension
    inYVariable = yDimension
    ZVariable = zDimension

    # Delete time dimension if timeEnabled = false
    if not timeEnabled:
        if "time" in  DimensionNames:
            DimensionNames.remove("time")
    

    rowDimensions = DimensionNames
    outNetCDFFeatureLayerName = Timestamp + "_" + LayerName

    MVariable = ""
    dimensionValues = ""
    valueSelectionMethod = ""


    
    # 3. Create NetCDF Feature Layer with function MakeNetCDFFeatureLayer
    arcpy.AddMessage("... creating NetCDF Feature Layer")
    outNetCDFFeatureLayer = arcpy.MakeNetCDFFeatureLayer_md(InNetCDFFileName, inVariables, inXVariable, 
                                inYVariable, outNetCDFFeatureLayerName, rowDimensions, ZVariable, MVariable, dimensionValues, valueSelectionMethod)

    # 4. Save NetCDF Feature Layer to a .lyrx Layer File
    # NetCDF Feature Layer can not be stored in a Point Scene Layer directly from a NetCDF Feature Layer .lyrx File
    # Workaround: 
    #   - First copy the Feature Class of the NetCDF Feature Layer and store in the current geodatabase. 
    #   - Then Make a new Point Feature Layer based on the copied Feature Class in the gdb 
    #   - Save the new Point Feature Layer as a .lyrx Layer File (This .lyrx File can then be used to create a Point Scene Layer in the ShareSceneLayer Function)
    outFeatureClass = os.path.join(current_geodatabase, LayerName+ "_" + Timestamp + "_pointFC")
    outFeatureClass = outFeatureClass.replace(os.sep, "/")
    arcpy.AddMessage("... copy Feature Class of NetCDF Feature Layer")
    CopiedFeatureClass = arcpy.CopyFeatures_management(outNetCDFFeatureLayer, out_feature_class=outFeatureClass)
    outFeatureLayerName = LayerName+ "_" + Timestamp + "_pointFL"
    outFeatureLayerPath = os.path.join(temporary_LayerFolder, outFeatureLayerName)
    outFeatureLayerPath = outFeatureLayerPath.replace(os.sep, "/")
    arcpy.AddMessage("... creating new Feature Layer with copied Feature Class")
    outFeatureLayer = arcpy.MakeFeatureLayer_management(outFeatureClass, outFeatureLayerName)
    arcpy.AddMessage("... saving Feature Layer as Layer File (.lyrx)")
    arcpy.SaveToLayerFile_management(outFeatureLayer, outFeatureLayerPath)

    arcpy.AddMessage("END Create Scene Layer\n\n")

    return outFeatureLayerPath

