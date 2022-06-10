'''----------------------------------------------------------------------------------
 ArcGIS Tool Name:  Horizontal Wind Classification
 Source Name:       HorizontalWindClassification.py
 Version:           ArcGIS Pro 2.8.0
 Author:            Tschannen Tim and Zurbrügg Niculin, ZHAW School of Engineering

 Arguments:         NetCDF file
                    NetCDF CLC variable name
                    Output netCDF File

 Description:       Workflow to classify the horizontal wind speed and wind direction at each
                    grid point. For the wind direction the following eight directions are used:
                    N, NE, E, SE, S, SW, W, NW.
                    
  
----------------------------------------------------------------------------------'''


#Import required modules
import arcpy
import numpy as np
import sys, os, copy
from netCDF4 import Dataset
from netCDF4 import Variable
import netCDF4



def HorizontalWind_classification(Wind_U_Data, Wind_V_Data):
    """
        Function Description:   Function to classify the horizontal wind speed and wind direction at each
                                grid point. For the wind direction the following eight directions are used:
                                N, NE, E, SE, S, SW, W, NW.

        Parameters
        ----------
        Wind_U_Data: array
            Array of the northward wind component
        Wind_V_Data: array
            Array of the eastward wind component
        
        Returns
        -------
        WindDirectionData: array
            Wind direction at each grid point
        WindSpeedData: array
            Wind speed at each grid point
        WindItem: array
            Value to determine which wind barb is used in the web app
    """
    fill_value = -3.4028235e+38
    
    Wind_U_Data = np.array(Wind_U_Data)
    shapeWind_U_Data = np.shape(Wind_U_Data)
    shapeWind_U_Data = tuple(shapeWind_U_Data) 

    Wind_V_Data = np.array(Wind_V_Data)
    shapeWind_V_Data = np.shape(Wind_V_Data)
    shapeWind_V_Data = tuple(shapeWind_V_Data) 

    WindDirectionData = np.empty(shapeWind_U_Data)  # Create empty output array for Wind Direction values
    WindSpeedData = np.empty(shapeWind_U_Data)      # Create empty output array for Wind Speed Values
    WindItem = np.empty(shapeWind_U_Data)           # Create empty output array for Wind Item Values

    arcpy.AddMessage('... Calculating Wind Direction and Windspeed')
    # Classify CLC Values to Categories 
    for time in range(shapeWind_U_Data[0]):
        for zcoord in range(shapeWind_U_Data[1]):
            arcpy.AddMessage('    Z-Coordinate: ' + str(zcoord))
            for i in range(shapeWind_U_Data[2]):        # latitude
                for j in range(shapeWind_U_Data[3]):    # longitude
                    if (i % 5 == 0) & (j % 5 == 0):
                        # Calculating Horizontal Wind Speed
                        if (Wind_U_Data[time, zcoord, i, j]  > -1000) & (Wind_V_Data[time, zcoord, i, j]  > -1000):
                            WindSpeedData[time, zcoord, i, j] = np.sqrt(Wind_U_Data[time, zcoord, i, j]**2 + Wind_V_Data[time, zcoord, i, j]**2)*1.943844 # To calculate the values from m/s to knots
                        else:
                            WindSpeedData[time, zcoord, i, j] = fill_value

                        # Calculating Wind Direction
                        if WindSpeedData[time, zcoord, i, j] > 0:
                            if np.arctan2(Wind_U_Data[time, zcoord, i, j], Wind_V_Data[time, zcoord, i, j]) < 0:
                                WindDirection = 360 - abs(np.rad2deg(np.arctan2(Wind_U_Data[time, zcoord, i, j], Wind_V_Data[time, zcoord, i, j])))
                            else:
                                WindDirection = np.rad2deg(np.arctan2(Wind_U_Data[time, zcoord, i, j], Wind_V_Data[time, zcoord, i, j]))

                        # Classification of Wind Direction into classical compass winds (N, NE, E, SE, S, SW, W, NW)¨
                            if ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 0
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 1

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 2
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 3
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 4
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 5
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 6
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 7.5):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 7

                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 8
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 9

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 10
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 11
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 12
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 13
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 14
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 15):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 15
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 16
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 17

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 18
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 19
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 20
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 21
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 22
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 25):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 23
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 24
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 25

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 26
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 27
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 28
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 29
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 30
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 35):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 31
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 32
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 33

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 34
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 35
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 36
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 37
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 38
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 45):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 39
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 40
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 41

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 42
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 43
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 44
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 45
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 46
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 55):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 47
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 48
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 49

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 50
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 51
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 52
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 53
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 54
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 65):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 55
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 56
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 57

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 58
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 59
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 60
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 61
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 62
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 75):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 63
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 85):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 64
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j]< 85):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 65

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 85):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 66
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 85):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 67
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 85):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 68
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 85):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 69
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 85):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 70
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 85):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 71
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 72
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 73

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 74
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 75
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 76
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 77
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 78
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] < 95):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 79
                            
                            elif ((WindDirection >= 337.5) or (WindDirection < 22.5)) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 0
                                WindItem[time, zcoord, i, j] = 80
                            
                            elif ((WindDirection >= 22.5) & (WindDirection < 67.5)) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 1
                                WindItem[time, zcoord, i, j] = 81

                            elif ((WindDirection >= 67.5) & (WindDirection < 112.5)) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 2
                                WindItem[time, zcoord, i, j] = 82
                            
                            elif ((WindDirection >= 112.5) & (WindDirection < 157.5)) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 3
                                WindItem[time, zcoord, i, j] = 83
                            
                            elif ((WindDirection >= 157.5) & (WindDirection < 202.5)) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 4
                                WindItem[time, zcoord, i, j] = 84
                            
                            elif (WindDirection >= 202.5) & (WindDirection < 247.5) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 5
                                WindItem[time, zcoord, i, j] = 85
                            
                            elif ((WindDirection >= 247.5) & (WindDirection < 292.5)) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 6
                                WindItem[time, zcoord, i, j] = 86
                            
                            elif ((WindDirection >= 292.5) & (WindDirection < 337.5)) & (WindSpeedData[time, zcoord, i, j] >= 95):
                                WindDirectionData[time, zcoord, i, j] = 7
                                WindItem[time, zcoord, i, j] = 87
                            
                            

                        else:
                            WindDirectionData[time, zcoord, i, j] = fill_value   # If no Wind Speed the fill_value (NaN) is inserted, thus no feature will be created in the feature layer
                            WindItem[time, zcoord, i, j] = fill_value
                    else:
                        WindDirectionData[time, zcoord, i, j] = fill_value
                        WindItem[time, zcoord, i, j] = fill_value
                        WindSpeedData[time, zcoord, i, j] = fill_value
    return [WindDirectionData, WindSpeedData, WindItem]

                




def HorizontalWindClassification(inNetCDFFileName, current_geodatabase, LayerName, Timestamp):
    """
        Function Description:   Function to classify the horizontal wind speed and wind direction at each
                                grid point and write to a output NetCDF file. For the wind direction the 
                                following eight directions are used:
                                N, NE, E, SE, S, SW, W, NW.
        
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
        outNetCDFVariables: list
            Names of output variables wind direction, wind speed and wind item
    """
    arcpy.AddMessage('\nSTART Calculating Wind Direction and Wind Speed Classification')

    #Define message constants so they may be translated easily
    msgInvalidParameter = "Invalid parameter."
    msgInvalidParameters = "Invalid number of parameters."
    ErrorDesc = "error while running"
    
    unique_name = arcpy.CreateUniqueName(Timestamp + "_" + LayerName + "_Classified_netCDF.nc", workspace=current_geodatabase)
    outNetCDFFileName = unique_name      
    ncVarU = 'U'
    ncVarV = 'V'
    outVarWindDirection = 'WindDirection'
    outVarWindSpeed = 'Windspeed'
    outVarWindItem ='WindItem'

    fill_value = -3.4028235e+38

    # 1. Import NetCDF Input File with CLC Values
    #1.1 Open the netCDF file and get variables
    inNetCDFFile = Dataset(inNetCDFFileName, 'r')
    ncVarNames = inNetCDFFile.variables.keys()
    ncDimNames = inNetCDFFile.dimensions.keys()
    
    ncDimNames = list(ncDimNames) 

    #1.2 Check if netCDF variable exists
    for var in [ncVarU, ncVarV]:
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



    # 2. Extract Horizontal Wind Speed Values from netCDF Input File
    # 2.1 Get netCDF Wind components variable objects (U,V)
    ncVarUObj = inNetCDFFile.variables[ncVarU]
    ncVarUData = inNetCDFFile.variables[ncVarU][:]
    ncVarVObj = inNetCDFFile.variables[ncVarV]
    ncVarVData = inNetCDFFile.variables[ncVarV][:]

    

    # 3. Classification of CLC Values 
    [WindDirectionData, WindSpeedData, WindItem] = HorizontalWind_classification(ncVarUData, ncVarVData)

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


    # 6. Create Variables for WindDirection and Windspeed 
    outNcVarDim = list(inNetCDFFile.variables[ncVarU].dimensions)
    outNcVarWindDirection = outNetCDFFile.createVariable(outVarWindDirection, 'f4', (outNcVarDim), fill_value = -3.4028235e+38)
    outNcVarWindDirection[:, :, :, :] = WindDirectionData[:]          

    # 7. Create Variables for WindDirection and Windspeed 
    outNcVarWindSpeed = outNetCDFFile.createVariable(outVarWindSpeed, 'f4', (outNcVarDim), fill_value = -3.4028235e+38)
    outNcVarWindSpeed[:, :, :, :] = WindSpeedData[:]

    # 8. Create Variables for WindItem
    outNcVarWindItem = outNetCDFFile.createVariable(outVarWindItem, 'f4', (outNcVarDim), fill_value = -3.4028235e+38)  
    outNcVarWindItem[:, :, :, :] = WindItem[:]       

    # 9. Create Variable for LayerLevel
    ncVarLayerLevelData = inNetCDFFile.variables["LayerLevel"][:]
    for z in range(np.shape(ncVarLayerLevelData)[1]):
        for i in range(np.shape(ncVarLayerLevelData)[2]):
            for j in range(np.shape(ncVarLayerLevelData)[3]):
                if not ((i % 5 == 0) & (j % 5 ==0)):
                    ncVarLayerLevelData[0, z, i, j] = fill_value

    outNcVarLayerLevelDim = list(inNetCDFFile.variables["LayerLevel"].dimensions)
    outNcVarLayerLevel = outNetCDFFile.createVariable("LayerLevel", 'f4', (outNcVarLayerLevelDim), fill_value = -3.4028235e+38)
    outNcVarLayerLevel[:, :, :, :] = ncVarLayerLevelData[:]

    # 10. Write all global attributes
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


    # 11. Synchronize and close NetCDF files
    outNetCDFFile.sync()    
    outNetCDFFile.close()
    inNetCDFFile.close()

    arcpy.AddMessage('END Calculating Wind Direction and Wind Speed\n\n')


    return [unique_name, [outVarWindSpeed, outVarWindDirection, outVarWindItem]]






