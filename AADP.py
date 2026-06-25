from Aircraft_State import AircraftState
from Physics_Engine import PhysicsEngine
import pygame
import numpy as np
import sys
import pandas as pd
############################################################
# INPUT BOX
############################################################
class InputBox:

    def __init__(self, x, y, width, height, label):

        self.rect = pygame.Rect(x, y, width, height)

        self.text = ""
        self.label = label

        self.active = False

        self.font = pygame.font.SysFont(None, 32)

    ########################################################
    # DRAW
    ########################################################
    def draw(self, screen):

        # Label
        label_surf = self.font.render(self.label, True, (255, 255, 255))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 30))

        # Box
        color = (100, 180, 255) if self.active else (180, 180, 180)

        pygame.draw.rect(screen, color, self.rect, 2)

        # Text
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))

    ########################################################
    # HANDLE EVENTS
    ########################################################
    def handle_event(self, event):

        ####################################################
        # MOUSE CLICK
        ####################################################
        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        ####################################################
        # KEYBOARD INPUT
        ####################################################
        if event.type == pygame.KEYDOWN and self.active:

            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_RETURN:
                self.active = False

            else:
                self.text += event.unicode
############################################################
# APP
############################################################
class AADPApp:

    def __init__(self):
        pygame.init()
        self.state = "menu"
        self.aircraft = AircraftState()
        self.physics = None
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("AADP")

        self.clock = pygame.time.Clock()

        # Fonts
        self.title_font = pygame.font.SysFont(None, 60)
        self.button_font = pygame.font.SysFont(None, 36)

        ####################################################
        # UI POSITIONS (Editable)
        ####################################################
        self.cog_pos = (30, 30)
        self.button_size = (200, 60)
        self.new_sim_rect = pygame.Rect(0, 0, 0, 0)
        self.continue_rect = pygame.Rect(0, 0, 0, 0)
        self.cog_rect = pygame.Rect(0, 0, 0, 0)
        ####################################################
        # INPUT BOXES(Only for the basic geometry inputs)
        ####################################################
        self.input_boxes = [

          InputBox(300, 180, 250, 45, "Wing Area"),

          InputBox(300, 280, 250, 45, "Wingspan"),

          InputBox(300, 380, 250, 45, "Length")
         ]

    ########################################################
    # DRAW BUTTON
    ########################################################
    def draw_button(self, text, center_pos):

        rect = pygame.Rect(0, 0, *self.button_size)
        rect.center = center_pos

        pygame.draw.rect(self.screen, (60, 60, 80), rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2, border_radius=10)

        text_surf = self.button_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)

        self.screen.blit(text_surf, text_rect)

        return rect

    ########################################################
    # DRAW COG
    ########################################################
    def draw_cog(self):

        x, y = self.cog_pos

        pygame.draw.circle(self.screen, (200, 200, 200), (x, y), 20, 2)
        pygame.draw.circle(self.screen, (200, 200, 200), (x, y), 8, 2)

        for angle in range(0, 360, 45):
            direction = pygame.math.Vector2(1, 0).rotate(angle)

            x1 = x + int(10 * direction.x)
            y1 = y + int(10 * direction.y)

            x2 = x + int(18 * direction.x)
            y2 = y + int(18 * direction.y)

            pygame.draw.line(self.screen, (200, 200, 200), (x1, y1), (x2, y2), 2)

        return pygame.Rect(x - 20, y - 20, 40, 40)

    ########################################################
    # DRAW MENU
    ########################################################
    def draw_menu(self):

        self.screen.fill((20, 20, 30))

        # Center positions
        center_x = self.width // 2
        center_y = self.height // 2

        # Title
        title = self.title_font.render("AADP", True, (255, 255, 255))
        title_rect = title.get_rect(center=(center_x, 100))
        self.screen.blit(title, title_rect)

        # Buttons
        self.new_sim_rect = self.draw_button("New Simulation", (center_x, center_y - 40))
        self.continue_rect = self.draw_button("Continue Simulation", (center_x, center_y + 40))

        # Cog
        self.cog_rect = self.draw_cog()
    ########################################################
    # DRAW CONFIG SCREEN
    ########################################################
  
    def draw_config(self):

     self.screen.fill((25, 25, 35))

    
    # TITLE
    
     title = self.title_font.render(
        "Aircraft Configuration",
        True,
        (255, 255, 255)
    )

     self.screen.blit(title, (250, 70))
 
    # Draw Input Boxes
    
     for box in self.input_boxes:
        box.draw(self.screen)

    #########################################################
    #  Simulation
    #########################################################
    def run_simulation(self):

     self.screen.fill((10, 10, 20))

    ########################################################
    # HANDLE MOUSE
    ########################################################
    def handle_mouse(self, event):

     if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

        mouse_pos = event.pos

        if self.new_sim_rect.collidepoint(mouse_pos):

            print("New Simulation Clicked")
            self.state = "config"

        if self.continue_rect.collidepoint(mouse_pos):

            print("Continue Simulation Clicked")
            self.state = "simulation"

        if self.cog_rect.collidepoint(mouse_pos):

            print("Settings Clicked")

    ########################################################
    # RUN LOOP
    ########################################################
    def run(self):

        while True:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.RESIZABLE
                    )
                self.handle_mouse(event)

            if self.state == "menu":

              self.draw_menu()

            elif self.state == "config":

              self.draw_config()

            else:
 
              self.run_simulation()

            pygame.display.flip()

############################################################
# RUN
############################################################
if __name__ == "__main__":
    app = AADPApp()
    app.run()