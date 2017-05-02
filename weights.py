import xarray as xr
import numpy as np
import pandas as pd
import glob
import re
from impactlab_tools.utils import weighting


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
    pths = glob.glob(filepaths)
    for pth in pths:

        model = re.search(r'/shares/gcp/outputs/temps/(?P<rcp>rcp[0-9]{2})/(?P<model>[^/]+)/climtas.nc4', pth).group('model')
        mdls.append(model)

        dsets.append(xr.open_dataset(pth))

    return xr.concat(dsets, dim=pd.Index(mdls, name=dim))


def period_reduce(data,period=20, reduce='mean', dim='year'):
    '''
    Takes a periodized summary of the data along the specified dimension


    Returns
    -------
    Xarray DataSetdsgpd
    '''



    data['period'] = data[dim]//period*period

    return data.groupby('period').mean(dim=dim)




def get_weights(path):
    '''
    Gets the weights for models for SMME weighting

    Returns
    -------
    pd.Series

    '''

    weights = pd.read_csv(path, delimiter='\t')

    weights = weights[['model', 'weight']]

    weights.set_index('model', inplace=True)
    weights.index = weights.index.map(lambda s: s.upper().replace('*',''))

    return weights.weight




def upper_coord_names(ds, dim):
    '''
    Coerces coord names to upper case


    '''



    ds[dim] = list(map(lambda x: x.upper(), ds[dim].values))

    #we need to drop some of the coords for the ds

    ds = ds[2:,:,:,0]

    return ds


def get_quantiiles(ds, qauntiles, weights, dim, years=['2020', '2040','2060','2080']):


    wtd = weighted_quantile_xr(ds, quantiles, weights, dim)

    for i,year in enumerate(years): 
        df = wtd[i].to_pandas().T.to_csv('rcp45_quantiles_{}_.csv'.format(year))



