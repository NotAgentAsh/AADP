############################################################
# Aircraft_State.py
# UI INTERFACE FOR ENTERING AIRCRAFT VALUES WHICH THEN GO TO PHYSCIS ENGINE.
############################################################
import pandas as pd
import json
import numpy as np

class AircraftState:
    def __init__(self):
     
     pass

     #FILL FROM JSON FILE
    def load_json(self, location):
     with open(location) as f:
      data = json.load(f)
      #Plane
      self.aricraft_name = data["aircraft_name"]

      #Physics
     
     #Plane Engine
     self.max_engine_thrust = data["max_engine_thrust"]
     self.engine_spool_rate = data["engine_spool_rate"]
     self.fuel_burn_rate = data["fuel_burn_rate"] #Fuel burnt In Kg Per Second

     #Structural Data
     self.max_flap_angle = data["max_flap_angle"] #In Degrees
     self.max_g = data["max_g"]
     self.max_airspeed = data["max_airspeed"]
     self.max_altitude = data["max_altitude"]
     self.max_alpha = data["max_aoa"] #Alpha is used to represent aoa in physics.
     self.CL_alpha = data["Cl_alpha"]

     #Weight
     self.empty_mass = data['max_empty_mass']
     self.max_fuel_mass = data["max_fuel_mass"]
     self.max_payload_mass = data['max_payload_mass']

     #Geometry of Plane
     self.wing_area = data["wing_area"]
     self.wingspan = data["wingspan"]
     #self.mean_chord = data["mean_chord"]
     self.length = data["length"]
     self.cg = data["cg"]

     #MAC Calculation
     self.wing_shape = data["wing_shape"]

     if self.wing_shape == "rectangular":
       if self.wingspan > 0:
        self.mean_chord = self.wing_area/self.wingspan

     if self.wing_shape == "tapered":
       if self.wingspan > 0:
        self.root_chord = data["root_chord"]
        self.tip_chord = data["tip_chord"]
        self.mean_chord = (
       (2 / 3) * self.root_chord *
       (1 + self.taper_ratio + self.taper_ratio**2) /
       (1 + self.taper_ratio))

