from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer()

# This script downloads ERA-Interim forecasts, on pressure levels or surface.
# Adapt the script to your requirements.

server.retrieve({
    # Specify the ERA-Interim data archive. Don't change.
    "class": "ei",
    "dataset": "interim",
    "expver": "1",
    "stream": "oper",
    "repres": "sh",
    "domain": "G",
    "resol": "auto",
    # pressure levels (levtype:pl), all available levels (levelist) or surface levels. you MUST choose one and remark the other
    "levtype": "sfc",
    # "levtype": "pl",
    # "levelist": "850",
    # "levelist": "/100/125/150/175/200/225/250/300/350/400/450/500/550/600/650/700/750/775/800/825/850/875/900/925/950/975/1000",
    "type": "an",
    "time": "00:00:00/06:00:00/12:00:00/18:00:00",
    "step": "0",
    # all available parameters, for codes see http://apps.ecmwf.int/codes/grib/param-db
    # Most used params by me are: Mean SLP = 151.128, Uwind = 131.128, Vwind = 132.128
    "param": "151.128",
    # dates of data (YYYY-MM-DD)
    "date": "1985-01-01/to/1985-12-31",
    # in 0.75 degrees lat/lon
    "grid": "2.5/2.5",
    # optionally restrict area (in N/W/S/E).
    "area": "50.25/19.5/9.75/50.25",
    "format": "netcdf",
    # set an output file name
    "target": "SLP_ERA_Int_2.5_10-50N_20-50E_full_1985.nc",
})
