'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  Icing Classification
 Source Name:       IcingClassification.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    NetCDF variable names T, QC
                    Output netCDF File

 Description:       Workflow to classify the icing at each grid point based on a temperature
                    below 0°C and the liquid water content.
                    
  
----------------------------------------------------------------------------------'''


#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset
from netCDF4 import Variable
import netCDF4



def Icing_classification(T_Data, QC_Data):
    """
        Function Description:   Function to classify the icing at each grid point based on a temperature
                                below 0°C and the liquid water content.

        Parameters
        ----------
        T_Data: array
            Array of T Values
        QC_Data: array
            Array of QC Values
        
        Returns
        -------
        outVariableData: array
            Icing areas
    """
    fill_value = -3.4028235e+38
    
    T_Data = np.array(T_Data)
    shape_T_Data = np.shape(T_Data)
    shape_T_Data = tuple(shape_T_Data) 

    QC_Data = np.array(QC_Data)
    shape_QC_Data = np.shape(QC_Data)
    shape_QC_Data = tuple(shape_QC_Data) 

    IcingData = np.empty(shape_T_Data)    # Create empty output array for Icing values
    
    arcpy.AddMessage('... Calculating Icing Warning')
    # Classify CLC Values to Categories 
    for time in range(shape_T_Data[0]):
        for zcoord in range(shape_T_Data[1]):
            arcpy.AddMessage('    Z-Coordinate: ' + str(zcoord))
            for i in range(shape_T_Data[2]):        # latitude
                for j in range(shape_T_Data[3]):    # longitude 
                    # Analysing if Icing is possible
                    if (273.15 >= T_Data[time, zcoord, i, j]  >= 233.15) & (QC_Data[time, zcoord, i, j]  > 0):
                        IcingData[time, zcoord, i, j] = 1
                    else:
                        IcingData[time, zcoord, i, j] = fill_value
    
    return [IcingData]

                




def IcingClassification(inNetCDFFileName, current_geodatabase, LayerName, Timestamp):
    """
        Function Description:   Function to classify the icing at each grid point based on a temperature
                                below 0°C and the liquid water content and write a output NetCDF file.
        

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
        outVarIcing: string
            Variable Name for Icing
    """
    arcpy.AddMessage('\nSTART Calculating Icing')

    #Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"
    
    
    #inNetCDFFileName = "HeightAssigned_netCDF.nc"
    unique_name = arcpy.CreateUniqueName(Timestamp + "_" + LayerName + "_Classified_netCDF.nc", workspace=current_geodatabase)
    outNetCDFFileName = unique_name      
    #outNetCDFFileName = "Icing_netCDF.nc"
    ncVarT = 'T'
    ncVarQC = 'QC'
    outVarIcing = 'Icing'
    

    fill_value = -3.4028235e+38

    # 1. Import NetCDF Input File with all Values
    #1.1 Open the netCDF file and get variables
    inNetCDFFile = Dataset(inNetCDFFileName, 'r')
    ncVarNames = inNetCDFFile.variables.keys()
    ncDimNames = inNetCDFFile.dimensions.keys()
    ncDimNames = list(ncDimNames) 

    
    #1.2 Check if netCDF variable exists
    for var in [ncVarT, ncVarQC]:
        if list(ncVarNames).count(var) == 0:
            arcpy.AddError("NetCDF variable " + var + " does not exist.")              
            raise Exception (msgInvalidParameter)
        arcpy.AddMessage("... netCDF variable " + var + " exists")


    #1.3 Check if X, Y, Z dimensions exist
    xDimension = 'longitude'
    yDimension = 'latitude'
    zDimension = 'Z'
    for Dimension in list((xDimension, yDimension, zDimension)):
        if list(ncDimNames).count(Dimension) == 0:
            arcpy.AddError("NetCDF Dimension " + Dimension + " does not exist.")              
            raise Exception (msgInvalidParameter)
        arcpy.AddMessage("... netCDF Dimension " + Dimension + " exists")



    # 2. Extract Icing Values from netCDF Input File
    # 2.1 Get netCDF Icing components variable objects (T, QC)
    ncVarTObj = inNetCDFFile.variables[ncVarT]
    ncVarTData = inNetCDFFile.variables[ncVarT][:]
    ncVarQCObj = inNetCDFFile.variables[ncVarQC]
    ncVarQCData = inNetCDFFile.variables[ncVarQC][:]

    

    # 3. Classification of Icing Values 
    [IcingData] = Icing_classification(ncVarTData, ncVarQCData)

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

    # 6. Create Variables for Icing
    outNcVarDim = list(inNetCDFFile.variables[ncVarT].dimensions)
    outNcVarIcing = outNetCDFFile.createVariable(outVarIcing, 'f4', (outNcVarDim), fill_value = -3.4028235e+38)
    outNcVarIcing[:, :, :, :] = IcingData[:]          
         


    # 7. Write all global attributes
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


    # 8. Synchronize and close NetCDF files
    outNetCDFFile.sync()    
    outNetCDFFile.close()
    inNetCDFFile.close()

    arcpy.AddMessage('END Calculating Icing Warning\n\n')


    return [unique_name, outVarIcing]






