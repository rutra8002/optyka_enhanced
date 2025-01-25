import pygame
import os
from gui.button import ButtonForgame
from gui.button_animation import ButtonAnimation

class Save:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.height = game.height
        self.width = game.width
        self.objects = game.objects
        self.font = pygame.font.Font(None, 36)
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False
        self.text = game.save_title if game.save_title else ''
        self.done = False

        self.clock = pygame.time.Clock()

        # Buttons
        self.save_button = ButtonForgame(101, self)
        self.dont_save_button = ButtonForgame(102, self)
        self.cancel_button = ButtonForgame(103, self)

        # Button Animations
        self.save_button_animation = ButtonAnimation(self.save_button, 100, 200)
        self.dont_save_button_animation = ButtonAnimation(self.dont_save_button, 100, 300)
        self.cancel_button_animation = ButtonAnimation(self.cancel_button, 100, 400)

        # Enable key repeat
        pygame.key.set_repeat(500, 50)

    def run(self):
        while not self.done:
            self.clock.tick(self.game.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.active = not self.active
                    else:
                        self.active = False
                    self.color = self.color_active if self.active else self.color_inactive

                    # Check button clicks
                    self.save_button.checkcollision(event.pos)
                    self.dont_save_button.checkcollision(event.pos)
                    self.cancel_button.checkcollision(event.pos)

                if event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_RETURN:
                            self.save()
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode

            self.screen.fill((0, 0, 0))
            txt_surface = self.font.render(self.text, True, self.color)
            width = max(200, txt_surface.get_width() + 10)
            self.input_box.w = width
            self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
            pygame.draw.rect(self.screen, self.color, self.input_box, 2)

            # Render buttons
            self.save_button.render()
            self.dont_save_button.render()
            self.cancel_button.render()

            # Animate buttons
            self.save_button_animation.animate()
            self.dont_save_button_animation.animate()
            self.cancel_button_animation.animate()

            # Draw instruction text
            instruction_text = self.font.render("Enter save name:", True, (255, 255, 255))
            self.screen.blit(instruction_text, (100, 50))

            pygame.display.flip()

    def save(self):
        save_title = self.text.strip()
        if save_title != '':
            save_title = save_title.replace(' ', "_")
            self.old_save_title = self.game.save_title
            self.game.save_title = save_title

            self.dir = "saves"
            self.saves_files = [file[:-5] for file in os.listdir(self.dir) if file.endswith('.json')]

            if self.game.save_title in self.saves_files and self.game.save_title != self.old_save_title:
                print("Error: You cannot save your game with the same name as another save file.")
            else:
                self.game.save_to_file()
                self.done = True

    def cancel(self):
        self.done = True
        self.game.cancel = True
        self.objects.remove(self.save_button)
        self.objects.remove(self.dont_save_button)
        self.objects.remove(self.cancel_button)