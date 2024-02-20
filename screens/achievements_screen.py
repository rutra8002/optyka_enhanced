import pygame
import sqlite3
import classes.font
from classes import parkinson as particles
from classes import sounds
import random
from gui import button
from gui.button_animation import ButtonAnimation

class AchievementsScreen:
    def __init__(self, game):
        self.game = game
        self.width = self.game.width
        self.height = self.game.height
        self.screen = self.game.screen
        self.objects = []
        self.font = pygame.font.Font(None, 24)  # Adjust the font size as needed
        self.achievements = []
        self.load_achievements()
        self.particle_system = particles.UnityParticleSystem()

        back = button.ButtonForgame(71, self)
        self.back_animation = ButtonAnimation(back, back.rect.x*6+(back.width//2), back.rect.y)

        self.game.objects.append(self)

    def checkevent(self, pos):
        for object in self.objects:
            object.checkcollision(pos)

    def load_achievements(self):
        try:
            conn = sqlite3.connect('achievements.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM achievements")
            self.achievements = cursor.fetchall()
            conn.close()
        except:
            print("Error: Could not load achievements from the database.")

    def generate_particles(self):
        # Adjust the parameters as needed
        self.particle_system.add_particle(
            x=random.randint(0, self.width),
            y=random.randint(0, self.height),
            vx=random.uniform(-0.1, 0.1),
            vy=random.uniform(-0.1, 0.1),
            lifespan=1000,
            size=random.randint(1, 2),
            red=random.randint(150, 255),
            green=random.randint(150, 255),
            blue=random.randint(150, 255),
            alpha=100,
            shape='circle'
        )

    def render(self):
        self.generate_particles()
        self.particle_system.update()
        self.particle_system.draw(self.screen)
        font = pygame.font.Font(classes.font.Font, self.game.width // 30)

        text = font.render('Achievements', True, (255, 255, 255))

        text_rect = text.get_rect()

        text_rect.centerx = self.game.screen.get_rect().centerx
        self.game.screen.blit(text, text_rect)
        text_rect.y = 10

        midpoint = len(self.achievements) // 2

        y_offset1 = 100
        y_offset2 = 100

        for achievement in self.achievements[:midpoint]:
            y_offset1 = self.render_achievement(achievement, 50, y_offset1)

        for achievement in self.achievements[midpoint:]:
            y_offset2 = self.render_achievement(achievement, self.game.width // 2, y_offset2)

        self.back_animation.animate()
        for object in self.objects:
            object.render()

    def render_achievement(self, achievement, x_offset, y_offset):
        achievement_name, unlocked, rarity = achievement
        if rarity == 'common':
            color = (200, 200, 200)
        elif rarity == 'uncommon':
            color = (100, 200, 0)
        elif rarity == 'rare':
            color = (25, 65, 120)
        elif rarity == 'epic':
            color = (83, 0, 135)
        elif rarity == 'legendary':
            color = (247, 247, 2)
        else:
            color = (50, 50, 50)
        text_color = tuple(255 - c for c in color)
        text_surface = self.font.render(f"{achievement_name} - {rarity}", True, text_color)

        rect_width = self.width // 2 - 100
        rect_height = 50

        text_rect = pygame.Rect(x_offset, y_offset, rect_width, rect_height)

        # Calculate the center of the rectangle
        center_x = x_offset + rect_width // 2
        center_y = y_offset + rect_height // 2

        text_surface_rect = text_surface.get_rect(center=(center_x, center_y))

        pygame.draw.rect(self.game.screen, color, text_rect.inflate(10, 10), 0, 5)
        self.game.screen.blit(text_surface, text_surface_rect)
        return y_offset + rect_height + 20
