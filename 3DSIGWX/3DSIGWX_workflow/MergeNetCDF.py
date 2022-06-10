'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  MergeNetCDF
 Source Name:       MergeNetCDF.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Edited by Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    

 Description:       Merge multiple netCDF files along Time Dimension. Used to create a 
                    timeserie in ArcGIS
 
----------------------------------------------------------------------------------'''



#Import required modules
import arcpy
import numpy as np
import sys, os,re, copy
from netCDF4 import Dataset
from netCDF4 import Variable
import netCDF4

def MergeNetCDFFunction(file_names, current_geodatabase, outFileName, Timestamp):
    """
        Function Description:   Function to Merge multiple NetCDF files along the
                                time Dimension.
         
        Parameters
        ----------
        file_names: array
            Array containing paths to NetCDF files
        current_geodatabase: string
            Path to work GDB
        outFileName: string
            Name of output file
        Timestamp: string
            Timestamp of the current NetCDF file 
        
        Returns
        -------
        outNetCDFFileName: string
            Path to merged output NetCDF file
        NetCDFDimensions: list
            Names of NetCDF dimensions (lat, lon, Z, time)
            Used to create NetCDF feature layer
    """

    arcpy.AddMessage('\nSTART Merging netCDF File')

    #Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"


    # 1. Open NetCDF Files and read as Multi-File netCDF Dataset (with shared dimension "time")
    # 1.1 Open as Multi-File Dataset
    arcpy.AddMessage(file_names)
    merged_file = netCDF4.MFDataset(file_names, aggdim = "time")
    master_file = netCDF4.Dataset(file_names[0]) # First file as Master-File to retrieve Global Attributes

    # 1.2 Get Variable and Dimension Names
    dimNames = list(merged_file.dimensions.keys())
    ncVarNames = list(merged_file.variables.keys())

    # 1.3 Check if X,Y,Z Dimension exist
    xDimension = 'longitude'
    yDimension = 'latitude'
    zDimension = 'Z'
    timeDimension = 'time'
    for Dimension in list((xDimension, yDimension, zDimension)):
            if list(dimNames).count(Dimension) == 0:
                arcpy.AddError("NetCDF Dimension " + Dimension + " does not exist.")              
                raise Exception (msgInvalidParameter)
            arcpy.AddMessage("... netCDF Dimension " + Dimension + " exists")


    # 2. Create new Output NetCDF file
    outNcFileName = Timestamp + "_" + outFileName + "_merged.nc"
    outNetCDFFileName = os.path.join(current_geodatabase, outNcFileName)
    outNetCDFFileName = outNetCDFFileName.replace(os.sep,'/')
    outNetCDFFile = Dataset(outNetCDFFileName, 'w', format='NETCDF4')


    # 3. Create dimension and coordinate variables in outNetCDFFile
    for dimName in dimNames:       
        #Set output dimension size    
        if dimName == xDimension:
            dimSize = len(merged_file.variables[dimName])
        elif dimName == yDimension:
            dimSize = len(merged_file.variables[dimName])
        elif dimName == zDimension:
                dimSize = len(merged_file.variables[dimName]) 
        else:
            dimSize = len(merged_file.dimensions[dimName])
            
        #Adjust output dimension size if it is NONE (NONE is returned for UNLIITED size)
        #Getting actual size in file from shape
        if dimSize == None:
            ncCoordVar = merged_file.variables[dimName]
            dimSize = list(ncCoordVar.shape)[0]

        #3.1 Create dimension in outnetCDFfile
        outNetCDFFile.createDimension(dimName,dimSize) 
        
        #3.2 Check if dimension is also a variable i.e. coordinate variable
        if dimName in ncVarNames:
            # Get coordinate variable    
            ncCoordVar = merged_file.variables[dimName]
                
            # Get all data
            ncCoordVarData = ncCoordVar[:] 
                
            #3.2.1 Create coordinate variable in outnetCDFfile           
            outNcCoordVar = outNetCDFFile.createVariable(dimName, 'f4', (dimName,), fill_value = -3.4028235e+38)
            
            if dimName == 'time':
                outNcCoordVar[:] = np.arange(0, len(ncCoordVarData), 1)
            else:
                outNcCoordVar[:] = ncCoordVarData
            
            #3.2.2 Write Coordinate Variable Attributes
            # First check if Coord. Variable is instance of class "netCDF4._netCDF4.Variable"
            if isinstance(ncCoordVar, (netCDF4._netCDF4.Variable)):         
                CoordVarAttributes = netCDF4.Variable.ncattrs(ncCoordVar)
        
                for CoordVarAttrib in CoordVarAttributes:
                    if CoordVarAttrib == '_FillValue':
                        pass
                    else:
                        CoordAttribValue = netCDF4.Variable.getncattr(ncCoordVar, CoordVarAttrib)
                        netCDF4.Variable.setncattr(outNcCoordVar, CoordVarAttrib, CoordAttribValue)
            # Some Variables in merged_file are instances of class "netCDF4._netCDF4._Variable". For those the "ncattrs" and "getncattr" methods are not available.
            # Thus a workaraound to assign the attributes is used by taking the attributes from the master_file
            else:   
                CoordVarAttributes = netCDF4.Variable.ncattrs(master_file.variables[dimName])
                for CoordVarAttrib in CoordVarAttributes:
                    if CoordVarAttrib == '_FillValue':
                        pass
                    else:
                        CoordAttribValue = netCDF4.Variable.getncattr(master_file.variables[dimName], CoordVarAttrib)
                        netCDF4.Variable.setncattr(outNcCoordVar, CoordVarAttrib, CoordAttribValue)
    arcpy.AddMessage("... writing dimensions and coordinate variables")



    # 4. Get the netCDF variable objects and write variables in new output netCDF file
    for varName in ncVarNames:
        if varName not in dimNames:                 # Coordinate Variables already written, thus only write variables which have no dimension of the same name
            ncVar = merged_file.variables[varName]
            ncVarData = ncVar[:]    
            ncVarShape = ncVar.shape
            ncVarRank = len(ncVarData.shape)
            ncVarDimNames = ncVar.dimensions 
            
            # 4.1 Check if X, Y dimensions exist
            if list(ncVarDimNames).count(xDimension) == 0:
                arcpy.AddError("Dimension " + xDimension + " does not exist in variable " + varName + ".")               
                #raise Exception (msgInvalidParameter)
            if list(ncVarDimNames).count(yDimension) == 0:
                arcpy.AddError("Dimension " + yDimension + " does not exist in variable " + varName + ".")               
                #raise Exception (msgInvalidParameter)
            else:
                arcpy.AddMessage("... " + xDimension + " and " +  yDimension + " dimensions exists in variable " + varName)

            
            # 4.2 Create variable in outnetCDFfile 
            outNcVar = outNetCDFFile.createVariable(varName, 'f4', ncVarDimNames, fill_value = -3.4028235e+38)    
            outNcVar[:] = ncVarData[:]
            arcpy.AddMessage("... writing variable " + varName)        

            
            # 4.3 Get variable attributes and write to new output file
            #    Also determine if grid_mapping exists or not
            bGridMappingExists = False
            ncGridMappingVarName = ""
            
            if isinstance(ncVar, (netCDF4._netCDF4.Variable)):
                allAttributes = netCDF4.Variable.ncattrs(ncVar)        
                for attrib in allAttributes:
                    if attrib == '_FillValue':
                        pass
                    else:
                        attribValue = netCDF4.Variable.getncattr(ncVar, attrib)
                        netCDF4.Variable.setncattr(outNcVar, attrib, attribValue)
                        if attrib == "grid_mapping":
                            bGridMappingExists = True
                            ncGridMappingVarName = attribValue
                arcpy.AddMessage("... writing variable attributes for " + varName)

            # Some Variables in merged_file are instances of class "netCDF4._netCDF4._Variable". For those the "ncattrs" and "getncattr" methods are not available.
            # Thus a workaraound to assign the attributes is used by taking the attributes from the master_file
            else:   
                allAttributes = netCDF4.Variable.ncattrs(master_file.variables[varName])
        
                for attrib in allAttributes:
                    if attrib == '_FillValue':
                        pass
                    else:
                        attribValue = netCDF4.Variable.getncattr(master_file.variables[varName], attrib)
                        netCDF4.Variable.setncattr(outNcVar, attrib, attribValue)
                        if attrib == "grid_mapping":
                            bGridMappingExists = True
                            ncGridMappingVarName = attribValue
                arcpy.AddMessage("... writing variable attributes for " + varName)

            # 4.4 Get grid_mapping variable object if exists
            if bGridMappingExists:
                ncGridMappingVar = merged_file.variables[ncGridMappingVarName]        
                ncGridMappingVarShape = ncGridMappingVar.shape        
                ncGridMappingVarDimNames = ncGridMappingVar.dimensions 
            
                #4.4.1 Create grid mapping variable in outnetCDFfile 
                outNcGridMappingVar = outNetCDFFile.createVariable(ncGridMappingVarName, ncGridMappingVar.dtype, ncGridMappingVarDimNames)   
                # Write Attributes
                allGridMappingAttributes = netCDF4.Variable.ncattrs(ncGridMappingVar)
                for gridmappingattrib in allGridMappingAttributes:
                    if gridmappingattrib not in ['assignValue', 'getValue', 'typecode']:
                        gridmappingAttribValue = netCDF4.Variable.getncattr(ncGridMappingVar, gridmappingattrib)
                        netCDF4.Variable.setncattr(outNcGridMappingVar, gridmappingattrib, gridmappingAttribValue)
                arcpy.AddMessage("... writing grid_mapping for " + varName)


    #5.0 Write all global attributes to OutNetCDF File
    # Global Attributes are taken from master_file
    globalAllAttributes = netCDF4.MFDataset.ncattrs(merged_file)
    for globalAttribute in globalAllAttributes:
        globalAttributeValue = netCDF4.Dataset.getncattr(master_file, globalAttribute)
        netCDF4.Dataset.setncattr(outNetCDFFile, globalAttribute, globalAttributeValue)
    arcpy.AddMessage("... writing global attributes")

    #6.0 Syncronize and close netCDF files
    outNetCDFFile.sync()    
    outNetCDFFile.close()
    merged_file.close()

    arcpy.AddMessage('END Merging netCDF File\n\n')

    return [outNetCDFFileName, [timeDimension, zDimension, yDimension, xDimension]]






                