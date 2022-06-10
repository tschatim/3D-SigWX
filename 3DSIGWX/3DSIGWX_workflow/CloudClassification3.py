'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  Cloud Classification
 Source Name:       CloudClassification.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    NetCDF CLC variable name
                    Output netCDF File

 Description:       ArcGIS Tool to classify the Cloud-Cover of each Cell of the COSMO netCDF file
                    to the unit of Okta (0-8). For this Purpose the CLC cloud cover value in the 
                    range of 0-100% from the Input netCDF file is reclassified and an output
                    netCDF file is generated.
                    
----------------------------------------------------------------------------------'''


#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset
from netCDF4 import Variable
import netCDF4



def cloud_classification(CLCData):
    """
        Function Description: 
        Classifying the CLC value at each (t,z,lat,lon)-Datapoint to a Okta value. 

        Parameters
        ----------
        CLCData: array
            Array of CLC Values
        
        Returns
        -------
        outVariableData: array
            Classified CLC values
    """
    fill_value = -3.4028235e+38
    
    CLCData = np.array(CLCData)
    shapeCLCData = np.shape(CLCData)
    shapeCLCData = tuple(shapeCLCData) 

    outVariableData = np.empty(shapeCLCData)    # Create empty output array

    arcpy.AddMessage('... Classifying Data')
    # Classify CLC Values to Categories 
    for time in range(shapeCLCData[0]):
        for zcoord in range(shapeCLCData[1]):
            arcpy.AddMessage('    Z-Coordinate: ' + str(zcoord))
            for i in range(shapeCLCData[2]):   # latitude
                for j in range(shapeCLCData[3]): # longitude 
                    if (CLCData[time, zcoord, i, j] > 0) & (CLCData[time, zcoord, i, j] < 6.25):
                        outVariableData[time, zcoord, i, j] = 0
                    
                    elif (CLCData[time, zcoord, i, j] >= 6.25) & (CLCData[time, zcoord, i, j] < 18.75):
                        outVariableData[time, zcoord, i, j] = 1

                    elif (CLCData[time, zcoord, i, j] >= 18.75) & (CLCData[time, zcoord, i, j] < 31.25):
                        outVariableData[time, zcoord, i, j] = 2

                    elif (CLCData[time, zcoord, i, j] >= 31.25) & (CLCData[time, zcoord, i, j] < 43.75):
                        outVariableData[time, zcoord, i, j] = 3

                    elif (CLCData[time, zcoord, i, j] >= 43.75 ) & (CLCData[time, zcoord, i, j] < 56.25):
                        outVariableData[time, zcoord, i, j] = 4

                    elif (CLCData[time, zcoord, i, j] >= 56.25) & (CLCData[time, zcoord, i, j] < 68.75):
                        outVariableData[time, zcoord, i, j] = 5

                    elif (CLCData[time, zcoord, i, j] >= 68.75) & (CLCData[time, zcoord, i, j] < 81.25):
                        outVariableData[time, zcoord, i, j] = 6

                    elif (CLCData[time, zcoord, i, j] >= 81.25) & (CLCData[time, zcoord, i, j] < 93.75):
                        outVariableData[time, zcoord, i, j] = 7

                    elif (CLCData[time, zcoord, i, j] >= 93.75) & (CLCData[time, zcoord, i, j] <= 100):
                        outVariableData[time, zcoord, i, j] = 8
                    else:
                        outVariableData[time, zcoord, i, j] = fill_value    # If CLC = 0% the fill_value (NaN) is inserted, thus no feature will be created in the feature layer
    
    return outVariableData

                




def CloudClassification(inNetCDFFileName, current_geodatabase, LayerName, Timestamp):
    """
        Function Description: 
        Classifies the cloud coverage at each (t,z,lat,lon)-Cell to Okta values based
        on the cloud area fraction variable "CLC" in the input netCDF file (given in percentage).

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
    """
    arcpy.AddMessage('\nSTART Cloud Area Fraction Classification')

    #Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"
    
    unique_name = arcpy.CreateUniqueName(Timestamp + "_" + LayerName + "_Classified_netCDF.nc", workspace=current_geodatabase)
    outNetCDFFileName = unique_name      
    ncVarCLC = 'CLC'
    outVarCloud = 'CloudClassification'

    fill_value = -3.4028235e+38

    # 1. Import NetCDF Input File with CLC Values
    #1.1 Open the netCDF file and get variables
    inNetCDFFile = Dataset(inNetCDFFileName, 'r')
    ncVarNames = inNetCDFFile.variables.keys()
    ncDimNames = inNetCDFFile.dimensions.keys()
    ncDimNames = list(ncDimNames) 

    
    #1.2 Check if netCDF variable exists
    if list(ncVarNames).count(ncVarCLC) == 0:
        arcpy.AddError("NetCDF variable " + ncVarCLC + " does not exist.")              
        raise Exception (msgInvalidParameter)
    arcpy.AddMessage("... netCDF variable " + ncVarCLC + " exists")


    #1.3 Check if X, Y, Z dimensions exist
    xDimension = 'longitude'
    yDimension = 'latitude'
    zDimension = 'Z'
    for Dimension in list((xDimension, yDimension, zDimension)):
        if list(ncDimNames).count(Dimension) == 0:
            arcpy.AddError("NetCDF Dimension " + Dimension + " does not exist.")              
            raise Exception (msgInvalidParameter)
        arcpy.AddMessage("... netCDF Dimension " + Dimension + " exists")



    # 2. Extract CLC Values from netCDF Input File
    # 2.1 Get netCDF CLC variable object
    ncVarCLCObj = inNetCDFFile.variables[ncVarCLC]
    ncVarCLCData = inNetCDFFile.variables[ncVarCLC][:]

    
    # 3. Classification of CLC Values 
    classifiedVariableData = cloud_classification(ncVarCLCData)

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

            # 5.2.1 Assign Attributes to Coordinate Variables
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

    # 6. Create Variable CloudClassification with new classified values
    ncVarCloudDim = list(inNetCDFFile.variables[ncVarCLC].dimensions)
    outNcVar = outNetCDFFile.createVariable(outVarCloud, 'f4', (ncVarCloudDim), fill_value = -3.4028235e+38)
    outNcVar[:, :, :, :] = classifiedVariableData[:]                    

    # 7. Get Variable Attributes and assign to new outVariable
        #    Also determine if grid_mapping exists or not
    bGridMappingExists = False
    ncGridMappingVarName = ""
    allAttributes = dir(ncVarCLCObj)

    arcpy.AddMessage("... writing variable attributes for " + ncVarCLC) 
    for attrib in allAttributes:
        if attrib not in ['assignValue', 'getValue', 'typecode', 'coordinates', '_FillValue', '__array__', '__class__', '__delattr__', '__delitem__', '__dir__', '__doc__', 
                '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__len__', 
                '__lt__', '__ne__', '__new__', '__orthogonal_indexing__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 
                '__unicode__', '_assign_vlen', '_check_safecast', '_cmptype', '_enumtype', '_get', '_getdims', '_getname', '_grp', '_grpid', '_has_lsd', '_iscompound', '_isenum', 
                '_isprimitive', '_isvlen', '_name', '_ncstring_attrs__', '_nunlimdim', '_pack', '_put', '_toma', '_use_get_vars', '_varid', '_vltype', 'always_mask', 
                'chartostring', 'chunking', 'datatype', 'delncattr', 'dimensions', 'dtype', 'endian', 'filters', 'getValue', 'get_dims', 'get_var_chunk_cache', 'getncattr', 
                'group', 'mask', 'name', 'ncattrs', 'ndim', 'renameAttribute', 'scale', 'set_always_mask', 'set_auto_chartostring', 'set_auto_mask', 'set_auto_maskandscale', 'set_auto_scale', 
                'set_collective', 'set_ncstring_attrs', 'set_var_chunk_cache', 'setncattr', 'setncattr_string', 'setncatts','shape', 'size', 'use_nc_get_vars']:
            attribValue = netCDF4.Variable.getncattr(ncVarCLCObj, attrib)
            netCDF4.Variable.setncattr(outNcVar, attrib, attribValue)
            if attrib == "grid_mapping":
                bGridMappingExists = True
                ncGridMappingVarName = attribValue
    
    # 8. Get grid_mapping variable object if exists
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
        arcpy.AddMessage("... writing grid_mapping for " + ncVarCLC)


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

    arcpy.AddMessage('END Classifying Cloud Area Fraction\n\n')


    return [unique_name, outVarCloud]






