"""
The ``main`` module performs all calculations and throw results ready to be interfaced wiht R's Reticulate package.
This script is called from the .qmd (Quarto) file 

SPDX-FileCopyrightText: 2024 <jorgethomasm@ieee.org>
SPDX-License-Identifier: MIT
"""

import pandas as pd
from lib import WindTurbine
from lib import wind_functions as windfun


def main():

    # Get wind turbine locations (geocoordinates)
    file_path = './data/database/Baltic-1_wt_geoloc.csv'
    wt_geocoords = windfun.read_csv_to_tuples(file_path)
    print(f"There are {len(wt_geocoords)} wind turbines.")
    
    # Instantiate Wind Turbines
    """
    The height of the turbine from the foundation to the blade tip is about 125m. 
    The monopiles are 30m tall and have a maximum diameter of 5.3m. 
    The rotor diameter of the turbines is 93m.
    https://www.renewable-technology.com/projects/baltic-1-offshore-wind-farm/
    """
    wind_turbines = [WindTurbine(manufacturer="Siemens", 
                       model="SWT-2.3-93", 
                       latitude=coordinates[0], 
                       longitude=coordinates[1], 
                       rated_power=2300, 
                       rated_wind_speed=13,                         
                       hub_height=67 , 
                       power_coefficient=0.4,
                       power_curve=pd.read_csv("./data/database/swt-93_power_curve.csv"),
                       rotor_diameter=93, 
                       cut_in_speed=4, 
                       cut_out_speed=25, 
                       min_speed=6, 
                       max_speed=16) for coordinates in wt_geocoords]
    
    # Get weather forecast for each wind turbine
    weather_data = [] # list with data frames
    for coordinates in wt_geocoords:
        weather_data.append(windfun.get_weather_forecast(*coordinates))
    
    print("debug")
    


if __name__ == "__main__":
    main()