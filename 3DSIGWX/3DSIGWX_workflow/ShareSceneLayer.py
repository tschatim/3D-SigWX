'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  ShareSceneLayer
 Source Name:       ShareSceneLayerWorkflow.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         ArcGIS Scene Layer(.lyrx)
                    Published Web Layer (.slpk)

 Description:       ArcGIS workflow to create a Scene Layer Package and to share the
                    Scene Layer Package to ArcGIS Online Portal as a hosted Layer. 
                    The shared layer will later be used in the 3D-SigWX Web-App.
                    
  
----------------------------------------------------------------------------------'''

#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from arcgis.gis import GIS  # ArcGIS Python API
import datetime



def ShareSceneLayerFunction(inSceneLayer, temporary_LayerFolder, LayerName, Timestamp, descriptionDate, username_arcgis, password_arcgis):
    """
        Function Description:   Function to create a Scene Layer Package and to share the
                                Scene Layer Package to ArcGIS Online Portal as a hosted Layer. 
                                The shared layer will later be used in the 3D-SigWX Web-App
         
        Parameters
        ----------
        inSceneLayer: string
            Path to Layer File (.lyrx)
        temporary_LayerFolder: string
            Path to Folder, where temporary Scene Layer files are stored
        LayerName: string
            Name of Layer (corresponds to Meteorological Parameter)
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
        
        Returns
        -------
    
    """

    # Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"

    # Log into ArcGIS Online
    gis = GIS(url="https://zhaw.maps.arcgis.com", username= username_arcgis, password= password_arcgis)
    gis.url


    arcpy.AddMessage("\nSTART Share Scene Layer Workflow")

    
    # 1. Archive older Layers from last Workflow runs
    # 1.1 Check for obsolete Layers from last Workflow run in Folder "LayerName"
    # If files are found, store the layer item in variables
    arcpy.AddMessage("... Checking for older versions of Scene layers in ArcGIS Online Portal")
    for folder in gis.users.me.folders:
        if folder['title'] == LayerName:
            for item in gis.users.me.items(folder['title']):
                if (item['type'] == 'Scene Service') & (Timestamp in item['title']):
                    SceneLayer = item
                if (item['type'] == 'Scene Package') & (Timestamp in item['title']):
                    ScenePackage = item    
    try: SceneLayer
    except NameError: SceneLayer=None
    try: ScenePackage
    except NameError: ScenePackage=None

    if SceneLayer: 
        arcpy.AddMessage("... Older SceneLayer file "+ str(SceneLayer.title)+ " found")
        SceneLayer.update(item_properties= {"access": "private"})
    else:
        arcpy.AddMessage("... No older SceneLayer file found")

    if ScenePackage: 
        arcpy.AddMessage("... Older ScenePackage file "+ str(ScenePackage.title)+" found")
        ScenePackage.update(item_properties= {"access": "private"})
    else:
        arcpy.AddMessage("... No older ScenePackage file found")
                    
    # 1.2 Get the item id and use get() method to access item object and data
    if SceneLayer: 
        SceneLayerID = SceneLayer.id 
        SceneLayerObj = gis.content.get(SceneLayerID)
        #CopyOldSceneLayerObj = SceneLayerObj.copy()         #Copy the existing SceneLayer and ScenePackage Item Objects
    if ScenePackage: 
        ScenePackageID = ScenePackage.id 
        ScenePackageObj = gis.content.get(ScenePackageID)
        #CopyOldScenePackageObj = ScenePackageObj.copy()     #Copy the existing SceneLayer and ScenePackage Item Objects

  
    # 1.3 Move the copies of the older file versions to the archive folder
    # First Check if archiveFolder to store files from older Workflow runs exists in the ArcGIS Online Portal
    # If True, move files to folder. If false, create folder, then move files to folder
    arcpy.AddMessage("... Checking for Archive Folder")
    archiveFolder_exists = False
    for folder in gis.users.me.folders:
        if folder['title'] == "Archived " + LayerName + " Layers":
            arcpy.AddMessage("... Archive Folder exists")
            archiveFolder_exists = True
    if not archiveFolder_exists:
        arcpy.AddMessage("... Archive Folder not found. Creating new folder in ArcGIS Online Portal")
        gis.content.create_folder(folder= "Archived " + LayerName + " Layers")
    if SceneLayer:
        arcpy.AddMessage("... Moving copy of older SceneLayer file to Archive Folder")
        SceneLayerObj.move(folder = "Archived " + LayerName + " Layers")
    if ScenePackage:
        arcpy.AddMessage("... Moving copy of older ScenePackage file to Archive Folder")
        ScenePackageObj.move(folder = "Archived " + LayerName + " Layers")
        
    arcpy.AddMessage("... Older files archived")

    # 2. Create Scene Layer Package
    inSceneLayer = inSceneLayer+".lyrx"
    inSceneLayer = inSceneLayer.replace(os.sep, '/')
    arcpy.AddMessage("... Input Scene Layer: "+inSceneLayer)
    inSceneLayerName = (inSceneLayer.split('.')[0])
    change_date = datetime.datetime.now().strftime("%y%m%d%H%M")
    outSceneLayerName = inSceneLayerName + '_'+ change_date 
    outSceneLayerPackage = os.path.join(temporary_LayerFolder, outSceneLayerName)
    arcpy.AddMessage("... Creating Scene Layer Package to folder: " + str(outSceneLayerPackage))
    arcpy.CreatePointSceneLayerPackage_management(inSceneLayer, outSceneLayerPackage)


    # 3. Update Scene Layer
    # Update SceneLayer with with new PointSceneLayer File (.slpk layer file)
    # 3.1 Share new Scene Layer Package if no ScenePackage is available in the ArcGIS Online Portal Folder
    portal_folder = LayerName
    outSceneLayerPackage = outSceneLayerPackage+".slpk"     # Add Layer Package Extension to file Path
    arcpy.AddMessage("... Sharing new Scene Layer Package to ArcGIS Online Portal")
    shared_result = arcpy.SharePackage_management(outSceneLayerPackage, username="tschatim_student", password="e7QtZkK:4!NBaUX", summary=
                                "SceneLayer Visualising Meteorogical Parameters for 3D-SigWX", tags="SceneLayer, 3D-SigWX", public='EVERYBODY',
                                publish_web_layer="TRUE", portal_folder=portal_folder)
    for folder in gis.users.me.folders:
        if folder['title'] == LayerName:
            for item in gis.users.me.items(folder['title']):
                if (item['type'] == 'Scene Service') & (Timestamp in item['title']):
                    NewSceneLayer = item
                if (item['type'] == 'Scene Package') & (Timestamp in item['title']):
                    NewScenePackage = item
    NewSceneLayer.update(item_properties= {"access": "public", "description": descriptionDate})
    NewScenePackage.update(item_properties= {"access": "public", "description": descriptionDate})

    if shared_result:
        arcpy.AddMessage("... Shared to ArcGIS Online Folder: "+ str(portal_folder))
    


    arcpy.AddMessage("END Share Scene Layer Workflow")
    arcpy.AddMessage('SUCCESS: Share Scene Layer Workflow ended without interruptions')
   


