import time

import pygame
from gui import ModifyParameters as mp
from classes import light, sounds, images
import math
from pygame.transform import rotate
import random
import settingsSetup
from pygame import gfxdraw
settings = settingsSetup.start()

NUM_RAYS = 15
FOV = 5
HALF_FOV = 2.5
DELTA_ANGLE = FOV / NUM_RAYS

class GameObject:

    def __init__(self, game, points, color, angle, image = None, texture = None):
        # Initialize common attributes
        self.game = game
        self.points = points
        self.color = color
        self.on = True
        self.selectedtrue = False
        self.mousepos = None
        self.layer = 1
        self.placed = False
        self.angle = angle
        self.image = image if image else None
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.triangles_generated = False
        self.update_rect()

        self.lazer = False

        self.texture = texture if texture else None

        self.find_parameters()

    def update_rect(self):
        # Update the rect based on the points
        min_x = min(pt[0] for pt in self.points)
        min_y = min(pt[1] for pt in self.points)
        max_x = max(pt[0] for pt in self.points)
        max_y = max(pt[1] for pt in self.points)
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    def get_triangles(self):
        # Check if triangles have already been generated
        if not self.triangles_generated:
            center_x = sum(x for x, _ in self.points) / len(self.points)
            center_y = sum(y for _, y in self.points) / len(self.points)
            self.triangles = [((center_x, center_y), (self.points[i][0], self.points[i][1]),(self.points[i + 1][0], self.points[i + 1][1])) for i in range(len(self.points) - 1)]
            self.triangles.append(((center_x, center_y), (self.points[len(self.points) - 1][0],self.points[len(self.points) - 1][1]),(self.points[0][0], self.points[0][1])))
            self.triangles_generated = True  # Set the flag to True after generating triangles

        return self.triangles
    def get_slopes(self):
        self.slopes=[(self.points[i],self.points[i+1]) for i in range(len(self.points)-1)]
        self.slopes.append((self.points[len(self.points)-1],self.points[0]))



    def draw_triangle(self,index):
        pygame.gfxdraw.aapolygon(self.game.screen, (255, 255, 255), self.triangles[index])
    def render(self):
        # print(self.get_triangles())

        self.get_slopes()


        if not self.selectedtrue:

            # Render the image if available
            if self.image:
                center_x = sum(x for x, _ in self.points) / len(self.points)
                center_y = sum(y for _, y in self.points) / len(self.points)
                rotated_image = rotate(self.image, -self.angle)
                image_rect = rotated_image.get_rect(center=(center_x, center_y))

                # Blit the rotated image without transparency
                self.game.screen.blit(rotated_image, image_rect.topleft)
            else:
                # Draw the rotated lines without transparency
                if self.texture:
                    pygame.gfxdraw.textured_polygon(self.game.screen, self.points, self.texture, int(self.x), int(self.y))
                else:
                    pygame.gfxdraw.filled_polygon(self.game.screen, self.points, self.color)

        else:
            mousepos = pygame.mouse.get_pos()
            if self.game.r:

                self.adjust(mousepos[0], mousepos[1], self.game.r)
                self.game.r = False

            elif self.game.p:
                self.change_parameters()
                self.selectedtrue = False

            else:
                self.adjust(mousepos[0], mousepos[1], 0)
            self.drawoutline()

    def rotate_points(self, points, angle):
        # Rotate points around the center of the object
        center_x = sum(x for x, _ in points) / len(points)
        center_y = sum(y for _, y in points) / len(points)

        # Create a new list to store the rotated points
        rotated_points = []

        # Rotate each point around the center
        for x, y in points:
            # Translate the point to the origin
            translated_x = x - center_x
            translated_y = y - center_y

            # Rotate the translated point
            rotated_x = translated_x * math.cos(math.radians(angle)) - translated_y * math.sin(math.radians(angle))
            rotated_y = translated_x * math.sin(math.radians(angle)) + translated_y * math.cos(math.radians(angle))

            # Translate the rotated point back to the original position
            final_x = rotated_x + center_x
            final_y = rotated_y + center_y

            # Add the rotated point to the list
            rotated_points.append((final_x, final_y))

        return rotated_points

    def adjust(self, x, y, d_angle):
        # Adjust the object's position and angle
        self.angle += d_angle
        self.x = x - sum(pt[0] for pt in self.points) / len(self.points)
        self.y = y - sum(pt[1] for pt in self.points) / len(self.points)

        # Reset the flag to regenerate triangles
        self.triangles_generated = False

        # Update the points based on the new position and angle
        self.points = self.rotate_points(self.points, d_angle)

        # Assuming self.transparent_surface is a surface with transparency
        # Blit the rotated image with transparency
        if self.image:
            rotated_image = pygame.transform.rotate(self.image, -self.angle)
            image_rect = rotated_image.get_rect(center=((self.x + sum(pt[0] for pt in self.points) / len(self.points)),
                                                        (self.y + sum(pt[1] for pt in self.points) / len(self.points))))
            self.game.screen.blit(rotated_image, image_rect.topleft)
            # Draw the rotated lines without transparency
            #rotated_points = self.rotate_points(self.points, self.angle)
            self.points = [(x + self.x, y + self.y) for x, y in self.points]
            self.update_rect()

        else:
            self.points = [(x + self.x, y + self.y) for x, y in self.points]
            mousepos = pygame.mouse.get_pos()
            if self.texture:
                pygame.gfxdraw.textured_polygon(self.game.screen, self.points, self.texture, mousepos[0], -mousepos[1])
            else:
                pygame.gfxdraw.filled_polygon(self.game.screen, self.points, self.color)
            self.update_rect()

    def move(self):
        # code for moving object with mouse
        self.mousepos = pygame.mouse.get_pos()

        # Calculate the average position of the object's vertices
        center_x = sum(x for x, _ in self.points) / len(self.points)
        center_y = sum(y for _, y in self.points) / len(self.points)

        # Update the position based on the mouse cursor
        self.x = self.mousepos[0] - center_x
        self.y = self.mousepos[1] - center_y


        # Assuming self.transparent_surface is a surface with transparency
        # Blit the rotated image with transparency
        if self.image:
            rotated_image = rotate(self.image, -self.angle)
            image_rect = rotated_image.get_rect(center=(self.x + center_x, self.y + center_y))
            self.game.screen.blit(rotated_image, image_rect.topleft)
            # Draw the rotated lines without transparency
            rotated_points = self.rotate_points(self.points, self.angle)
            self.points = [(x + self.x, y + self.y) for x, y in rotated_points]
            self.update_rect()
        else:

            mousepos = pygame.mouse.get_pos()
            if self.texture:
                pygame.gfxdraw.textured_polygon(self.game.screen, self.points, self.texture, mousepos[0], -mousepos[1])
            else:
                pygame.gfxdraw.filled_polygon(self.game.screen, self.points, self.color)
    def drawoutline(self):
        # Draw an outline around the object
        pygame.gfxdraw.aapolygon(self.game.screen, self.points, (255, 255, 255))
        if settings['DEBUG'] == "True":
            pygame.draw.rect(self.game.screen, (255, 255, 0), self.rect, 2) # draw object hitbox

    def checkifclicked(self, mousepos):
        # Check if the object is clicked
        mask_surface = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
        pygame.gfxdraw.filled_polygon(mask_surface, self.points, (255, 255, 255))

        if mask_surface.get_at((int(mousepos[0]), int(mousepos[1])))[3] != 0:
            if self.on == 1:
                self.on = 0
            else:
                self.on = 1

    def selected(self, mousepos):
        mask_surface = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
        pygame.gfxdraw.filled_polygon(mask_surface, self.points, (255, 255, 255))

        if mask_surface.get_at((int(mousepos[0]), int(mousepos[1])))[3] != 0:
            if self.game.selected_object is not None and self.game.selected_object != self:
                self.game.selected_object.selectedtrue = False  # Deselect the currently selected object

            if not self.selectedtrue:
                self.selectedtrue = True
                self.game.selected_object = self  # Set this object as the currently selected object
                sounds.selected_sound()
            else:
                self.selectedtrue = False
                self.game.selected_object = None  # No object is selected now
                if type(self) == Flashlight:
                    sounds.laser_sound()
                else:
                    sounds.placed_sound()

    def find_parameters(self):
        centerx = sum(x[0] for x in self.points) / len(self.points)
        centery = sum(y[1] for y in self.points) / len(self.points)

        self.parameters = {'x':centerx, 'y':centery, 'angle':self.angle}

        if type(self) == Flashlight:
            lazer_on = {'lazer': self.lazer}
            self.parameters.update(lazer_on)

        colors = {'red': self.color[0], 'green': self.color[1], 'blue': self.color[2]}

        self.parameters.update(colors)


    def change_parameters(self):
        self.find_parameters()

        window = mp.Parameters(self)

        try:
            d_angle = self.parameters['angle'] - self.angle
            self.adjust(self.parameters['x'], self.parameters['y'], d_angle)
            self.color = (self.parameters['red'], self.parameters['green'], self.parameters['blue'])
            self.lazer = self.parameters["lazer"]
            print('lazer: ', self.lazer)
        except:
            pass


class Mirror(GameObject):
    def __init__(self, game, points, color, angle, islighting=False, image_path=None, texture = None):
        super().__init__(game, points, color, angle, image_path, texture)

class Prism(GameObject):
    def __init__(self, game, points, color, angle, islighting=False, image_path=None, texture = None):
        super().__init__(game, points, color, angle, image_path, texture)

class ColoredGlass(GameObject):
    def __init__(self, game, points, color, angle, islighting=False, image_path=None, texture = None):
        super().__init__(game, points, color, angle, image_path, texture)

# class oldFlashlight(GameObject):
#     def __init__(self, game, points, color, angle, islighting=True, image=None):
#         super().__init__(game, points, color, angle, image)
#         self.islighting = bool(islighting)
#         self.light = None
#         self.light_width = 8
#         self.color = color
#         self.angle = angle
#         self.image = image if image else None
#
#     def render(self):
#         super().render()
#         if self.islighting:
#             if self.on:
#                 # Calculate the starting point of the light from the center of the rotated rectangle/surface
#                 center_x = sum(x for x, _ in self.points) / len(self.points)
#                 center_y = sum(y for _, y in self.points) / len(self.points)
#                 self.light_adjust(center_x, center_y)
#
#                 self.light = light.Light(self.game,
#                                          [[self.light_start_x, self.light_start_y]],
#                                          self.color, -1*self.angle, self.light_width)
#
#                 #if up arrow clicked, color goes random
#                 if pygame.key.get_pressed()[pygame.K_UP]:
#                     self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
#
#                 self.light.trace_path2()
#                 self.placed = True
#                 light.Light.render(self.light)
#                 super().render()
#
#             elif not self.on:
#                 self.light = None
#
#
#     def light_adjust(self, center_x, center_y):
#         self.light_start_x = center_x
#         self.light_start_y = center_y
#         # Adjust the flashlight light position and direction
#         direction_vector = (self.points[0][0] - center_x, self.points[0][1] - center_y)
#
#         # Calculate the length of the direction vector
#         length = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)
#
#         # Check if the length is not zero before normalizing
#         if length != 0:
#             # Normalize the direction vector
#             normalized_direction = (direction_vector[0] / length, direction_vector[1] / length)
#
#             # Calculate the end point of the light
#             self.light_end_x = center_x + normalized_direction[0] * 1000
#             self.light_end_y = center_y + normalized_direction[1] * 1000
#
#             # Calculate the angle between the normalized direction and the x-axis
#             # self.angle = math.degrees(math.atan2(normalized_direction[1], normalized_direction[0]))
#
#
#

class Flashlight(GameObject):  # Inheriting from GameObject
    def __init__(self, game, points, color, angle, islighting=True, image=None):
        super().__init__(game, points, color, angle, image)
        self.islighting = bool(islighting)
        self.light = None
        self.light_width = 8
        self.color = color
        self.angle = angle
        self.image = image if image else None
        self.lazer = False

    def render(self):
        if not self.lazer:
            super().render()
            if self.islighting:
                #surface = pygame.surface.Surface(self.game.screen.get_size()).convert_alpha()
                #surface.fill([0, 0, 0, 0])
                if self.on:
                    ray_angle = self.angle - HALF_FOV + 0.0001
                    # Calculate the starting point of the light from the center of the rotated rectangle/surface
                    center_x = sum(x for x, _ in self.points) / len(self.points)
                    center_y = sum(y for _, y in self.points) / len(self.points)
                    self.light_adjust(center_x, center_y)
                    # if up arrow clicked, color goes random
                    if pygame.key.get_pressed()[pygame.K_UP]:
                        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    for ray in range(NUM_RAYS):
                        # self.light = light.Light(self.game,
                        #                          [[self.light_start_x, self.light_start_y]],
                        #                          self.color, -1*self.angle, self.light_width)
                        self.light = light.Light(self.game,
                                                 [[self.light_start_x, self.light_start_y]],
                                                 self.color, -1 * ray_angle, self.light_width, alpha=40)
                        self.light.angle = -1 * ray_angle

                        self.light.trace_path2()
                        self.placed = True
                        # self.light = light.Light(self.game, ((self.light_start_x, self.light_start_y), (self.light_end_x, self.light_end_y)),"white", self.angle, self.light_width)

                        # Render the light before blitting the rotated surface
                        #light.Light.render(self.light, surface)
                        light.Light.render(self.light)
                        #self.game.objects.remove(self.light)
                        ray_angle += DELTA_ANGLE
                    super().render()
                    #self.game.screen.blit(surface, (0, 0))

                elif not self.on:
                    self.light = None
        else:
            super().render()
            if self.islighting:
                if self.on:
                    # Calculate the starting point of the light from the center of the rotated rectangle/surface
                    center_x = sum(x for x, _ in self.points) / len(self.points)
                    center_y = sum(y for _, y in self.points) / len(self.points)
                    self.light_adjust(center_x, center_y)

                    self.light = light.Light(self.game,
                                             [[self.light_start_x, self.light_start_y]],
                                             self.color, -1 * self.angle, self.light_width)

                    # if up arrow clicked, color goes random
                    if pygame.key.get_pressed()[pygame.K_UP]:
                        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                    self.light.trace_path2()
                    self.placed = True
                    light.Light.render(self.light)
                    super().render()

                elif not self.on:
                    self.light = None


    def light_adjust(self, center_x, center_y):
        if not self.lazer:
            self.light_start_x = center_x
            self.light_start_y = center_y
            # Adjust the flashlight light position and direction
            direction_vector = (self.points[0][0] - center_x, self.points[0][1] - center_y)

            # Calculate the length of the direction vector
            length = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)

            # Check if the length is not zero before normalizing
            if length != 0:
                # Normalize the direction vector
                normalized_direction = (direction_vector[0] / length, direction_vector[1] / length)

                # Calculate the end point of the light
                self.light_end_x = center_x + normalized_direction[0] * 1000
                self.light_end_y = center_y + normalized_direction[1] * 1000

                # Calculate the angle between the normalized direction and the x-axis
                # self.angle = math.degrees(math.atan2(normalized_direction[1], normalized_direction[0]))
        else:
            self.light_start_x = center_x
            self.light_start_y = center_y
            # Adjust the flashlight light position and direction
            direction_vector = (self.points[0][0] - center_x, self.points[0][1] - center_y)

            # Calculate the length of the direction vector
            length = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)

            # Check if the length is not zero before normalizing
            if length != 0:
                # Normalize the direction vector
                normalized_direction = (direction_vector[0] / length, direction_vector[1] / length)

                # Calculate the end point of the light
                self.light_end_x = center_x + normalized_direction[0] * 1000
                self.light_end_y = center_y + normalized_direction[1] * 1000

                # Calculate the angle between the normalized direction and the x-axis
                # self.angle = math.degrees(math.atan2(normalized_direction[1], normalized_direction[0]))
