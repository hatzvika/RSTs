from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer()

# This script downloads ERA-Interim forecasts, on pressure levels or surface.
# Adapt the script to your requirements.
for current_year in range (1979, 1982):
    for param_str in ["151.128", "131.128", "132.128"]:
        if param_str == "151.128":
            levtype_str = "sfc"
            levlist_str = "850"
            param_name = "SLP"
            target_str = param_name + "_ERA_Int_10-50N_20-50E_full_" + str(current_year) + ".nc"
        else:
            levtype_str = "pl"
            levlist_str = "850"
            if param_str == "131.128":
                param_name = "uwind"
            else:
                param_name = "vwind"
            target_str = param_name + "_ERA_Int_850hPa_10-50N_20-50E_full_" + str(current_year) + ".nc"

        date_str = str(current_year) + "-01-01/to/" + str(current_year) + "-12-31"

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
            "levtype": levtype_str,
            "levelist": levlist_str,
            # "levelist": "/100/125/150/175/200/225/250/300/350/400/450/500/550/600/650/700/750/775/800/825/850/875/900/925/950/975/1000",
            "type": "an",
            "time": "00:00:00/06:00:00/12:00:00/18:00:00",
            "step": "0",
            # all available parameters, for codes see http://apps.ecmwf.int/codes/grib/param-db
            # Most used params by me are: Mean SLP = 151.128, Uwind = 131.128, Vwind = 132.128
            "param": param_str,
            # dates of data (YYYY-MM-DD)
            "date": date_str,
            # in 0.75 degrees lat/lon
            "grid": "0.75/0.75",
            # optionally restrict area (in N/W/S/E).
            "area": "50.25/19.5/9.75/50.25",
            "format": "netcdf",
            # set an output file name
            "target": target_str
        })
