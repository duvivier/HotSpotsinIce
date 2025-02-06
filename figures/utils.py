import traceback
import warnings

import numpy as np
import xarray as xr

# import variable_defs

nmols_to_PgCyr = 1e-9 * 86400. * 365. * 12e-15

### define functions to load the biological data
# define the metrics we can load 
metrics_dict = {
    "NPP": ['photoC_TOT_zint'],
    "Zooplankton Production": ['graze_diat_zint', 'graze_sp_zint'],
    "Diatom fraction (biomass)": ['diatC', 'spC'],
    "Mesozoo production": ['graze_diat_zint', 'graze_sp_zint', 'diatC', 'spC'],
    "Mesozooplankton biomass": ['zooC', 'diatC', 'spC', 'graze_diat_zint', 'graze_sp_zint'],
    "Trophic Level 3": ['graze_diat_zint', 'graze_sp_zint', 'diatC', 'spC'],
    "Krill Growth Potential": ['TEMP','diatChl','spChl','diazChl']
}

def get_metrics_list():
    return list(metrics_dict.keys())

# function to return the variables we need to return for all metrics
def get_metric_variable(metric):
    var_names = metrics_dict[metric]
    # handle the case where there is only one variable
    if isinstance(var_names, str):
        return var_names
    # handle the case where there are multiple variables
    else:
        return var_names[:]

# function to average over top 150m for relevant variables and to keep time bound
def preprocess(ds):
    tb = ds.time_bound
    # check if relevant variables are in dataset, and if so, average over the dimension
    if hasattr(ds,'TEMP'):
        print('getting top level (500cm) temperature')
        temp = ds.TEMP
        ds['TEMP'] = temp.isel(z_t=0)
        ds['TEMP'].attrs['long_name'] = 'ocean temperature, surface (500cm)'
        del(temp)    
    if hasattr(ds,'diatChl'):
        print('getting top level (500cm) diatom chlorophyll')
        temp = ds.diatChl
        ds['diatChl'] = temp.isel(z_t_150m=0)
        ds['diatChl'].attrs['long_name'] = 'diatom chlorophyll, surface (500cm)'
        del(temp) 
    if hasattr(ds,'diazChl'):
        print('getting top level (500cm) diazatroph chlorophyll')
        temp = ds.diazChl
        ds['diazChl'] = temp.isel(z_t_150m=0)
        ds['diazChl'].attrs['long_name'] = 'diazatroph chlorophyll, surface (500cm)'
        del(temp)         
    if hasattr(ds,'spChl'):
        print('getting top level (500cm) small phytoplankton chlorophyll')
        temp = ds.spChl
        ds['spChl'] = temp.isel(z_t_150m=0)
        ds['spChl'].attrs['long_name'] = 'small phytoplankton chlorophyll, surface (500cm)'
        del(temp)         
    if hasattr(ds,'diatC'):
        print('averaging diatC over top 150m')
        temp = ds.diatC
        ds['diatC'] = temp.mean(dim='z_t_150m')
        ds['diatC'].attrs['long_name'] = 'diatom plankton carbon, top 150m mean'
        del(temp)
    if hasattr(ds,'spC'):
        print('averaging spC over top 150m')
        temp = ds.spC
        ds['spC'] = temp.mean(dim='z_t_150m')
        ds['spC'].attrs['long_name'] = 'small phytoplankton carbon, top 150m mean'
        del(temp)
    
    #re-write time bound with saved value
    ds['time_bound'] = tb
    return ds

# function for loading datasets
def load_datasets(varnames, experiment,lat_min,lat_max):
    ds_list = []
    for varname in varnames:
        subset = catalog.search(component='ocn',
                                variable=varname,
                                experiment=experiment,
                                forcing_variant='cmip6',
                               )
        with dask.config.set(**{'array.slicing.split_large_chunks': True}):
            dsets = subset.to_dataset_dict()
        ds = dsets[f'ocn.{experiment}.pop.h.cmip6.{varname}'] 
        
        # compute time mean to get correct months
        ds['time']= ds.time_bound.compute().mean(dim="d2")
        # keep only some variables
        keep_vars=['z_t','time_bound','z_t_150m','KMT','TLAT','TLONG','time'] + [varname]
        ds = ds.drop([v for v in ds.variables if v not in keep_vars])
        ds_list.append(ds)
        ds = xr.merge(ds_list, compat="override")
        
        # crop data to the latitudes we want, use given lat/lon, not specific indices
        #ds = ds.isel(nlat=slice(0,37)) # Crop to Southern Ocean, ind_start = 0, ind_end = 37
        ds = ds.where(((ds['TLAT'] <= lat_max) & (ds['TLAT'] >= lat_min)), drop=True)
        
    return ds


# ## define functions to adjust grid for plotting

def adjust_pop_grid(tlon,tlat,field):
    nj = tlon.shape[0]
    ni = tlon.shape[1]
    xL = int(ni/2 - 1)
    xR = int(xL + ni)

    tlon = np.where(np.greater_equal(tlon,min(tlon[:,0])),tlon-360.,tlon)
    lon  = np.concatenate((tlon,tlon+360.),1)
    lon = lon[:,xL:xR]

    if ni == 320:
        lon[367:-3,0] = lon[367:-3,0]+360.
    lon = lon - 360.
    lon = np.hstack((lon,lon[:,0:1]+360.))
    if ni == 320:
        lon[367:,-1] = lon[367:,-1] - 360.

    #-- trick cartopy into doing the right thing:
    #   it gets confused when the cyclic coords are identical
    lon[:,0] = lon[:,0]-1e-8
    
    #-- periodicity
    lat  = np.concatenate((tlat,tlat),1)
    lat = lat[:,xL:xR]
    lat = np.hstack((lat,lat[:,0:1]))

    field = np.ma.concatenate((field,field),1)
    field = field[:,xL:xR]
    field = np.ma.hstack((field,field[:,0:1]))
    return lon,lat,field


def normal_lons(lons):

    lons_norm=np.full((len(lons.nlat), len(lons.nlon)), np.nan)

    lons_norm_firstpart = lons.where(lons<=180.)
    lons_norm_secpart = lons.where(lons>180.) - 360.

    lons_norm_firstpart = np.asarray(lons_norm_firstpart)
    lons_norm_secpart = np.asarray(lons_norm_secpart)

    lons_norm[~np.isnan(lons_norm_firstpart)] = lons_norm_firstpart[~np.isnan(lons_norm_firstpart)]
    lons_norm[~np.isnan(lons_norm_secpart)] = lons_norm_secpart[~np.isnan(lons_norm_secpart)]

    lons_norm=xr.DataArray(lons_norm)
    lons_norm=lons_norm.rename({'dim_0':'nlat'})
    lons_norm=lons_norm.rename({'dim_1':'nlon'})
    
    return(lons_norm)


def calc_area(nx,ny,lats):

    area = xr.DataArray(np.zeros([ny,nx]), dims=('lat','lon'))

    j=0

    for lat in lats:

        pi     =    3.14159265359
        radius = 6378.137

        deg2rad = pi / 180.0

        resolution_lat =1./12. #res in degrees
        resolution_lon =1./12. #res in degrees

        elevation = deg2rad * (lat + (resolution_lat / 2.0))

        deltalat = deg2rad * resolution_lon
        deltalon = deg2rad * resolution_lat

        area[j,:] = (2.0*radius**2*deltalon*np.cos(elevation)*np.sin((deltalat/2.0)))

        j = j + 1

    return(area)
