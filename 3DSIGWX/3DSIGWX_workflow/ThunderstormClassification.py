'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  Thunderstorm Classification
 Source Name:       ThunderstormClassification.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    NetCDF CLC variable name
                    Output netCDF File

 Description:       Workflow to classify the storm potential at each (t,z,lat,lon)-Cell based
                    on the CAPE_MU variable in the input netCDF file (given in J/kg).
                    
  
----------------------------------------------------------------------------------'''


#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset
from netCDF4 import Variable
import netCDF4



def storm_classification(CAPEData):
    """
        Function Description: 
        Classifying the CAPE_MU value at each (t,z,lat,lon)-Datapoint. 

        Parameters
        ----------
        CAPE_MUData: array
            Array of CAPE_MU Values
        
        Returns
        -------
        outVariableData: array
            Classified CAPE_MU values
    """
    fill_value = -3.4028235e+38
    
    CAPEData = np.array(CAPEData)
    shapeCAPEData = np.shape(CAPEData)
    shapeCAPEData = tuple(shapeCAPEData) 

    outVariableData = np.empty(shapeCAPEData)    # Create empty output array

    arcpy.AddMessage('... Classifying Data')
    # Classify CLC Values to Categories 
    for time in range(shapeCAPEData[0]):
        for zcoord in range(shapeCAPEData[1]):
            arcpy.AddMessage('    Z-Coordinate: ' + str(zcoord))
            for i in range(shapeCAPEData[2]):   # latitude
                for j in range(shapeCAPEData[3]): # longitude                     
                    if (CAPEData[time, zcoord, i, j] >= 500) & (CAPEData[time, zcoord, i, j] <= 1000):
                        outVariableData[time, zcoord, i, j] = 1
                    
                    elif (CAPEData[time, zcoord, i, j] > 1000) & (CAPEData[time, zcoord, i, j] <= 2000):
                        outVariableData[time, zcoord, i, j] = 2
                    
                    elif (CAPEData[time, zcoord, i, j] > 2000) & (CAPEData[time, zcoord, i, j] <= 3000):
                        outVariableData[time, zcoord, i, j] = 3

                    elif (CAPEData[time, zcoord, i, j] > 3000):
                        outVariableData[time, zcoord, i, j] = 4

                    else:
                        outVariableData[time, zcoord, i, j] = fill_value    # If 0<CAPE_MU<500 the fill_value (NaN) is inserted, thus no feature will be created in the feature layer
    
    return outVariableData

                


def StormClassification(inNetCDFFileName, current_geodatabase, LayerName, Timestamp):
    """
        Function Description: 
        Classifies the storm potential at each (t,z,lat,lon)-Cell based
        on the CAPE_MU variable in the input netCDF file (given in J/kg).

        Parameters
        ----------
        inNetCDFFileName: string
            Name of Input NetCDF File
        current_geodatabase: string
            Path to the current project geodatabase (to save the output file)
        LayerName: string
            Name of Layer (corresponds to Meteorological Parameter)
        Timestamp: string
            Timestamp of the current NetCDF file 

        Returns
        -------
        unique_name: string
            Name of the output NetCDF file
        outVarCAPE: string
            Variable Name in outNetCDF file 
    """
    arcpy.AddMessage('\nSTART CAPE Classification')

    #Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"
    
    
    #inNetCDFFileName = "CapeRegrid_netCDF.nc"
    unique_name = arcpy.CreateUniqueName(Timestamp + "_" + LayerName + "_Classified_netCDF.nc", workspace=current_geodatabase)
    outNetCDFFileName = unique_name      
    #outNetCDFFileName = "StormClassified_netCDF.nc"
    ncVarCAPE = 'CAPE_MU'
    outVarCAPE = 'StormClassification'

    fill_value = -3.4028235e+38

    # 1. Import NetCDF Input File with CAPE Values
    #1.1 Open the netCDF file and get variables
    inNetCDFFile = Dataset(inNetCDFFileName, 'r')
    ncVarNames = inNetCDFFile.variables.keys()
    ncDimNames = inNetCDFFile.dimensions.keys()
    ncDimNames = list(ncDimNames) 

    
    #1.2 Check if netCDF variable exists
    if list(ncVarNames).count(ncVarCAPE) == 0:
        arcpy.AddError("NetCDF variable " + ncVarCAPE + " does not exist.")              
        raise Exception (msgInvalidParameter)
    arcpy.AddMessage("... netCDF variable " + ncVarCAPE + " exists")


    #1.3 Check if X, Y, Z dimensions exist
    xDimension = 'longitude'
    yDimension = 'latitude'
    zDimension = 'Z'
    for Dimension in list((xDimension, yDimension, zDimension)):
        if list(ncDimNames).count(Dimension) == 0:
            arcpy.AddError("NetCDF Dimension " + Dimension + " does not exist.")              
            raise Exception (msgInvalidParameter)
        arcpy.AddMessage("... netCDF Dimension " + Dimension + " exists")


    # 2. Extract CAPE Values from netCDF Input File
    # 2.1 Get netCDF CAPE variable object
    ncVarCAPEObj = inNetCDFFile.variables[ncVarCAPE]
    ncVarCAPEData = inNetCDFFile.variables[ncVarCAPE][:]

    
    # 3. Classification of CAPE Values 
    classifiedVariableData = storm_classification(ncVarCAPEData)

    # 4. Create new Output NetCDF file
    outNetCDFFile = Dataset(outNetCDFFileName, 'w', format = 'NETCDF4_CLASSIC')


    # 5. Create Dimensions
    for dimName in ncDimNames:       
        #Set output dimension size    
        if dimName == xDimension:
            dimSize = len(inNetCDFFile.variables[dimName])
        elif dimName == yDimension:
            dimSize = len(inNetCDFFile.variables[dimName])
        elif dimName == zDimension:
            dimSize = len(inNetCDFFile.variables[dimName])     
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

            # 5.2.2 Assign Attributes to Coordinate Variables
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


    # 6. Create Variable StormClassification with new classified values
    ncVarCloudDim = list(inNetCDFFile.variables[ncVarCAPE].dimensions)
    outNcVar = outNetCDFFile.createVariable(outVarCAPE, 'f4', (ncVarCloudDim), fill_value = -3.4028235e+38)
    outNcVar[:, :, :, :] = classifiedVariableData[:]                    

    # 7. Get Variable Attributes and assign to new outVariable
        #    Also determine if grid_mapping exists or not
    bGridMappingExists = False
    ncGridMappingVarName = ""
    allAttributes = dir(ncVarCAPEObj)

    arcpy.AddMessage("... writing variable attributes for " + ncVarCAPE) 
    for attrib in allAttributes:
        if attrib not in ['assignValue', 'getValue', 'typecode', 'coordinates', '_FillValue', '__array__', '__class__', '__delattr__', '__delitem__', '__dir__', '__doc__', 
                '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__len__', 
                '__lt__', '__ne__', '__new__', '__orthogonal_indexing__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 
                '__unicode__', '_assign_vlen', '_check_safecast', '_cmptype', '_enumtype', '_get', '_getdims', '_getname', '_grp', '_grpid', '_has_lsd', '_iscompound', '_isenum', 
                '_isprimitive', '_isvlen', '_name', '_ncstring_attrs__', '_nunlimdim', '_pack', '_put', '_toma', '_use_get_vars', '_varid', '_vltype', 'always_mask', 
                'chartostring', 'chunking', 'datatype', 'delncattr', 'dimensions', 'dtype', 'endian', 'filters', 'getValue', 'get_dims', 'get_var_chunk_cache', 'getncattr', 
                'group', 'mask', 'name', 'ncattrs', 'ndim', 'renameAttribute', 'scale', 'set_always_mask', 'set_auto_chartostring', 'set_auto_mask', 'set_auto_maskandscale', 'set_auto_scale', 
                'set_collective', 'set_ncstring_attrs', 'set_var_chunk_cache', 'setncattr', 'setncattr_string', 'setncatts','shape', 'size', 'use_nc_get_vars']:
            attribValue = netCDF4.Variable.getncattr(ncVarCAPEObj, attrib)
            netCDF4.Variable.setncattr(outNcVar, attrib, attribValue)
            if attrib == "grid_mapping":
                bGridMappingExists = True
                ncGridMappingVarName = attribValue
    
    #8. Get grid_mapping variable object if exists
    if bGridMappingExists:
        ncGridMappingVar = inNetCDFFile.variables[ncGridMappingVarName]        
        ncGridMappingVarShape = ncGridMappingVar.shape        
        ncGridMappingVarDimNames = ncGridMappingVar.dimensions 
        
        #8.1 Create grid mapping variable in outnetCDFfile 
        outNcGridMappingVar = outNetCDFFile.createVariable(ncGridMappingVarName, ncGridMappingVar.typecode(), ncGridMappingVarDimNames)   
        
        allGridMappingAttributes = dir(ncGridMappingVar)
        for gridmappingattrib in allGridMappingAttributes:
            if gridmappingattrib not in ['assignValue', 'getValue', 'typecode']:
                gridmappingAttribValue = getattr(ncGridMappingVar, gridmappingattrib)
                setattr(outNcGridMappingVar, gridmappingattrib, gridmappingAttribValue)
        arcpy.AddMessage("... writing grid_mapping for " + ncVarCAPE)


    # 9. Write all global attributes
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


    # 10. Synchronize and close NetCDF files
    outNetCDFFile.sync()    
    outNetCDFFile.close()
    inNetCDFFile.close()

    arcpy.AddMessage('END Classifing CAPE Values\n\n')


    return [unique_name, outVarCAPE]






