"""
The ``jthomwindlib`` module contains the class WindTurbine that implements
a wind turbine and functions needed for the modelling of a
wind turbine.

SPDX-FileCopyrightText: 2024 <jorgethomasm@ieee.org>
SPDX-License-Identifier: MIT
"""

class WindTurbine:
    """ A custom and simple model of the requiered attributes of a Wind Turbine"""

    pass


def calc_sat_water_vapour_press(temperature):
     
     """
     Herman Wobus polynomial
     https://wahiduddin.net/calc/density_altitude.htm
       
     """
     tem = temperature
        
     es0 = 6.1078
     c0 = 0.99999683
     c1 = -0.90826951e-2
     c2 = 0.78736169e-4
     c3 =0.61117958e-6
     c4 =.43884187e-8
     c5 =0.29883885e-10
     c6 =.21874425e-12
     c7 =0.17892321e-14
     c8 =.11112018e-16
     c9 =0.30994571e-19
     
     pol =  c0+tem*(c1+tem*(c2+tem*(c3+tem*(c4+tem*(c5+tem*(c6+tem*(c7+tem*(c8+tem*(c9)))))))))
    
     p_sat = es0 / pol**8 # [hpas] = [mbar] # 1 mbar = 100 Pa
    
    # Approx.Tetens Eq. [mbar] p_sat = es0*10**((7.5*tem)/(237.3+tem))

     return p_sat

def calc_humid_air_density(temperature, relative_humidity, pressure):
    """
    Constants:
    R = 8314.32 # Universal gas constant (in 1976 Standard Atmosphere)
    Md = 28.964 # molecular weight of dry air [gm/mol]
    Mv = 18.016 # molecular weight of water vapor [gm/mol]
    
    """
    
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


def calc_tsr(tip_speed, wind_speed):
    """
    Calculate Tip-speed Ratio (TSR)
    tip_speed Linear speed of blade tip [m/s]
    wind_speed in [m/s]
    return tip-speed ratio [0, 1]
    """
    
    tsr = tip_speed / wind_speed

    return tsr


def calc_wt_output_power(rated_power, area, power_coeff, cut_in, cut_out, air_density, wind_speed):
    """
    Calculate the output power of a wind turbine
    rated_power in [kW]
    area circular swept area in [squared metres]
    Cp Power Coefficient
    cut_in cut-in wind speed [m/s]
    cut_out cut-out wind speed [m/s]
    air_density dry or humid air density [kg/m**3]
    wind_speed in [m/s]

    return generated electrical power [kW]

    """

    #TODO: add for loops or install numpy?
    
    # Cut-in / cut-out
    if wind_speed < cut_in:
        wind_speed = 0
    elif wind_speed > cut_out:
        wind_speed = 0
    else:
        wind_speed = wind_speed

    
    p_out = (power_coeff * area * air_density * wind_speed**3) / 2 # [W]
    p_out = p_out / 1000 # [kW]

    # Power Ratings
    if p_out > rated_power:
        p_out = rated_power
    
    return p_out
