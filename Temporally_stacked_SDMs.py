# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 15:07:37 2022

@author: 21746316
"""


import os
import pandas as pd
import rasterio
import numpy as np
from osgeo import gdal
from osgeo import osr
import subprocess


data_file = "Beeflora_list.csv" 
data_path = os.path.join(os.getcwd(), data_file)
df = pd.read_csv(data_path)

df = df[['SpeciesNameID','1','2','3','4','5','6','7','8','9','10','11','12']]
df = df.melt(id_vars = ['SpeciesNameID'])
df['species_month'] = df['SpeciesNameID'].astype(str) + "_" + df['variable'].astype(str)
flowering_dict = dict(zip(df['species_month'], df['value']))
# making 12 rasters where pixel values represent the flowering count of species
months = [i for i in range(1, 12 + 1)]

df2 = pd.read_csv(data_path)
threshold_dict = dict(zip(df2['SpeciesNameID'], df2['ThresholdLog']))


'''
for each month:
    convert format
    load all rasters and reclassify
    stack
    sum
    export

'''

# ### stake SDMs based on flowering month = 12 rasters with number of species flowering per month

species_loc =  os.path.join(os.getcwd(), "MaxEnt_outputs")
species = [i for i in os.listdir(species_loc) if i.endswith('_utm3000.tif')]

for month in months:
    print(month)
    l = [] # list to stack rasters
    for s in species:
        print(s)
        # get the flowering information for that species and month
        species_temp = s.split('_utm3000.tif')[0]
        threshold = threshold_dict[int(species_temp)]
        if int(species_temp) in list(df.SpeciesNameID.unique()):
            species_month = str(species_temp) + "_" + str(month)
            is_flowering = flowering_dict[species_month]
            
            raster = os.path.join(species_loc, s)
            #print(raster)
            print(os.path.exists(raster)) 
            
            # select all the cells with probability > 0.5 
            
            with rasterio.open(raster, 'r') as ds:
                meta = ds.meta
                array = ds.read()
                array = array[0,:,:]
                array[array < threshold] = 0
                array[array >= threshold] = is_flowering
                l.append(array)
    
        stacked = np.stack(l)
        stacked = stacked.sum(axis = 0)
        stacked = stacked.reshape(1, stacked.shape[0], stacked.shape[1])
        
        out_loc = os.path.join(os.getcwd(), "Monthly_flowering")
        new_file = os.path.join(out_loc, str(month) + ".tif")
        
        with rasterio.open(new_file, "w", **meta) as dest:
            dest.write(stacked)
            
         
        
        
        





