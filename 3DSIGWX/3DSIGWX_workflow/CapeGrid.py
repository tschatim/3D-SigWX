'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  CapeGrid
 Source Name:       CapeGrid.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    ncVarName
                    Output netCDF File

 Description:       Convert Values from the independent Variable from the level-based (level, latitude, longitude)-
                    Coordinate System to the (Z, latitude, longitude)-Coordinate System, where Z is the height in [m].
                    For this purpose, the geometric height variable in the COSMO-NetCDF Data is used to assign every 
                    dependent Variable Value at Datapoints in the (levels, lat, lon)-System to a geometric 
                    height value. Afterwards the dependent variable values at Datapoints in the (Z, lat, lon) are determined
                    by Interpolation using the nearest points above and below the Z-coordinate.
                    
  
----------------------------------------------------------------------------------'''

#Import required modules

import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset
from netCDF4 import Variable
import netCDF4

def CapeRegrid(GeometricHeight, VariableData, AmountofLayers, MaxHeight):
    """
        Function Description: 
        Creating new z-Coordinates with "nVertLayers"-Layers. Assigning a Geometric Height to each Level Based
        Datapoint of the COSMO Output. Interpolating the Values of the variable "VariableData" to the new 
        z-Coordinates.

        Parameters
        ----------
        GeometricHeight: array
            array of netCDF variable "height"
        VariableData: array
            Values from the Variable to interpolate
        AmountofLayers: int
            Number of Layers in new vertical coordinate system
        MaxHeight: int
            Heighest interpolated Layer in new vert. coord. system

        Returns
        -------
        outVariableData: array
            Interpolated data
        HeightSpacing: int
            Vertical Layer numbers
    """
    GeometricHeight = np.array(GeometricHeight)
    
    # Define Fixed Z layer spacing 
    maxHeight =  np.max(GeometricHeight)
    minHeight = np.min(GeometricHeight)
    heightSpacing = np.linspace(MaxHeight, 0, num = AmountofLayers)   # Divide Vertical Spacing in to uniform spacing (Reversed because of order of geometric height)
    min_indices = np.empty(2)
    shapeVariableData = list(np.shape(VariableData))
    shapeVariableData.insert(1, AmountofLayers)
    shapeVariableData = tuple(shapeVariableData)
    outVariableData = np.empty(shapeVariableData)
    
    arcpy.AddMessage('... regrid data')
    # Reclassify Height 
    for height in range(AmountofLayers):
        for i in range(GeometricHeight.shape[1]):       # latitude
            for j in range(GeometricHeight.shape[2]):   # longitude
                if GeometricHeight[0,i,j] < -100000:    # Check for NaN Values in Geometric Height
                    pass
                else:
                    CapeValue = VariableData[0,i,j]
                    outVariableData[0, height, i, j] = CapeValue      # Time dimension also iterable (if more than one timestamp)

        arcpy.AddMessage('    height: '+ str(height))
    return outVariableData, heightSpacing

def CapeGridAssignment(inNetCDFFileName, ncVarName, current_geodatabase, AmountofLayers, MaxHeight, LayerName, Timestamp):
    """
        Function Description: 
        Transforms the Variable CAPE to a three dimensional coordinate system.
        Writes a new netCDF file containing the transformed variable.

        Parameters
        ----------
        inNetCDFFileName: string
            Name of Input NetCDF File
        ncVarName: string
            Name of the variable to be transformed
        current_geodatabase: string
            Path to the current project geodatabase (to save the output file)
        AmountofLayers: int
            Number of Layers in new vertical coordinate system
        MaxHeight: int
            Heighest interpolated Layer in new vert. coord. system
        LayerName: string
            Name of Layer (corresponds to Meteorological Parameter)
        Timestamp: string
            Timestamp of the current NetCDF file 
        
        Returns
        -------
        unique_name: string
            Name of the output NetCDF file 
    """
    arcpy.AddMessage('\nSTART Transforming to Z-Coordinates')

    ncVarHeight = 'HEIGHT'
    unique_name = arcpy.CreateUniqueName(Timestamp + "_" + LayerName + "_CapeRegrid_netCDF.nc", workspace=current_geodatabase)
    outNetCDFFileName = unique_name    

    fill_value = -3.4028235e+38

    #Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"


    # 1. Load netCDF File
    #1.1 Open the netCDF file and get variables
    inNetCDFFile = Dataset(inNetCDFFileName, 'r')
    ncVarNames = inNetCDFFile.variables.keys()
    
    #1.2 Check if netCDF variable "Height" and "ncVarName" exist
    if list(ncVarNames).count(ncVarHeight) == 0:
        arcpy.AddError("NetCDF variable " + ncVarHeight + " does not exist.")              
        raise Exception (msgInvalidParameter)
    arcpy.AddMessage("... netCDF variable " + ncVarHeight + " exists")

    if list(ncVarNames).count(ncVarName) == 0:
        arcpy.AddError("NetCDF variable " + ncVarName + " does not exist.")              
        raise Exception (msgInvalidParameter)
    arcpy.AddMessage("... netCDF variable " + ncVarName + " exists")

    # 1.3 Get Dimensions of independent Varibale
    xDimension = 'longitude'
    yDimension = 'latitude'
    zDimension = 'Z'
    ncDimNames = inNetCDFFile.variables[ncVarName].dimensions
    ncDimNames = list(ncDimNames)
    ncDimNames.insert(1, zDimension)

    #1.4 Check if X, Y, Z dimensions exist
    for Dimension in list((xDimension, yDimension, zDimension)):
        if list(ncDimNames).count(Dimension) == 0:
            arcpy.AddError("NetCDF Dimension " + Dimension + " does not exist.")              
            raise Exception (msgInvalidParameter)
        arcpy.AddMessage("... netCDF Dimension " + Dimension + " exists")
    


    # 2. Extract variable Geometric Height and Specified Dependent Variable from netCDF Input File
    # 2.1 Get the netCDF geometric height variable object 
    height = inNetCDFFile.variables[ncVarHeight]
    heightData = height[:]    
    heightShape = height.shape
    heightRank = len(heightData.shape)
    heightDimNames = height.dimensions 

    # 2.2 Get the specified dependent variable object from netCDF Input File
    ncVarObj = inNetCDFFile.variables[ncVarName]
    ncVarData = inNetCDFFile.variables[ncVarName][:]

    # 3. Construction of new z-Coordinate Frame and interpolation of dependent variable data
    [RegriddedData, zCoordinates] = CapeRegrid(heightData, ncVarData, AmountofLayers, MaxHeight)

    # 4. Create new Output NetCDF file
    outNetCDFFile = Dataset(outNetCDFFileName, 'w', format = 'NETCDF4')    

    # 5. Create Dimensions
    for dimName in ncDimNames:       
        #Set output dimension size    
        if dimName == xDimension:
            dimSize = len(inNetCDFFile.variables[dimName])
        elif dimName == yDimension:
            dimSize = len(inNetCDFFile.variables[dimName])
        elif dimName == zDimension:
            dimSize = len(zCoordinates)      
        else:
            dimSize = inNetCDFFile.dimensions[dimName].size
        
        #Adjust output dimension size if it is NONE (NONE is returned for UNLIITED size)
        #Getting actual size in file from shape
        if dimSize == None:
            ncCoordVar = inNetCDFFile.variables[dimName]
            dimSize = list(ncCoordVar.shape)[0]

        #5.1 Create dimension in outnetCDFfile
        outNetCDFFile.createDimension(dimName,dimSize)

        #5.2 Check if dimension is also a variable i.e. coordinate variable
        if dimName in ncVarNames:
            # Get coordinate variable    
            ncCoordVar = inNetCDFFile.variables[dimName]
            
            # Get data of variable
            ncCoordVarData = ncCoordVar[:] 
            
            #5.2.1 Create coordinate variable in outnetCDFfile           
            outNcCoordVar = outNetCDFFile.createVariable(dimName, 'f4', (dimName,), fill_value = -3.4028235e+38)
            outNcCoordVar[:] = ncCoordVarData

            CoordVarAttributes = dir(ncCoordVar)   
            for CoordVarAttrib in CoordVarAttributes:
                if CoordVarAttrib not in ['assignValue', 'getValue', 'typecode', 'coordinates', '_FillValue', '__array__', '__class__', '__delattr__', '__delitem__', '__dir__', '__doc__', 
                '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__len__', 
                '__lt__', '__ne__', '__new__', '__orthogonal_indexing__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 
                '__unicode__', '_assign_vlen', '_check_safecast', '_cmptype', '_enumtype', '_get', '_getdims', '_getname', '_grp', '_grpid', '_has_lsd', '_iscompound', '_isenum', 
                '_isprimitive', '_isvlen', '_name', '_ncstring_attrs__', '_nunlimdim', '_pack', '_put', '_toma', '_use_get_vars', '_varid', '_vltype', 'always_mask', 
                'chartostring', 'chunking', 'datatype', 'delncattr', 'dimensions', 'dtype', 'endian', 'filters', 'getValue', 'get_dims', 'get_var_chunk_cache', 'getncattr', 
                'group', 'mask', 'name', 'ncattrs', 'ndim', 'renameAttribute', 'scale', 'set_always_mask', 'set_auto_chartostring', 'set_auto_mask', 'set_auto_maskandscale', 'set_auto_scale', 
                'set_collective', 'set_ncstring_attrs', 'set_var_chunk_cache', 'setncattr', 'setncattr_string', 'setncatts','shape', 'size', 'use_nc_get_vars']:
                    CoordAttribValue = netCDF4.Variable.getncattr(ncCoordVar, CoordVarAttrib)
                    netCDF4.Variable.setncattr(outNcCoordVar, CoordVarAttrib, CoordAttribValue)

        
        # 5.3 Create new z-Coordinate variable for height
        if dimName == zDimension:
            outNcCoordVar = outNetCDFFile.createVariable(dimName, 'f4', (dimName), fill_value = -3.4028235e+38)
            netCDF4.Variable.setncattr(outNcCoordVar, 'axis', 'Z')
            netCDF4.Variable.setncattr(outNcCoordVar, 'units', 'meters')
            netCDF4.Variable.setncattr(outNcCoordVar, 'positive', 'down')
            netCDF4.Variable.setncattr(outNcCoordVar, 'standard_name', 'Z')
            outNcCoordVar[:] = zCoordinates[:]      # Assign new z-Coordinate values from reclassify_height function output to Height coordinate variable 
            
    
    outNcVar = outNetCDFFile.createVariable(ncVarName, 'f4', (ncDimNames), fill_value = -3.4028235e+38)
    outNcVar [:, :, :, :] = RegriddedData[:]                    

    # 6. Get Variable Attributes and assign to new outVariable
        #    Also determine if grid_mapping exists or not
    bGridMappingExists = False
    ncGridMappingVarName = ""
    allAttributes = dir(ncVarObj)
    for attrib in allAttributes:
        if attrib not in ['assignValue', 'getValue', 'typecode', 'coordinates', '_FillValue', '__array__', '__class__', '__delattr__', '__delitem__', '__dir__', '__doc__', 
                '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__len__', 
                '__lt__', '__ne__', '__new__', '__orthogonal_indexing__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 
                '__unicode__', '_assign_vlen', '_check_safecast', '_cmptype', '_enumtype', '_get', '_getdims', '_getname', '_grp', '_grpid', '_has_lsd', '_iscompound', '_isenum', 
                '_isprimitive', '_isvlen', '_name', '_ncstring_attrs__', '_nunlimdim', '_pack', '_put', '_toma', '_use_get_vars', '_varid', '_vltype', 'always_mask', 
                'chartostring', 'chunking', 'datatype', 'delncattr', 'dimensions', 'dtype', 'endian', 'filters', 'getValue', 'get_dims', 'get_var_chunk_cache', 'getncattr', 
                'group', 'mask', 'name', 'ncattrs', 'ndim', 'renameAttribute', 'scale', 'set_always_mask', 'set_auto_chartostring', 'set_auto_mask', 'set_auto_maskandscale', 'set_auto_scale', 
                'set_collective', 'set_ncstring_attrs', 'set_var_chunk_cache', 'setncattr', 'setncattr_string', 'setncatts','shape', 'size', 'use_nc_get_vars']:
            if attrib == 'cell_methods':
                netCDF4.Variable.setncattr(outNcVar, attrib, 'Z: interval')
            else:
                attribValue = netCDF4.Variable.getncattr(ncVarObj, attrib)
                netCDF4.Variable.setncattr(outNcVar, attrib, attribValue)
            if attrib == "grid_mapping":
                bGridMappingExists = True
                ncGridMappingVarName = attribValue
    arcpy.AddMessage("... writing variable attributes for " + ncVarName)
    
    
    #7. Get grid_mapping variable object if exists
    if bGridMappingExists:
        ncGridMappingVar = inNetCDFFile.variables[ncGridMappingVarName]        
        ncGridMappingVarShape = ncGridMappingVar.shape        
        ncGridMappingVarDimNames = ncGridMappingVar.dimensions       
        
        #7.1 Create grid mapping variable in outnetCDFfile 
        outNcGridMappingVar = outNetCDFFile.createVariable(ncGridMappingVarName, ncGridMappingVar.typecode(), ncGridMappingVarDimNames)   
        allGridMappingAttributes = dir(ncGridMappingVar)
        for gridmappingattrib in allGridMappingAttributes:
            if gridmappingattrib not in ['assignValue', 'getValue', 'typecode']:
                gridmappingAttribValue = getattr(ncGridMappingVar, gridmappingattrib)
                setattr(outNcGridMappingVar, gridmappingattrib, gridmappingAttribValue)
        arcpy.AddMessage("... writing grid_mapping for " + ncVarName)




    # 8. Write all global attributes
    globalAllAtributes = dir(inNetCDFFile)
    for globalAttribute in globalAllAtributes:
        if globalAttribute not in ['close', 'createDimension', 'createVariable', 'flush', 'sync', '__class__', '__delattr__', '__dir__', '__doc__', '__enter__', '__eq__', 
        '__exit__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', 
        '__new__', '__orthogonal_indexing__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__unicode__', '_close', 
        '_close_mem', '_enddef', '_getname', '_grpid', '_isopen', '_ncstring_attrs__', '_redef', 'cmptypes', 'createCompoundType', 'createDimension', 'createEnumType', 'createGroup', 'createVLType',
        'data_model', 'delncattr', 'dimensions', 'disk_format', 'enumtypes', 'file_format','filepath', 'get_variables_by_attributes', 'getncattr', 'groups', 'isopen', 'keepweakref', 'name', 'ncattrs',
        'parent', 'path', 'renameAttribute', 'renameDimension', 'renameGroup', 'renameVariable', 'set_always_mask', 'set_auto_chartostring', 'set_auto_mask', 'set_auto_maskandscale', 'set_auto_scale',
        'set_fill_off','set_fill_on', 'set_ncstring_attrs', 'setncattr', 'setncattr_string', 'setncatts', 'variables','vltypes','fromcdl','tocdl']:
            globalAttributeValue = netCDF4.Dataset.getncattr(inNetCDFFile, globalAttribute)
            netCDF4.Dataset.setncattr(outNetCDFFile, globalAttribute, globalAttributeValue)
    arcpy.AddMessage("... writing global attributes")


    # 9. Synchronize and close NetCDF files
    outNetCDFFile.sync()    
    outNetCDFFile.close()
    inNetCDFFile.close()

    arcpy.AddMessage('END Transforming to Z-Coordinates\n\n')

    
    return unique_name


