"""
The ``wind_functions.py`` module contains functions needed for calculations of the 
energy yield forecast of a wind turbine.
In order to avoid "for loops" this library is vectorised with NumPy as external dependency.
It also contains theh function to retrieve the weather forecast.

SPDX-FileCopyrightText: 2024 <jorgethomasm@ieee.org>
SPDX-License-Identifier: MIT
"""

import numpy as np  # transform Python to R or MATLAB
import openmeteo_requests
import requests_cache
import pandas as pd
import csv
from retry_requests import retry

def read_csv_to_tuples(file_path: str, has_header = True) -> list[tuple]:
        """
        Read a text file (csv) with the geographical coordinates of each wind turbine.
        The file must have two columns: one for latitude and the other for longitude, in that order.
        The function returns a list of tuples.
        """

        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            
            if has_header:
                 next(csv_reader)  # Skip the header row
            
            list_of_tuples = [tuple(row) for row in csv_reader]

        return list_of_tuples


def get_weather_forecast(latitude: float, longitude: float) -> pd.DataFrame:
    """
    Extract weather forecast from the free Open Meteo service.
    Only included weather variables needed for the wind power calculations.


    """
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/dwd-icon"
    params = {
    	"latitude": latitude,
    	"longitude": longitude,
    	"hourly": ["relative_humidity_2m", "surface_pressure", "wind_speed_120m", "temperature_120m"],
    	"wind_speed_unit": "ms",
    	"timeformat": "unixtime"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    
    hourly_relative_humidity_2m = hourly.Variables(0).ValuesAsNumpy()    
    hourly_surface_pressure = hourly.Variables(1).ValuesAsNumpy()
    
    hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_80m = hourly.Variables(3).ValuesAsNumpy()
    hourly_wind_speed_120m = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_speed_180m = hourly.Variables(5).ValuesAsNumpy()
        
    hourly_temperature_2m = hourly.Variables(6).ValuesAsNumpy()
    hourly_temperature_80m = hourly.Variables(7).ValuesAsNumpy()
    hourly_temperature_120m = hourly.Variables(8).ValuesAsNumpy()
    hourly_temperature_180m = hourly.Variables(9).ValuesAsNumpy()

    hourly_wind_gusts_10m = hourly.Variables(10).ValuesAsNumpy()

    hourly_wind_direction_10m = hourly.Variables(11).ValuesAsNumpy()
    hourly_wind_direction_80m = hourly.Variables(12).ValuesAsNumpy()
    hourly_wind_direction_120m = hourly.Variables(13).ValuesAsNumpy()
    hourly_wind_direction_180m = hourly.Variables(14).ValuesAsNumpy()


    hourly_data = {"date": pd.date_range(
    	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
    	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = hourly.Interval()),
    	inclusive = "left"
    )}
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["surface_pressure"] = hourly_surface_pressure

    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_speed_80m"] = hourly_wind_speed_80m
    hourly_data["wind_speed_120m"] = hourly_wind_speed_120m
    hourly_data["wind_speed_180m"] = hourly_wind_speed_180m

    hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
    
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["temperature_80m"] = hourly_temperature_80m
    hourly_data["temperature_120m"] = hourly_temperature_120m
    hourly_data["temperature_180m"] = hourly_temperature_180m

    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["wind_direction_80m"] = hourly_wind_direction_80m
    hourly_data["wind_direction_120m"] = hourly_wind_direction_120m
    hourly_data["wind_direction_180m"] = hourly_wind_direction_180m

    hourly_df = pd.DataFrame(data = hourly_data)

    return hourly_df


def calc_sat_water_vapour_press(temperature: np.ndarray) -> np.ndarray:
     
     """
     Herman Wobus polynomial
     https://wahiduddin.net/calc/density_altitude.htm
       
     """
     tem = temperature
        
     es0 = 6.1078
     c0 = 0.99999683
     c1 = -0.90826951e-2
     c2 = 0.78736169e-4
     c3 = 0.61117958e-6
     c4 = 0.43884187e-8
     c5 = 0.29883885e-10
     c6 = 0.21874425e-12
     c7 = 0.17892321e-14
     c8 = 0.11112018e-16
     c9 = 0.30994571e-19
     
     pol =  c0+tem*(c1+tem*(c2+tem*(c3+tem*(c4+tem*(c5+tem*(c6+tem*(c7+tem*(c8+tem*(c9)))))))))
    
     p_sat = es0 / pol**8 # [hpas] = [mbar] # 1 mbar = 100 Pa
    
    # Approx.Tetens Eq. [mbar] p_sat = es0*10**((7.5*tem)/(237.3+tem))

     return p_sat


def calc_humid_air_density(temperature: np.ndarray, relative_humidity: np.ndarray, pressure: np.ndarray) -> np.ndarray:
    """
    Constants:
    R = 8314.32 # Universal gas constant (in 1976 Standard Atmosphere)
    Md = 28.964 # molecular weight of dry air [gm/mol]
    Mv = 18.016 # molecular weight of water vapor [gm/mol]
    
    The function returns a vector with humid air densities
    """
    if temperature.shape != relative_humidity.shape or temperature.shape != pressure.shape:
        raise ValueError("Input arrays must have the same shape") 


    Rd = 287.05 # J/(kg*degK)  | Gas constant for dry air (R/Md)
    Rv = 461.495 # J/(kg*degK) | Gas constant for water vapor (R/Mv)

    p_sat_vap = calc_sat_water_vapour_press(temperature) # [mbar]
    p_vap = relative_humidity * p_sat_vap # [mbar]

    # pressure = p_dry + p_vap = total air pressure
    p_dry = pressure - p_vap # [mbar]

    p_dPa = p_dry * 100 # [Pa] pressure of dry air (partial pressure)
    p_vPa = p_vap * 100 # [Pa] pressure of water vapor (partial pressure)
        
    temK = temperature + 273.15

    rho_h = (p_dPa / (Rd * temK)) + (p_vPa / (Rv * temK))

    return rho_h


def calc_tsr(tip_speed: float, wind_speed: float) -> float:
    """
    Calculate Tip-speed Ratio (TSR)
    tip_speed Linear speed of blade tip [m/s]
    wind_speed in [m/s]
    return tip-speed ratio [0, 1]
    """
    tsr = tip_speed / wind_speed

    return tsr



def calc_wt_input_power(area: float, cut_in: float, cut_out: float, air_density: np.ndarray, wind_speed: np.ndarray) -> np.ndarray:
    """
    Calculate the input power of a wind turbine,
    i.e., the kinetic power of the wind.
    
    - area: circular swept area in [squared metres]    
    - air_density: dry or humid air density [kg/m**3]
    - wind_speed: in [m/s]

    return kinetic wind (input) power [kW]

    """

    if air_density.shape != wind_speed.shape:
        raise ValueError(("air_density and wind_speed must have the same shape")) 
    
    p_in = (area * air_density * wind_speed**3) / 2 # wind power [W]

    p_in = p_in/1000 # [kW]
            
    return p_in



def calc_wt_output_power(rated_power: float, input_power: np.ndarray, power_coeff: float, power_curve: pd.DataFrame, cut_in: float, cut_out: float, wind_speed: np.ndarray) -> np.ndarray:
    """
    Calculate the output power of a wind turbine
    rated_power in [kW]
    input wind power [kW]
    Power Coefficient (Cp)
    cut_in cut-in wind speed [m/s]
    cut_out cut-out wind speed [m/s]    
    wind_speed in [m/s]

    return generated electrical power [kW]

    """

    if input_power.shape != wind_speed.shape:
        raise ValueError(("air_density and wind_speed must have the same shape"))
    
    # Standard var names for equations
    p_in = input_power
    Cp = power_coeff # wt efficiency 

    # Cut-in / cut-out
    p_in[wind_speed < cut_in] = 0
    p_in[wind_speed > cut_out] = 0
        
    
    # TODO: Get Power or CP curve for the turbine model
        
    if power_curve is None:
         p_out = Cp * p_in # [kW]    
    else:
         p_out = Cp * p_in # [kW]    
        



    # Limit output to rated power
    p_out[p_out > rated_power] = rated_power # override efficiency (Cp) drop
        
    return p_out
