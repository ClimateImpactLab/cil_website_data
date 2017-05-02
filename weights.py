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


def period_reduce(data,period=20, dim='year'):
    '''
    Takes a periodized mean of the data along the specified dimension

    Parameters
    ----------
    data: Xarray Dataset

    period: int
        time period to 

    dim: str
        time dimension to take mean along

    Returns
    -------
    Xarray DataSet
    '''



    data['period'] = data[dim]//period*period

    return data.groupby('period').mean(dim=dim)




def get_weights(path):
    '''
    Gets the weights for models for SMME weighting

    Parameters
    ----------
    path: str
        path to read in the SMME-weights

    Returns
    -------
    pd.Series of model weights 

    '''

    weights = pd.read_csv(path, delimiter='\t')

    weights = weights[['model', 'weight']]

    weights.set_index('model', inplace=True)
    weights.index = weights.index.map(lambda s: s.upper().replace('*',''))

    return weights.weight




def upper_coord_names(ds, dim):
    '''
    Coerces coord names to upper case and removes 

    Paramters
    ---------
    ds: Xarray Dataset

    
    Returns
    -------
    Xarray Dataset


    '''



    ds[dim] = list(map(lambda x: x.upper(), ds[dim].values))


    

    return ds


def get_quantiiles(ds, quantiles, weights, dim, years=['2020', '2040','2060','2080']):
    '''
    Gets weighted quantiles of Climate model outputs
    Writes outputs to csv for each year in years parameter

    Parameters
    ----------
    ds: Xarray Dataset

    quantiles: list
        list of quantiles [.17, .5, .83, .95]

    weights: pd.Series
        Series of weights to apply to each model

    dim: str
        time dimension to apply weights 

    years: list of years to produce weighted outputs


    '''

    # we need to drop some of the coords for the ds
    ds = ds[2:,:,:,0]

    wtd = weighted_quantile_xr(ds, quantiles, weights, dim)

    for i,year in enumerate(years): 
        df = wtd[i].to_pandas().T.to_csv('rcp45_quantiles_{}_.csv'.format(year))



