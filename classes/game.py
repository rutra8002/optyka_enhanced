import random
import os
import pygame
from pygame import *
from gui import gui_main as gui1
from gui.gui_main import GUI
from screens import settings_screen
import settingsSetup
from classes import fps
from classes import bin, images, gameobjects
from classes.achievements import Achievements
from classes import parkinson as particles
from classes.font import Font
import time
from datetime import datetime
import functions
import gui
from gui import polygonDrawing
from screens import achievements_screen


isDrawingModeOn = False
class Game:
    """
    The main game class that handles the game loop, events, rendering and settings.
    """
    def __init__(self, save):
        """
        Initializes the game with settings, pygame, objects, and other necessary attributes.
        """
        self.save_to_load = save
        self.settings = settingsSetup.load_settings()  # Load game settings
        self.width = self.settings['WIDTH']  # Game width
        self.height = self.settings['HEIGHT']  # Game height
        self.font = pygame.font.Font(Font, self.height//20)  # Font for displaying FPS
        self.objects = []  # List of game objects
        pygame.init()  # Initialize pygame
        # Set up the game display based on settings
        if self.settings['FULLSCREEN'] == 'ON':
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN, vsync=0)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height), vsync=0)

        self.run = True  # Game loop control
        self.fps = fps.return_fps()  # Frames per second
        self.tick = int((1 / self.fps) * 1000)  # Time per frame in milliseconds
        self.mousepos = None  # Mouse position which will be updated every time the left mouse button is clicked
        self.rightclickedmousepos = None  # Right click mouse position
        self.r = False  # Used for mouse wheel events
        self.current_flashlight = None  # Current flashlight object
        self.mode = 'default'  # Current game mode
        self.executed_command = 'default'  # Last executed command
        self.clock = pygame.time.Clock()  # Pygame clock for controlling FPS
        pygame.mouse.set_visible(False)  # Hide the default mouse cursor
        self.cursor_img = images.bad_coursor  # Custom cursor image
        self.cursor_img_rect = self.cursor_img.get_rect()  # Rectangle for the custom cursor image
        self.pen_img = images.pen
        self.pen_img_rect = self.pen_img.get_rect()
        self.achievements = Achievements(self)  # Achievements object

        self.p = False #used for properties windows for gameobjects

        self.selected_object = None

        self.cursor_particle_system = particles.UnityParticleSystem()

        self.cached_mousepos = None

        self.surface_num = 12 # IMPORTANT lower numbers = higher fps, higher numbers = better quality
        self.surfaces = [pygame.Surface((self.width, self.height), pygame.SRCALPHA) for _ in range(self.surface_num)]
        for surface in self.surfaces:
            surface.set_alpha(40)

        self.surface_rays = {i : [] for i in range(self.surface_num)}

        self.save = False
        self.save_title = None

        self.background_color = (0, 0, 0)

    def go_to_achievements_screen(self):
        self.mode = 'achievements'
        self.achievements_screen = achievements_screen.AchievementsScreen(self)


    def create_cursor_particles(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for i in range(1):
            self.cursor_particle_system.add_particle(
                mouse_x, mouse_y,
                random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5),
                150, random.randint(1, 2),
                random.randint(200, 255), random.randint(200, 255), random.randint(200, 255),
                250, 'square'
            )

    def create_clicked_particles(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for i in range(20):
            self.cursor_particle_system.add_particle(
                mouse_x, mouse_y,
                random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                50, random.randint(2, 3),
                random.randint(200, 255), random.randint(200, 255), random.randint(200, 255),
                200, 'circle'
            )

    def return_fps(self):
        return self.displayFPS()

    def events(self):
        """
        Handles all the pygame events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.run = False
                quit()
            if self.mode == 'default':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousepos = event.pos  # when the left button is clicked the position is saved to self.mousepos
                    if isDrawingModeOn:
                        polygonDrawing.addPoint(self.mousepos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.create_clicked_particles()
                    if event.button == 3:
                        self.rightclickedmousepos = event.pos
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.r = 5
                    if event.y < 0:
                        self.r = -5
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.p = True
                    elif event.key == 13 and isDrawingModeOn:
                        gui.polygonDrawing.createPolygon()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.achievements_button.is_clicked(event.pos):
                        self.achievements_button.action()


            elif self.mode == 'settings':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for object in self.objects:
                        if isinstance(object, settings_screen.Settings_screen):
                            object.checkevent(event.pos)

    def update(self):
        """
        Updates the game display and controls the game FPS.
        """
        pygame.display.update()
        self.clock.tick(self.fps)

    def render_particles(self):
        """
        Renders all the game objects and the custom cursor.
        """
        if self.cached_mousepos != pygame.mouse.get_pos():
            self.create_cursor_particles()

        self.cached_mousepos = pygame.mouse.get_pos()

        self.cursor_particle_system.update()
        self.cursor_particle_system.draw(self.screen)

    def render(self):
        """
        Renders all the game objects and the custom cursor.
        """
        self.achievements_button = achievements_screen.Button(self, "Achievements", self.width - 150, 300, 150, 40,
                                                              self.go_to_achievements_screen)
        self.render_particles()

        if self.mode == 'default':
            if self.settings['HD_Flashlight'] == 'ON':
                for surface in self.surfaces:
                    surface.fill((0, 0, 0, 0))
                #self.surfaces = [surface.copy() for surface in self.default_surfaces]

                for surface_num, rays in self.surface_rays.items():
                    if surface_num > self.surface_num -1:
                        break
                    for ray in rays:
                        functions.draw_thick_line(self.surfaces[surface_num], int(ray.start_point[0]), int(ray.start_point[1]),
                                             int(ray.end_point[0]), int(ray.end_point[1]), ray.color, 5)
                    self.screen.blit(self.surfaces[surface_num], (0, 0))

                self.surface_rays = {i: [] for i in range(self.surface_num)}

            sorted_objects = sorted(self.objects, key=lambda obj: getattr(obj, 'layer', 0))
            for object in sorted_objects:
                if type(self.mousepos) is tuple:
                    if type(object) is gui1.GUI:
                        object.checkifclicked(self.mousepos)
                    if isinstance(object, gameobjects.GameObject):
                        object.checkifclicked(self.mousepos)
                if type(self.rightclickedmousepos) is tuple:
                    if isinstance(object, gameobjects.GameObject):
                        object.selected(self.rightclickedmousepos)


                object.render()
                if type(object) != bin.Bin:
                    for bin_2 in self.objects:
                        if type(bin_2) == bin.Bin:
                            bin_2.checkCollision(object)
                            break
            # if isDrawingModeOn:
            #     optyka.gui.polygonDrawing.renderDots()
        elif self.mode == 'settings':
            if self.executed_command != 'settings':
                self.settings_screen = settings_screen.Settings_screen(self)
                self.settings_screen.render()
                self.executed_command = 'settings'
            else:
                self.settings_screen.render()
        elif self.mode == 'load_new_settings':
            self.objects.remove(self.settings_screen)
            self.settings_screen = None
            self.mode = 'default'
            self.settings = settingsSetup.load_settings()
            self.width = self.settings['WIDTH']
            self.height = self.settings['HEIGHT']
            if self.settings['FULLSCREEN'] == 'ON':
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode((self.width, self.height))
            for object in self.objects:
                if type(object) == gui1.GUI or type(object) == bin.Bin:
                    object.load_settings()
            self.executed_command = 'default'

        if self.mode == 'default':
            self.achievements_button.render()
        elif self.mode == 'achievements':
            self.achievements_screen.render()
        self.cursor_img_rect.center = pygame.mouse.get_pos()  # update position
        if isDrawingModeOn:
            self.screen.blit(self.pen_img, self.cursor_img_rect)
        else:
            self.screen.blit(self.cursor_img, self.cursor_img_rect)  # draw the cursor
        self.displayFPS()
        self.displayClock()


    def background(self):
        # Use the background color attribute to fill the game display
        self.screen.fill(self.background_color)

    def displayFPS(self):
        """
        Displays the current FPS on the game display.
        """
        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {int(fps)}", True, "white")
        self.screen.blit(fps_text, (12.5, 10))
        return fps

    def displayClock(self):
        current_time = time.localtime()
        current_hour = current_time.tm_hour
        current_minute = current_time.tm_min
        current_second = current_time.tm_sec
        if current_hour < 10:
            current_hour = f"0{current_hour}"
        if current_minute < 10:
            current_minute = f"0{current_minute}"
        if current_second < 10:
            current_second = f"0{current_second}"
        time_text = self.font.render(f"{current_hour}:{current_minute}:{current_second}", True, "white")
        self.screen.blit(time_text, (self.width - 157.5, 10))
        return time_text



    def loop(self):
        """
        The main game loop.
        """
        while self.run:
            self.background()
            self.render()
            self.update()
            self.mousepos = None  # resets self.mouspos
            self.rightclickedmousepos = None
            self.p = False
            self.events()
            self.achievements.fps_achievements()
            if self.save_to_load != None:
                self.load()
                self.save_to_load = None

    def load(self):
        save = settingsSetup.load_settings(f"saves/{self.save_to_load}.json")
        self.save_title = self.save_to_load
        for parameters in save:
            if not isinstance(parameters, dict):
                break

            mousepos = (500, 500)
            print('as')
            if parameters['class'] == "Flashlight":
                obj = gameobjects.Flashlight(self, [(mousepos[0], mousepos[1]), (mousepos[0] + 200, mousepos[1]), (mousepos[0] + 200, mousepos[1] + 100), (mousepos[0], mousepos[1] + 100)], (255, 255, 255), 0, 0.4, 0.5, image=images.torch)

            elif parameters['class'] == "Mirror":
                obj = gameobjects.Mirror(self, [(mousepos[0] - 100, mousepos[1] - 50), (mousepos[0] + 100, mousepos[1] - 50), (mousepos[0] + 100, mousepos[1] + 50), (mousepos[0] - 100, mousepos[1] + 50)], (255, 0, 0), 0, 0.9, 0.5, texture=images.wood, textureName='wood')

            elif parameters['class'] == "ColoredGlass":
                obj = gameobjects.ColoredGlass(self, [(mousepos[0] - 10, mousepos[1] - 50), (mousepos[0] + 10, mousepos[1] - 50), (mousepos[0] + 10, mousepos[1] + 50), (mousepos[0] - 10, mousepos[1] + 50)], (0, 255, 0), 0, 0.4, 0.5)

            elif parameters['class'] == "Prism":
                obj = gameobjects.Prism(self, [(mousepos[0] - 50, mousepos[1]), (mousepos[0], mousepos[1] - 100), (mousepos[0] + 50, mousepos[1])], (0, 0, 255), 0, 0.4, 0.5)

            elif parameters['class'] == "Lens":
                obj = gameobjects.Lens(self, [(mousepos[0] - 100, mousepos[1] - 100), (mousepos[0], mousepos[1] - 100), (mousepos[0], mousepos[1] + 100), (mousepos[0] - 100, mousepos[1] + 100)], (64, 137, 189), 0, 0, 140, 0, 0.5)

            # elif parameters['class'] == ""

            obj.parameters = parameters
            obj.change_parameters('not')
            self.objects.append(obj)

    def generate_save(self):
        self.save_obj = []
        for object in self.objects:
            if issubclass(type(object), gameobjects.GameObject):
                object.find_parameters()
                object.parameters['class'] = object.__class__.__name__
                self.save_obj.append(object.parameters)
        if not os.path.exists("saves"):
            os.makedirs("saves")

        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.save_obj.append(formatted_time)


    def save_to_file(self):
        if os.path.exists(f'saves/{self.save_title}'):
            old_save = settingsSetup.load_settings(f'saves/{self.save_title}.json')
            new_save = old_save.update(self.save_obj)
            settingsSetup.writesettingstofile(new_save, 2, f'saves/{self.save_title}.json')
        else:
            settingsSetup.writesettingstofile(self.save_obj, 2, f'saves/{self.save_title}.json')