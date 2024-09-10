"""
The ``main`` module performs all calculations and throw results ready to be interfaced wiht R's Reticulate package.
This script is called from the .qmd (Quarto) file 

SPDX-FileCopyrightText: 2024 <jorgethomasm@ieee.org>
SPDX-License-Identifier: MIT
"""

from lib import WindTurbine
from lib import wind_functions as windfun

def main():

    # List of tuples containing person attributes
    wt_locations = [(53.88, 7.40), (53.88, 7.40), (53.88, 7.40)]

    wt_1 = WindTurbine(manufacturer="Siemens", 
                       model="SWT-2.3-93", 
                       latitude=53.88, 
                       longitude=7.40, 
                       rated_power=2300, 
                       rated_wind_speed=13,                         
                       hub_height=133 , 
                       power_coefficient=0.4, 
                       rotor_diameter=93, 
                       cut_in_speed=4, 
                       cut_out_speed=25, 
                       min_speed=6, 
                       max_speed=16)
    
    # Instantiate Wind Park
    wind_turbines = [WindTurbine(manufacturer="Siemens", 
                       model="SWT-2.3-93", 
                       latitude=location, 
                       longitude=location, 
                       rated_power=2300, 
                       rated_wind_speed=13,                         
                       hub_height=133 , 
                       power_coefficient=0.4, 
                       rotor_diameter=93, 
                       cut_in_speed=4, 
                       cut_out_speed=25, 
                       min_speed=6, 
                       max_speed=16) for location in wt_locations]
    
    weather_data = []
    for location in wt_locations:
        weather_data.append(windfun.get_weather_forecast(location)) # arg latitude, longitude

    print("wind park ready.")



if __name__ == "__main__":
    main()