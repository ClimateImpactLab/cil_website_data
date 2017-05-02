import xarray as xr
import numpy as np
import pandas as pd
from glob import glob
import re


#Get climate data outputs from sacagawea for all models including the 
#pattern models

#load all the models into xarray and concat along model dim

#Take 20 year averages 

#run this through our weighting scheme associated with the gcp
#generate csvs will column headers as 2020, 2040, 2060, 2080

def merge_datasets(filepaths, dim='model'):
    '''
    Given a string representation fo file paths, concatenates
    the datasets for a given variable along a specified dimension 

    Parameters
    ----------

    filepaths: str
        string representation of set of filepaths

    dim: str
        dimension to concatenate along

    '''

    mdls = []
    dsets = []
    pths = glob(filepaths)
    for pth in pths:

        model = re.search(r'/shares/gcp/outputs/temps/(?P<rcp>rcp[0-9]{2})(?P<model>[^/]+)/climtas.nc4', pth).group('model')
        mdls.append(model)

        dsets.append(xr.open_dataset(pth))


    return xr.concat(dsets, dim=pd.Index(mdls, name=dim))



# def period_reduce(data,period=20, reduce='mean', dim='year'):
#     '''
#     Takes a periodized summary of the data along the specified dimension
#     '''



#     data['period'] = data['dim']//20*20

#     dsgpd = data.groupby('period').mean(dim=dim)












