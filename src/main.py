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
                                 hub_height=67,
                                 power_coefficient=0.4,
                                 power_input=None,
                                 power_curve=pd.read_csv("./data/database/swt-93_power_curve.csv"),
                                 rotor_diameter=93,
                                 cut_in_speed=4,
                                 cut_out_speed=25,
                                 min_speed=6,
                                 max_speed=16) for coordinates in wt_geocoords]

    # Get weather forecast for each wind turbine
    weather_data = []  # list with data frames
    for coordinates in wt_geocoords:
        weather_data.append(windfun.get_weather_forecast(*coordinates))

    # Input wind power calculation
    air_densities = []
    for i in range(0, len(weather_data)):
        air_densities.append(windfun.calc_humid_air_density(temperature=weather_data[i].loc[:, 'temperature_80m'],
                                                            relative_humidity=weather_data[i].loc[:,
                                                                              'relative_humidity_2m'],
                                                            pressure=weather_data[i].loc[:, 'surface_pressure']))
    
    p_in = []
    for i in range(0, len(air_densities)):
        p_in.append(windfun.calc_wt_input_power(area=wind_turbines[i].area(),
                                                cut_in=wind_turbines[i].cut_in_speed,
                                                cut_out=wind_turbines[i].cut_out_speed,
                                                air_density=air_densities[i],
                                                wind_speed=weather_data[i].loc[:, 'wind_speed_80m']))

    # Add input power to wind_turbines attributes
    for i in range(0, len(air_densities)):
        wind_turbines[i].power_input = p_in[i]
    
    
    # Save Table in data / RAW (for Power BI Vis)
    wtkeys = ['WT' + str(i+1) for i in range(len(wt_geocoords))]       
    # df_p_in = pd.concat(p_in, keys=wtkeys)
    # df_p_in.columns = ["id", "record", "p_in_kW"]
    # # df_p_in.drop("record", axis=1, inplace=True)
    # df_p_in.to_csv("./data/raw/p_in.csv", header=True, index=True, index_label='id')
        
    # Output electrical power calculation
    p_out =[]
    for i in range(0, len(air_densities)):
        p_out.append(windfun.calc_wt_output_power(rated_power=wind_turbines[i].rated_power, 
                                                  input_power=wind_turbines[i].power_input,
                                                  power_coeff=wind_turbines[i].power_coefficient,
                                                  power_curve= wind_turbines[i].power_curve, 
                                                  cut_in= wind_turbines[i].cut_in_speed, 
                                                  cut_out= wind_turbines[i].cut_out_speed, 
                                                  wind_speed = weather_data[i].loc[:, 'wind_speed_80m']))
        
    
    df_p_out = pd.DataFrame.from_records(p_out).transpose()
    df_p_out.columns = wtkeys    
    df_p_out['datetime'] = weather_data[0].date
    df_p_out_long = pd.melt(df_p_out, id_vars='datetime', value_vars=wtkeys, var_name='id', value_name='output_kW')
    df_p_out_long.to_csv("./data/raw/p_out.csv", header=True, index=False)



if __name__ == "__main__":
    main()
