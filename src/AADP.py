# AADP.PY
# UI INTERFACE FOR ENTERING AIRCRAFT VALUES WHICH THEN GO TO PHYSICS ENGINE.

#Path imports
from pathlib import Path
import webbrowser
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QDialog,
    QMessageBox,
    QStackedWidget,
)

from PySide6.QtCore import Qt
import json
import numpy as np

# Inter python imports

from Loader_3D import load_3D_Model, AircraftGeometry
from Model_Converter import convert_and_export
from Mesh_Gen import generate_mesh
from Cleanup import clean_surface
from State import AircraftState


# AIRCRAFT STATE (TO GO TO .cpp Engine via PyBind)

if getattr(sys, "frozen", False):
    # Running as PyInstaller app
    PROJECT_FOLDER = Path(sys.executable).parent.parent / "Resources"
else:
    # Running normally from SourceCode/AADP.py
    PROJECT_FOLDER = Path(__file__).parent.parent

PRESETS_FOLDER = PROJECT_FOLDER / "Assets" / "Presets"



def new_sim():

    presets = load_presets()

    if len(presets) > 0:
        refresh_presets()
        stack.setCurrentWidget(preset_page)
        return

    file, _ = QFileDialog.getOpenFileName(
        window,
        "Select Aircraft Preset",
        str(PROJECT_FOLDER),
        "JSON Files (*.json)"
    )

    if file:
        print("Selected:", file)
        load_aircraft(file)

def load_aircraft(location):

    source = Path(location)
    destination = PRESETS_FOLDER / source.name

    # Only copy if it is not already in Presets
    if source.resolve() != destination.resolve():

        destination.write_text(source.read_text())

    refresh_presets()



def load_presets(): #This Checks the Presets folder for .json presets
    presets = []

    if PRESETS_FOLDER.exists():

      for file in PRESETS_FOLDER.iterdir():

        if file.suffix.lower() == ".json":
          presets.append(file)

    return presets



#THE ADD BUTTON FUNCTION
def add_preset():

    file, _ = QFileDialog.getOpenFileName(
        window,
        "Select Aircraft Preset",
        str(PROJECT_FOLDER),
        "JSON Files (*.json)"
    )

    if file:
        load_aircraft(file)

# Clearing Presets

def clear_presets():
    while preset_layout.count():
        item = preset_layout.takeAt(0)

        if item is None:
            break

        widget = item.widget()

        if widget is not None:
            widget.deleteLater()

# Adding Delete Function to the Presets

def delete_preset(preset_path):

    if preset_path.exists():
        preset_path.unlink()   # Deletes JSON file

    refresh_presets()

class PresetCard(QWidget):

    def __init__(self, preset):
        super().__init__()

        self.preset = preset

        self.setFixedSize(180,180)

        # Main preset buttons
        self.button = QPushButton(preset.stem, self)
        self.button.setGeometry(0,0,180,180)

        self.button.clicked.connect(self.open_preset)

        # Trash button overlay
        self.delete_button = QPushButton("🗑️", self)
        self.delete_button.setGeometry(145,5,30,30)

        self.delete_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
        """)

        self.delete_button.clicked.connect(self.delete)


    def delete(self):

        if self.preset.exists():
            self.preset.unlink()

        refresh_presets()

    def open_preset(self):
        chosen_file_path = str(self.preset)
        print(f"User clicked on preset. File location: {chosen_file_path}")

        with open(chosen_file_path, "r") as f:
            file_content = json.load(f)
            print("Successfully opened file! Data contents:", file_content)

        state = AircraftState()
        state.load_json(chosen_file_path)

        aircraft = load_3D_Model()

        if aircraft is not None:
            state.model_geometry = aircraft

            # Unpack the aligned & real-scale vertices/faces
            output_path, consistency, conv_verts, conv_faces = convert_and_export(
                state, PROJECT_FOLDER / "Assets" / "Converted Models"
            )
            print(f"Mismatch: {consistency['mismatch'] * 100:.2f}%")

            conv_verts, conv_faces = clean_surface(conv_verts, conv_faces)

            # Pass converted geometry to Gmsh for mesh generation
            mesh_path = generate_mesh(conv_verts, conv_faces, state.aircraft_name)
            #print("Mesh written to:", mesh_path)


#Refreshing the Presets
def refresh_presets():

    clear_presets()

    presets = load_presets()

    for preset in presets:

        card = PresetCard(preset)

        preset_layout.addWidget(card)

    # Add button always exists

    plus_button = QPushButton("+")

    plus_button.setFixedSize(180,180)

    plus_button.clicked.connect(add_preset)

    preset_layout.addWidget(plus_button)


# Open my repo and leave a review
def open_repo():

    webbrowser.open("https://github.com/NotAgentAsh/AADP")

# Cog Wheel 

def open_settings():

    dialog = QDialog(window)
    dialog.setWindowTitle("AADP Settings")
    dialog.resize(400, 300)

    layout = QVBoxLayout(dialog)

    title = QLabel("AADP Settings")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    info = QLabel(
        "If you enjoy using AADP, consider leaving a GitHub Star ⭐\n"
        "or sharing feedback in the Discussions tab."
    )
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info.setWordWrap(True)

    github_button = QPushButton("⭐ Open AADP on GitHub")
    github_button.clicked.connect(open_repo)

    layout.addWidget(title)
    layout.addWidget(info)
    layout.addStretch()
    layout.addWidget(github_button)

    dialog.exec()




if __name__ == "__main__":
    #UI
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("AADP")
    window.resize(1280, 720)

    # Create the central widget
    central = QWidget()
    window.setCentralWidget(central)

    main_layout = QVBoxLayout(central)

    stack = QStackedWidget()

    main_layout.addWidget(stack)

    # Making Home Page

    home_page = QWidget()
    home_layout = QVBoxLayout(home_page)

    top_bar = QHBoxLayout()

    settings_button = QPushButton("⚙")
    settings_button.setFixedSize(40,40)
    settings_button.clicked.connect(open_settings)

    top_bar.addWidget(settings_button)
    top_bar.addStretch()

    home_layout.addLayout(top_bar)

    home_layout.addStretch()

    new_button = QPushButton("New Simulation")
    new_button.setFixedSize(220,60)
    new_button.clicked.connect(new_sim)

    home_layout.addWidget(new_button,alignment=Qt.AlignmentFlag.AlignCenter)

    home_layout.addStretch()


    # Making The Presets Page

    preset_page = QWidget()
    preset_page_layout = QVBoxLayout(preset_page)

    # Preset Page Top Bar

    preset_top = QHBoxLayout()

    preset_settings = QPushButton("⚙")
    preset_settings.setFixedSize(40,40)
    preset_settings.clicked.connect(open_settings)

    preset_top.addWidget(preset_settings)
    preset_top.addStretch()

    preset_page_layout.addLayout(preset_top)

    # Preset Layout

    preset_layout = QHBoxLayout()
    preset_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    preset_page_layout.addStretch()
    preset_page_layout.addLayout(preset_layout)
    preset_page_layout.addStretch()

    stack.addWidget(home_page)

    stack.addWidget(preset_page)

    stack.setCurrentWidget(home_page)

    #Quit AADP
    window.show()
    sys.exit(app.exec())