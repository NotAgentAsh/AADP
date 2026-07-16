###########################################################################
# AADP.PY
# UI INTERFACE FOR ENTERING AIRCRAFT VALUES WHICH THEN GO TO PHYSICS ENGINE.
###########################################################################
#Path imports
from pathlib import Path
from unittest import result
#UI Imports
#Old UI Libs
from ursina import window
from ursina import *
import sys
#Future UI Library
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout

##################################
import ctypes
from ctypes import wintypes
import platform
import subprocess
import json
import numpy as np

PROJECT_FOLDER = Path(__file__).parent #Loads  main AADP folder as my main folder.

PRESETS_FOLDER = PROJECT_FOLDER / "Presets"

# Making Buttons for Presets
preset_buttons = []

# File Opener For Mac To Choose Presets
def mac_file_picker():
    script = 'POSIX path of (choose file with prompt "Select an aircraft preset (.json)")'
    print("Opening file picker...")
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    return Path(result.stdout.strip())

def windows_file_picker():
   pass

def linux_file_picker():
   pass


#OPENING PRESET FOR USERS OS TYPE.
def new_sim():
    print("New Simulation button clicked")
    system = platform.system()

    if system == "Darwin":
        location = mac_file_picker()

    elif system == "Windows":
        location = windows_file_picker()

    elif system == "Linux":
        location = linux_file_picker()

    else:
        output.text = "Unsupported operating system."
        return

    if not location:
        return

    load_aircraft(location)

def load_aircraft(location):
    try: #try tells python to try running the code if it crashes It wont atleast crash UI.
        aircraft = AircraftState()
        aircraft.load_json(location)

        text = ""

        for key, value in vars(aircraft).items():
            text += f"{key}: {value}\n"

        output.text = text
        New_Sim_Button.enabled = False

    except Exception as e:
        output.text = f"Error loading aircraft:\n{e}"
        print(e)

#UI
app = Ursina()
#app = QApplication

window.title = "AADP"           # Sets The Window title to AADP
window.borderless = False      # Keep the normal OS window frame
window.fullscreen = False      # Start windowed
window.size = (1280, 720)      # Starting size
window.fps_counter.enabled = False

New_Sim_Button = Button(
    text="New Simulation",
    scale=(0.35, 0.1), 
    position=(0, 0),
    color=color.azure,
    on_click=new_sim)

output = Text(
    text="",
    position=(-0.82, 0.42),
    origin=(-0.5, 0.5),
    scale=1)
    #wordwrap=40)


class AircraftState:
    def __init__(self): #This is wehre I'll store values that change while sim is running like- spped,altitude,etc so basically all that changes from UI of wind tunnel and doesnt come from .json
     
     pass

     #FILL FROM JSON FILE
    def load_json(self, location):
     #json_file = PRESETS_FOLDER / location
     with open(location, "r") as f: #"r" means reading mode.
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
        
#START AADP

app.run() #This initiates Ursina UI.