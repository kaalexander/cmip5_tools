from cmip5_paths import *
from numpy import *
from netCDF4 import Dataset

# Calculate the multi-model-mean of monthly-averaged atmospheric output for
# RCPs 4.5 and 8.5. 
def mmm_atmos_rcp_raw ():

    expt_names = ['rcp45', 'rcp85']
    start_year = 2006
    end_year = 2100
    num_ts = 12*(end_year-start_year+1)
    # Directory containing output files from cmip5_atmos_rcp_raw.py
    directory = '/short/y99/kaa561/CMIP5_forcing/atmos/'
    # Path to ERA-Interim file (created using eraint_climatology_netcdf.py)
    eraint_file = directory + 'climatology/ERA-Interim.nc'
    # Variable names in NetCDF files
    var_names = ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10', 'tp', 'sf', 'e', 'ssrd', 'strd']
    # Corresponding units
    var_units = ['Pa', 'K', 'K', 'fraction', 'm/s', 'm/s', 'm/12h', 'm/12h', 'm/12h', 'J/m^2/12h', 'J/m^2/12h']

    # Get a list of CMIP5 model names
    model_names = build_model_list()

    # Read ERA-Interim grid
    id = Dataset(eraint_file, 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    id.close()

    # Loop over RCPs
    for expt in expt_names:
        print 'Processing experiment ' + expt

        output_file = directory + expt + '_raw/MMM.nc'
        # Set up output file
        print 'Setting up ' + output_file
        out_id = Dataset(output_file, 'w')
        # Define dimensions
        out_id.createDimension('longitude', size(lon))
        out_id.createDimension('latitude', size(lat))
        out_id.createDimension('time', num_ts)
        # Define dimension variables and fill with axes
        out_id.createVariable('longitude', 'f8', ('longitude'))
        out_id.variables['longitude'].units = 'degrees'
        out_id.variables['longitude'][:] = lon
        out_id.createVariable('latitude', 'f8', ('latitude'))
        out_id.variables['latitude'].units = 'degrees'
        out_id.variables['latitude'][:] = lat
        out_id.createVariable('time', 'f8', ('time'))
        out_id.variables['time'].units = 'month'
        out_id.variables['time'][:] = arange(1, num_ts+1)

        # Loop over variables
        for i in range(len(var_names)):
            var = var_names[i]
            print 'Variable ' + var

            num_models = 0  # Number of models in the multi-model mean
            multi_model_mean = None
            # Loop over models
            for model_name in model_names:
                # Read model data
                id = Dataset(directory + expt + '_raw/' + model_name + '.nc', 'r')
                model_data = id.variables[var][:,:,:]
                id.close()

                # Check for missing data
                try:
                    mask = model_data.mask
                except(AttributeError):
                    # There is no mask; set it to False
                    mask = False
                if all(mask):
                    # Everything is masked; data is missing for this variable
                    pass
                else:
                    # Add to multi-model mean and increment num_models
                    if multi_model_mean is None:
                        multi_model_mean = model_data[:,:,:]
                    else:
                        multi_model_mean[:,:,:] += model_data[:,:,:]
                    num_models += 1

            # Divide multi_model_mean (currently just a sum) by num_models
            multi_model_mean /= num_models
            # Define variable and fill with data
            out_id.createVariable(var_names[i], 'f8', ('time', 'latitude', 'longitude'))
            out_id.variables[var_names[i]].units = var_units[i]
            out_id.variables[var_names[i]][:,:,:] = multi_model_mean
        out_id.close()


# Command-line interface
if __name__ == "__main__":

    mmm_atmos_rcp_raw()
    


    
