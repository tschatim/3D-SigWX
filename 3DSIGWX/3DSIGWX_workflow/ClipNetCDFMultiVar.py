'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  ClipNetCDF
 Source Name:       ClipNetCDF.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Environmental Systems Research Institute Inc.
                    Edited by Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    NetCDF variable name
                    X Dimension
                    Y Dimension
                    Value Selection Method (BY_INDEX or BY_VALUE)
                    Extent
                    Output netCDF File

 Description:       Clip netCDF variable based on the extent (Coordinates or Indices of vertices).
 
 Note: Auxiliary coordinate variables are dropped during clipping  
----------------------------------------------------------------------------------'''

#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset as NetCDFFile
import netCDF4


def getSlice(inArray,xMinIndex,yMinIndex,xMaxIndex,yMaxIndex,xDimensionIndex,yDimensionIndex,rank=1):
    """
        Function Description: This defines the extent (lat/lon), which is finally used to carry out the clipping.

        Parameters
        ----------
        inArray: array
            array of netCDF variable values
        xMinIndex: int
            Index of minimum x-extent value specified in Tool Input
        yMinIndex: int
            Index of minimum y-extent value specified in Tool Input
        xMaxIndex: int
            Index of maximum x-extent specified in Tool Input
        yMaxIndex: int
            Index of maximum y-extent specified in Tool Input
        xDimensionIndex: int
            Index of x-Dimension
        yDimensionIndex: int
            Index of y-Dimension
        rank: int
            Rank of the variable array (number of dimensions)

        Returns
        -------
        array
            Returns multidimensional array containing the variable values for the given extent and the given dimensions
    """
    #Get a subset of a multidimensional array
    args = [":" for i in range(rank) ]
    xRange = ":".join([str(xMinIndex), str(xMaxIndex+1)])
    yRange = ":".join([str(yMinIndex), str(yMaxIndex+1)])
    args[xDimensionIndex] = xRange
    args[yDimensionIndex] = yRange
    args = ",".join(args)
    execstring = "inArray" + "[" + args + "]"        
    return eval(execstring)


def getIndex(inList,inValue):
    """
        Function Description: 
        Get the index of the nearest value specified by 'inValue' in a given list 'inList'. 
        Used to determine the indices of the xMin, xMax, yMin, yMax values describing the 'extent'.

        Parameters
        ----------
        inList: list
            List of values (e.g. coordinates in x/y-dimension)
        inValue: float
            Desired Value

        Returns
        -------
        int
            Index of the value which is nearest to 'inValue'
    """
    #Get index of the nearest value with the list
    inList = copy.deepcopy(inList)
    inListReverse = False
    vIndex = -1
    if inList[0] > inList[len(inList)-1]:
        inListReverse = True
        inList.reverse()
        
    vDiff = abs(inList[len(inList)-1] - inList[0])
    i = 0
    for v in inList:
        vCurrDiff = abs(inValue - v)
        if vCurrDiff < vDiff:
            vDiff = vCurrDiff
            vIndex = i
        i = i + 1
    if inListReverse:
        vIndex = len(inList) - 1  - vIndex
    return vIndex
    
    



def ClipNetCDFMultiVar(inNetCDFFileName, ncVarName, xDimension, yDimension, xyExtent, current_geodatabase, Timestamp):

    """
        Function Description: 
        Clips the input NetCDF file to the given extent (longitude/latitude). Only the Variables
        specified in "ncVarName" are included in the output netCDF file.

        Parameters
        ----------
        inNetCDFFileName: string
            Name of the netCDF File to clip
        ncVarName: list
            Names of Variables to be included in the output file
        xDimension: string
            NetCDF Dimension for x-Coordinate (longitude)
        yDimension: string
            NetCDF Dimension for y-Coordinate (latitude)
        xyExtent: array
            x/y coordinates of the desired boundaries to clip the input file
        current_geodatabase: string
            Path to the current project geodatabase (to save the output file)
        

        Returns
        -------
        unique_name: string
            Name of the output NetCDF file 
        
    """
    arcpy.AddMessage('\nSTART Clipping NetCDF File')


    unique_name = arcpy.CreateUniqueName(Timestamp +"_Clipped_netCDF.nc", workspace= current_geodatabase)
    outNetCDFFileName = unique_name

    #Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"

    # Split the Input varNames variables
    ncVarName = ncVarName.split(",")

    #Get XMin, YMin, XMax, and YMax from extennt
    xyExtentVal = xyExtent.split()
    xMin = float(xyExtentVal[0])
    yMin = float(xyExtentVal[1])
    xMax = float(xyExtentVal[2])
    yMax = float(xyExtentVal[3])

    # 1. Load NetCDF File
    #1.0 Open the netCDF file and get variables
    inNetCDFFile = NetCDFFile(inNetCDFFileName, 'r')
    ncVarNames = inNetCDFFile.variables.keys()

    # Combine the Dimensions from all Input Variables
    dimNames = list()
    for varName in ncVarName:
        ncVar = inNetCDFFile.variables[varName]
        varDimName = list(ncVar.dimensions)
        for DimName in varDimName:
            if DimName not in dimNames:
                dimNames.append(DimName)
               
    
    #1.1 Check if netCDF variable exists
    for varName in ncVarName:
        if list(ncVarNames).count(varName) == 0:
            arcpy.AddError("NetCDF variable " + varName + " does not exist.")              
            raise Exception (msgInvalidParameter)
        arcpy.AddMessage("... netCDF variable " + varName + " exists")

    # 2.0 Create outNetCDFFile
    outNetCDFFile = NetCDFFile(outNetCDFFileName, 'w')
    arcpy.AddMessage("... creating output netCDF file " + outNetCDFFileName)  

    #3.0 Find xmin, ymin, xmax, and ymax index 
    #3.1. Find xmin and xmax index
    ncCoordVar = inNetCDFFile.variables[xDimension]        
    ncCoordVarData = ncCoordVar[:]
    ncCoordVarDataList = list(ncCoordVarData)        
    xMinIndex = getIndex(ncCoordVarDataList, xMin)                
    xMaxIndex = getIndex(ncCoordVarDataList, xMax)        
    if xMinIndex > xMaxIndex:
        TempMinIndex = xMinIndex
        xMinIndex = xMaxIndex
        xMaxIndex = TempMinIndex
        
    #3.2. Find ymin and ymax index        
    ncCoordVar = inNetCDFFile.variables[yDimension]        
    ncCoordVarData = ncCoordVar[:]
    ncCoordVarDataList = list(ncCoordVarData)        
    yMinIndex = getIndex(ncCoordVarDataList, yMin)                
    yMaxIndex = getIndex(ncCoordVarDataList, yMax)        
    if yMinIndex > yMaxIndex:
        TempMinIndex = yMinIndex
        yMinIndex = yMaxIndex
        yMaxIndex = TempMinIndex
                    

    #4.0 Adjust x and y dimension sizes based on the given extent
    xDimensionSize = xMaxIndex - xMinIndex + 1
    yDimensionSize = yMaxIndex - yMinIndex + 1


    #5.0 Create dimension and coordinate variables in outNetCDFFile
    for dimName in dimNames:       
        #Set output dimension size    
        if dimName == xDimension:
            dimSize = xDimensionSize
        elif dimName == yDimension:
            dimSize = yDimensionSize
        else:
            dimSize = inNetCDFFile.dimensions[dimName].size
            
        #Adjust output dimension size if it is NONE (NONE is returned for UNLIITED size)
        #Getting actual size in file from shape
        if dimSize == None:
            ncCoordVar = inNetCDFFile.variables[dimName]
            dimSize = list(ncCoordVar.shape)[0]

        #5.1 Create dimension in outnetCDFfile
        outNetCDFFile.createDimension(dimName,dimSize) 
        
        #5.2 Check if dimension is alos a variable i.e. coordinate variable
        if dimName in ncVarNames:
            # Get coordinate variable    
            ncCoordVar = inNetCDFFile.variables[dimName]
                
            # Get data: a subset if x or y dimension else get all
            if dimName == xDimension:                
                ncCoordVarData = ncCoordVar[xMinIndex:xMaxIndex+1]            
            elif dimName == yDimension:                
                ncCoordVarData = ncCoordVar[yMinIndex:yMaxIndex+1]                
            else:
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
    arcpy.AddMessage("... writing dimensions and coordinate variables")


    #6.0 Get the netCDF variable objects
    for varName in ncVarName:
        ncVar = inNetCDFFile.variables[varName]
        ncVarData = ncVar[:]    
        ncVarShape = ncVar.shape
        ncVarRank = len(ncVarData.shape)
        ncVarDimNames = ncVar.dimensions 
        
        #6.1 Check if X, Y dimensions exist
        if list(ncVarDimNames).count(xDimension) == 0:
            arcpy.AddError("Dimension " + xDimension + " does not exist in variable " + varName + ".")               
            raise Exception (msgInvalidParameter)
        if list(ncVarDimNames).count(yDimension) == 0:
            arcpy.AddError("Dimension " + yDimension + " does not exist in variable " + varName + ".")               
            raise Exception (msgInvalidParameter)
        else:
            arcpy.AddMessage("... " + xDimension + " and " +  yDimension + " dimensions exists in variable " + varName)

        #6.2 Get dimension names of the specified variable and find out X Y dimension indices
        xDimensionIndex = list(ncVarDimNames).index(xDimension)
        yDimensionIndex = list(ncVarDimNames).index(yDimension)
        
        #6.3 Create variable in outnetCDFfile 
        outNcVar = outNetCDFFile.createVariable(varName, 'f4', ncVarDimNames, fill_value = -3.4028235e+38)    
        outNcVar[:] = getSlice(ncVarData, xMinIndex, yMinIndex, xMaxIndex, yMaxIndex,xDimensionIndex, yDimensionIndex, ncVarRank)
        arcpy.AddMessage("... writing variable " + varName)

        #6.4 Get variable attributes, write all except 'coordinates'
        #    Also determine if grid_mapping exists or not
        bGridMappingExists = False
        ncGridMappingVarName = ""
        allAttributes = dir(ncVar)

        for attrib in allAttributes:
            if attrib not in ['assignValue', 'getValue', 'typecode', 'coordinates', '_FillValue', '__array__', '__class__', '__delattr__', '__delitem__', '__dir__', '__doc__', 
                    '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__len__', 
                    '__lt__', '__ne__', '__new__', '__orthogonal_indexing__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 
                    '__unicode__', '_assign_vlen', '_check_safecast', '_cmptype', '_enumtype', '_get', '_getdims', '_getname', '_grp', '_grpid', '_has_lsd', '_iscompound', '_isenum', 
                    '_isprimitive', '_isvlen', '_name', '_ncstring_attrs__', '_nunlimdim', '_pack', '_put', '_toma', '_use_get_vars', '_varid', '_vltype', 'always_mask', 
                    'chartostring', 'chunking', 'datatype', 'delncattr', 'dimensions', 'dtype', 'endian', 'filters', 'getValue', 'get_dims', 'get_var_chunk_cache', 'getncattr', 
                    'group', 'mask', 'name', 'ncattrs', 'ndim', 'renameAttribute', 'scale', 'set_always_mask', 'set_auto_chartostring', 'set_auto_mask', 'set_auto_maskandscale', 'set_auto_scale', 
                    'set_collective', 'set_ncstring_attrs', 'set_var_chunk_cache', 'setncattr', 'setncattr_string', 'setncatts','shape', 'size', 'use_nc_get_vars']:
                attribValue = netCDF4.Variable.getncattr(ncVar, attrib)
                netCDF4.Variable.setncattr(outNcVar, attrib, attribValue)
                if attrib == "grid_mapping":
                    bGridMappingExists = True
                    ncGridMappingVarName = attribValue

        arcpy.AddMessage("... writing variable attributes for " + varName)
        
        
        #6.5 Get grid_mapping variable object if exists
        if bGridMappingExists:
            ncGridMappingVar = inNetCDFFile.variables[ncGridMappingVarName]        
            ncGridMappingVarShape = ncGridMappingVar.shape        
            ncGridMappingVarDimNames = ncGridMappingVar.dimensions      
            
            #6.5.1 Create grid mapping variable in outnetCDFfile 
            outNcGridMappingVar = outNetCDFFile.createVariable(ncGridMappingVarName, ncGridMappingVar.dtype, ncGridMappingVarDimNames)   
            allGridMappingAttributes = dir(ncGridMappingVar)
            for gridmappingattrib in allGridMappingAttributes:
                if gridmappingattrib not in ['assignValue', 'getValue', 'typecode']:
                    gridmappingAttribValue = getattr(ncGridMappingVar, gridmappingattrib)
                    setattr(outNcGridMappingVar, gridmappingattrib, gridmappingAttribValue)
            arcpy.AddMessage("... writing grid_mapping for " + varName)

    #7.0 Write all global attributes
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
    
    #8.0 Syncronize and close netCDF files
    outNetCDFFile.sync()    
    outNetCDFFile.close()
    inNetCDFFile.close()
    
    arcpy.AddMessage('END Clipping NetCDF File\n\n')

    return unique_name
       