

import numpy as np
import json
from Loader_3D import AircraftGeometry


class AircraftState:
    def __init__(self): #This is wehre I'll store values that change while sim is running like- spped,altitude,etc so basically all that changes from UI of wind tunnel and doesnt come from .json
     
             self.model_geometry: "AircraftGeometry | None" = None   # set later, once the user picks a Model

     #FILL FROM JSON FILE
    def load_json(self, location):
     #json_file = PRESETS_FOLDER / location
     with open(location, "r") as f: #"r" means reading mode.
      data = json.load(f)

      #Required Values
      Required_Values = np.array([
        "aircraft_name",
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
        "nose_to_tail_axis",
        "towards_nose",
        "height_axis",
        "towards_up",
      ])
     missing = [key for key in Required_Values if key not in data] #Cross checks keys in data with the ones in Required_Values
     if missing:
      raise ValueError(f"Missing required values in JSON: {missing}")

      #Plane
     self.aircraft_name = data["aircraft_name"]

      #Physics
     
     #Plane Engine
     

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
     self.length = data["length"] #In Meters



    # Manual axis mapping — required, no auto-detect
     self.nose_to_tail_axis = data["nose_to_tail_axis"]
     self.towards_nose = data["towards_nose"]

     self.height_axis = data["height_axis"]
     self.towards_up = data["towards_up"]
