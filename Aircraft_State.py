############################################################
# Aircraft_State.py
# Stores aircraft design configuration (NO physics here)
############################################################
import pandas as pd

class AircraftState:
    def __init__(self):

        ####################################################
        # UNIT SYSTEM
        ####################################################
        # "SI" or "IMPERIAL"
        self.units = "SI"

        ####################################################
        # PRIMARY DESIGN PARAMETERS
        ####################################################
        self.wing_area = None         # m^2
        self.wingspan = None          # m
        self.length = None            # m
        self.mean_chord = None        # m
        self.cg = None                # meters from nose
        self.engine_thrust = None     # Newtons
        self.engine_spool_rate = None # Spool Rate Of Engine

       ####################################################
       # FUEL SYSTEM
       ####################################################
        self.empty_mass = None        # kg (aircraft without fuel)
        self.max_fuel_mass = None     # kg
        self.initial_fuel_mass = None # kg at start
        self.fuel_burn_rate = None    # kg per second at full throttle

        ####################################################
        # TAIL GEOMETRY
        ####################################################
        self.tail_area = None         # m^2
        self.tail_arm = None          # distance from CG (m)

        ####################################################
        # AERODYNAMIC COEFFICIENTS
        ####################################################
        self.CL0 = None               # Lift coefficient at 0 AoA
        self.CL_alpha = None          # Lift slope per radian
        self.CL_max = None            # Maximum lift coefficient (stall)

        self.CD0 = None               # Zero-lift drag coefficient
        self.k = None                 # Induced drag factor

        self.Cm_alpha = None          # Pitch moment coefficient slope

        ####################################################
        # CONTROL SURFACES
        ####################################################
        self.aileron_effectiveness = None
        self.elevator_effectiveness = None
        self.rudder_effectiveness = None
        self.flap_effectiveness = None
        self.max_flap_angle = None    # degrees

        ####################################################
        # ROTATIONAL INERTIA
        ####################################################
        self.Ixx = None               # Roll inertia
        self.Iyy = None               # Pitch inertia
        self.Izz = None               # Yaw inertia
        ####################################################
        # STRUCTURAL LIMITS
        ####################################################
        self.max_g = None

    ####################################################
    # CONVERT IMPERIAL TO SI
    ####################################################
    def convert_to_SI(self):
     if self.units == "IMPERIAL":

        # Mass (lb → kg)
        if self.empty_mass is not None:
            self.empty_mass *= 0.453592

        if self.max_fuel_mass is not None:
            self.max_fuel_mass *= 0.453592

        if self.initial_fuel_mass is not None:
            self.initial_fuel_mass *= 0.453592

        if self.fuel_burn_rate is not None:
            self.fuel_burn_rate *= 0.453592

        # Area (ft² → m²)
        if self.wing_area is not None:
            self.wing_area *= 0.092903

        if self.tail_area is not None:
            self.tail_area *= 0.092903

        # Length (ft → m)
        if self.wingspan is not None:
            self.wingspan *= 0.3048

        if self.length is not None:
            self.length *= 0.3048

        if self.mean_chord is not None:
            self.mean_chord *= 0.3048

        if self.cg is not None:
            self.cg *= 0.3048

        if self.tail_arm is not None:
            self.tail_arm *= 0.3048

        # Force (lbf → N)
        if self.engine_thrust is not None:
            self.engine_thrust *= 4.44822

        self.units = "SI"
    ####################################################
    # EXPORT TO DICTIONARY
    ####################################################
    def to_dict(self):
        return {

            "units": self.units,

            # Primary
            "wing_area": self.wing_area,
            "wingspan": self.wingspan,
            "length": self.length,
            "mean_chord": self.mean_chord,
            "cg": self.cg,
            "engine_thrust": self.engine_thrust,

            # Fuel
           "empty_mass": self.empty_mass,
           "max_fuel_mass": self.max_fuel_mass,
           "initial_fuel_mass": self.initial_fuel_mass,
           "fuel_burn_rate": self.fuel_burn_rate,

            # Tail
            "tail_area": self.tail_area,
            "tail_arm": self.tail_arm,

            # Aerodynamics
            "CL0": self.CL0,
            "CL_alpha": self.CL_alpha,
            "CL_max": self.CL_max,
            "CD0": self.CD0,
            "k": self.k,
            "Cm_alpha": self.Cm_alpha,

            # Controls
            "aileron_effectiveness": self.aileron_effectiveness,
            "elevator_effectiveness": self.elevator_effectiveness,
            "rudder_effectiveness": self.rudder_effectiveness,
            "flap_effectiveness": self.flap_effectiveness,
            "max_flap_angle": self.max_flap_angle,

            # Inertia
            "Ixx": self.Ixx,
            "Iyy": self.Iyy,
            "Izz": self.Izz,
            
            # Structural
            "max_g": self.max_g 
         }
    def validate(self):
        required = [
        "wing_area",
        "wingspan",
        "empty_mass",
        "engine_thrust",
        "CL0",
        "CL_alpha",
        "CL_max",
        "CD0",
        "k",
        "Ixx",
        "Iyy",
        "Izz"
        ]

        for field in required:
         if getattr(self, field) is None:
            raise ValueError(
                f"Missing aircraft parameter: {field}")
    def get_stall_angle_rad(self):
        #Calculates critical stall angle of attack in radians.

         if self.CL_alpha is not None and self.CL_alpha > 0:

            return(self.CL_max - self.CL0) / self.CL_alpha
            return 0.2618  # Safe default fallback (15 degrees in radians)


    

    ####################################################
    # LOAD FROM DICTIONARY
    ####################################################
    def from_dict(self, data):

        self.units = data.get("units")

        self.wing_area = data.get("wing_area")
        self.wingspan = data.get("wingspan")
        self.length = data.get("length")
        self.mean_chord = data.get("mean_chord")
        self.cg = data.get("cg")
        self.engine_thrust = data.get("engine_thrust")
        self.empty_mass = data.get("empty_mass")
        self.max_fuel_mass = data.get("max_fuel_mass")
        self.initial_fuel_mass = data.get("initial_fuel_mass")
        self.fuel_burn_rate = data.get("fuel_burn_rate")

        self.tail_area = data.get("tail_area")
        self.tail_arm = data.get("tail_arm")

        self.CL0 = data.get("CL0")
        self.CL_alpha = data.get("CL_alpha")
        self.CL_max = data.get("CL_max")
        self.CD0 = data.get("CD0")
        self.k = data.get("k")
        self.Cm_alpha = data.get("Cm_alpha")

        self.aileron_effectiveness = data.get("aileron_effectiveness")
        self.elevator_effectiveness = data.get("elevator_effectiveness")
        self.rudder_effectiveness = data.get("rudder_effectiveness")
        self.flap_effectiveness = data.get("flap_effectiveness")
        self.max_flap_angle = data.get("max_flap_angle")

        self.Ixx = data.get("Ixx")
        self.Iyy = data.get("Iyy")
        self.Izz = data.get("Izz")
        self.max_g = data.get("max_g")