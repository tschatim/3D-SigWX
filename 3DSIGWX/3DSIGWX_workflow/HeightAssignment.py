'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  HeightAssignment5
 Source Name:       HeightAssignment5.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    ncVarName
                    Interpolation Parameters
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


def reclassify_height(GeometricHeight, VariableData, zCoordinates, AmountofLayers, MaxHeight, fillValue):
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
        zCoordinates: int
            Vertical Layer numbers
        AmountofLayers: int
            Number of Layers in new vertical coordinate system
        MaxHeight: int
            Heighest interpolated Layer in new vert. coord. system
        fillValue: float
            Default value

        Returns
        -------
        outVariableData: array
            Interpolated data
    """
    GeometricHeight = np.array(GeometricHeight)
    
    # Define Fixed Z layer spacing 
    maxHeight =  np.max(GeometricHeight)
    minHeight = np.min(GeometricHeight)
    min_indices = np.empty(3)
    shapeVariableData = list(np.shape(VariableData))
    shapeVariableData[1] = AmountofLayers
    shapeVariableData = tuple(shapeVariableData)
    outVariableData = np.empty(shapeVariableData)
    
    arcpy.AddMessage('... Interpolating Data')
    # Reclassify Height 
    for height in zCoordinates:
        for i in range(GeometricHeight.shape[1]):       # latitude
            for j in range(GeometricHeight.shape[2]):   # longitude
                if GeometricHeight[0,i,j] < -100000:    # Check for NaN Values in Geometric Height
                    pass
                else:
                    delta_height = (abs(height - GeometricHeight[:-2,i,j]))     # Distance from every geometric height layer at point (x[j], y[i]) to the Z-Coordinate "height"
                    min_indices[0] =np.where(np.isclose(delta_height, np.sort(delta_height)[0]))[0][0]
                    min_indices[1] =np.where(np.isclose(delta_height, np.sort(delta_height)[1]))[0][0]
                    min_indices[2] =np.where(np.isclose(delta_height, np.sort(delta_height)[2]))[0][0]

                    # Check, if z-Coordinate is between the two geometric height layers geometricHeight[min_indices[0]] and geometricHeight[min_indices[1]]
                    if (height - GeometricHeight[int(min_indices[0]),i,j]) * (height - GeometricHeight[int(min_indices[1]),i,j]) < 0:
                        # Interpolation
                        heightDiffLayers = abs(GeometricHeight[int(min_indices[1]),i,j] -GeometricHeight[int(min_indices[0]),i,j])    # Difference between higher and lower layer
                        heightDiffZCoord = abs(height-GeometricHeight[int(min_indices[0]),i,j])  # Difference between z-Coordinate (middle point) and lower Layer
                        ratio = heightDiffZCoord/heightDiffLayers
                        interpolatedVariableData = VariableData[0, int(min_indices[0]), i,j]- (VariableData[0, int(min_indices[0]), i,j] - VariableData[0, int(min_indices[1]), i,j])*ratio      # Time dimension also iterable (if more than one timestamp)
                    elif (height - GeometricHeight[int(min_indices[0]),i,j]) * (height - GeometricHeight[int(min_indices[2]),i,j]) < 0:
                        # Interpolation
                        heightDiffLayers = abs(GeometricHeight[int(min_indices[2]),i,j] -GeometricHeight[int(min_indices[0]),i,j])    # Difference between higher and lower layer
                        heightDiffZCoord = abs(height-GeometricHeight[int(min_indices[0]),i,j])  # Difference between z-Coordinate (middle point) and lower Layer
                        ratio = heightDiffZCoord/heightDiffLayers
                        interpolatedVariableData = VariableData[0, int(min_indices[0]), i,j]- (VariableData[0, int(min_indices[0]), i,j] - VariableData[0, int(min_indices[2]), i,j])*ratio      # Time dimension also iterable (if more than one timestamp)
                    else:
                        interpolatedVariableData = fillValue  # If z-Coordinate "height" is below the two nearest geometric height layers, set Variable Value to 0.0 (Point is below the terrain)

                    heightIndex = np.where(np.isclose(zCoordinates, height))[0][0]
                    outVariableData[0, heightIndex, i, j] = interpolatedVariableData       # Time dimension also iterable (if more than one timestamp)

        arcpy.AddMessage('    height: '+ str(height))
    return outVariableData





def HeightAssignment(inNetCDFFileName, ncVarName: list, current_geodatabase, AmountofLayers, MaxHeight, LayerName, Timestamp):
    """
        Function Description: 
        Transforms the Variable specified by "ncVarName" from the Level Based Coordinate system of 
        the COSMO Output file to a new z-Coordinate System by Interpolating the Variable Values.
        Writes a new netCDF file containing the transformed variable.

        Parameters
        ----------
        inNetCDFFileName: string
            Name of Input NetCDF File
        ncVarName: list
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
    unique_name = arcpy.CreateUniqueName(Timestamp + "_" + LayerName + "_HeightAssigned_netCDF.nc", workspace=current_geodatabase)
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

    for varName in ncVarName:
        if list(ncVarNames).count(varName) == 0:
            arcpy.AddError("NetCDF variable " + varName + " does not exist.")              
            raise Exception (msgInvalidParameter)
        arcpy.AddMessage("... netCDF variable " + varName + " exists")

    # 1.3 Get Dimensions of independent Variable
    ncDimNames = inNetCDFFile.variables[ncVarName[0]].dimensions
    ncDimNames = list(ncDimNames) 
    ncDimNames[1] = 'Z'

    #1.4 Check if X, Y, Z dimensions exist
    xDimension = 'longitude'
    yDimension = 'latitude'
    zDimension = 'Z'
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

    
    # 3. Construction of new z-Coordinate Frame 
    zCoordinates = np.linspace(MaxHeight, 0, num = AmountofLayers)   # Divide Vertical Spacing in to uniform spacing (Reversed because of order of geometric height)
    

    # 4. Create new Output NetCDF file
    outNetCDFFile = Dataset(outNetCDFFileName, 'w', format = 'NETCDF4_CLASSIC')
    arcpy.AddMessage("... creating output netCDF file " + outNetCDFFileName)    
    

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
            
    # 6. Write Output Variables
    for varName in ncVarName:
        # 6.1 Get the specified dependent variable object from netCDF Input File
        ncVarObj = inNetCDFFile.variables[varName]
        ncVarData = inNetCDFFile.variables[varName][:]

        # 6.2 Interpolation of dependent variable data
        [interpolatedVariableData] = reclassify_height(heightData, ncVarData, zCoordinates, AmountofLayers, MaxHeight, fill_value)

        # 6.3. Create Variable with new dimension "height" in outNetCDF file and assign values
        ncVarDim = list(inNetCDFFile.variables[varName].dimensions)
        for index, value in enumerate((ncVarDim)):
            if value in ['z_1', 'z_2','z_5']:
                ncVarDim[index] = zDimension

        outNcVar = outNetCDFFile.createVariable(varName, 'f4', (ncVarDim), fill_value = -3.4028235e+38)
        outNcVar[:, :, :, :] = interpolatedVariableData[:]                    

        # 6.4 Get Variable Attributes and assign to new outVariable
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
        arcpy.AddMessage("... writing variable attributes for " + varName)
        
        
        # 6.5 Get grid_mapping variable object if exists
        if bGridMappingExists:
            ncGridMappingVar = inNetCDFFile.variables[ncGridMappingVarName]        
            ncGridMappingVarShape = ncGridMappingVar.shape        
            ncGridMappingVarDimNames = ncGridMappingVar.dimensions         
            
            #6.5.1 Create grid mapping variable in outnetCDFfile 
            outNcGridMappingVar = outNetCDFFile.createVariable(ncGridMappingVarName, ncGridMappingVar.typecode(), ncGridMappingVarDimNames)   
            
            allGridMappingAttributes = dir(ncGridMappingVar)
            for gridmappingattrib in allGridMappingAttributes:
                if gridmappingattrib not in ['assignValue', 'getValue', 'typecode']:
                    gridmappingAttribValue = getattr(ncGridMappingVar, gridmappingattrib)
                    setattr(outNcGridMappingVar, gridmappingattrib, gridmappingAttribValue)
            arcpy.AddMessage("... writing grid_mapping for " + varName)

    # 7. Add a new NetCDF Variable for the Vertical Level Numbers 
    outNcVarLevels = outNetCDFFile.createVariable('LayerLevel', 'f4', ("time", "Z", "latitude", "longitude"), fill_value = -3.4028235e+38)
    shapeNcVarLevels = ["0", "0", "0", "0"]
    shapeNcVarLevels[0] = 1 # Time Dimension
    shapeNcVarLevels[1] = AmountofLayers
    shapeNcVarLevels[2] = np.shape(heightData)[1]
    shapeNcVarLevels[3] = np.shape(heightData)[2]
    shapeNcVarLevels = tuple(shapeNcVarLevels)
    outVarLevelsData = np.empty(shapeNcVarLevels)
    for levels in range(AmountofLayers):
        for i in range(heightData.shape[1]):       # latitude
            for j in range(heightData.shape[2]):   # longitude
                outVarLevelsData[0, levels, i, j] = AmountofLayers - levels
    outNcVarLevels[:, :, :, :] = outVarLevelsData[:]


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

