"""
The ``wind_turbine.py`` module contains the data class WindTurbine that implements
a wind turbine and functions needed for the modelling of a
wind turbine.

SPDX-FileCopyrightText: 2024 <jorgethomasm@ieee.org>
SPDX-License-Identifier: MIT
"""

import math
import pandas as pd
from dataclasses import dataclass

@dataclass
class WindTurbine:
    """ 
    A custom and simple model of the requiered attributes and
    properties of a Wind Turbine
    """
    # ====== Wind Turbine Atributes (Specs) ======

    manufacturer: str  # e.g. Goldwin
    model: str # e.g. GW 165-6.0 6300 
    
    # Location
    latitude: float
    longitude: float

    rated_power: float # [kW]
    rated_wind_speed: float # [m/s] at standard air density    
    hub_height: float # metres
    power_coefficient: float # Cp
    power_curve: pd.DataFrame
    rotor_diameter: float # metres

    cut_in_speed: float # m/s
    cut_out_speed: float # m/s

    # Variable Speed - Variable pitch  

    # Speed Range During Power Production
    min_speed: float # [RPM]
    max_speed: float # [RPM] Nominal

    # Area
    def area(self) -> float:
        """
        Sweapt area calculation in squared metres.
        """
        return math.pi*(self.rotor_diameter/2)**2

    # Tip speed of blade 
    @property
    def min_tip_speed(self) -> float:
        """
        Linear speed of blade tip for Tip-Speed Ratio (lambda) calculation.
        It returns Min. tip-speed in [m/s]
        """
        return 2*math.pi*(self.min_speed/60)*(self.rotor_diameter/2)
    
    @property
    def max_tip_speed(self) -> float:
        """
        Linear speed of blade tip for Tip-Speed Ratio (lambda) calculation.
        It returns Max. tip-speed in [m/s]
        Sometimes this can be obtained directly from tech-spechs.
        """
        # max_tip_speed <- 92 # [m/s] # From Specs.

        return 2*math.pi*(self.max_speed/60)*(self.rotor_diameter/2)
   
