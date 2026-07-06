############################################################
# AADP.PY
# UI INTERFACE FOR ENTERING AIRCRAFT VALUES WHICH THEN GO TO PHYSICS ENGINE.
############################################################
import pandas as pd
import json
import numpy as np

class AircraftState:
    def __init__(self):
     pass

     #FILL FROM JSON FILE
    def load_json(self, location="/Users/manishkumar/Desktop/AADP_Project/Presets/777-300ER.json"):
     with open(location) as f:
      data = json.load(f)

      #Required Values
      Required_Values = np.array([
        "aircraft_name",
        "max_engine_thrust",
        "engine_spool_rate",
        "fuel_burn_rate",
        "max_flap_angle",
        "max_g",
        "max_airspeed",
        "max_altitude",
        "max_aoa",
        "Cl_alpha",
        "max_empty_mass",
        "max_fuel_mass",
        "max_payload_mass",
        "wing_area",
        "wingspan",
        "length",
        "cg",
        "wing_shape"
      ])
     missing = [key for key in Required_Values if key not in data] #Cross checks keys in data with the ones in Required_Values
     if missing:
      raise ValueError(f"Missing required values in JSON: {missing}")

      #Plane
     self.aircraft_name = data["aircraft_name"]

      #Physics
     
     #Plane Engine
     self.max_engine_thrust = data["max_engine_thrust"]
     self.engine_spool_rate = data["engine_spool_rate"]
     self.fuel_burn_rate = data["fuel_burn_rate"] #Fuel burnt In Kg Per Second

     #Structural Data
     self.max_flap_angle = data["max_flap_angle"] #In Degrees
     self.max_g = data["max_g"]
     self.max_airspeed = data["max_airspeed"] #In Knots
     self.max_altitude = data["max_altitude"] #In Meters
     self.max_alpha = data["max_aoa"] #Alpha is used to represent aoa in physics.
     self.CL_alpha = data["Cl_alpha"]

     #Weight
     self.empty_mass = data['max_empty_mass'] #In Kg
     self.max_fuel_mass = data["max_fuel_mass"] #In Kg
     self.max_payload_mass = data['max_payload_mass'] #In Kg

     #Geometry of Plane
     self.wing_area = data["wing_area"] #In Square Meters
     self.wingspan = data["wingspan"] #In Meters
     #self.mean_chord = data["mean_chord"]
     self.length = data["length"] #in Meters
     self.cg = data["cg"] #As A fraction of MAC (Mean Aerodynamic Chord)

     #MAC (Mean Aerodynamic Chord) Calculation
     self.wing_shape = data["wing_shape"]

     if self.wing_shape == "rectangular":
       if self.wingspan > 0:
        self.mean_chord = self.wing_area/self.wingspan

     if self.wing_shape == "tapered":
       if self.wingspan > 0:
        self.root_chord = data["root_chord"]
        self.tip_chord = data["tip_chord"]
        self.taper_ratio = self.tip_chord/self.root_chord
        self.mean_chord = (
       (2 / 3) * self.root_chord *
       (1 + self.taper_ratio + self.taper_ratio**2) /
       (1 + self.taper_ratio))