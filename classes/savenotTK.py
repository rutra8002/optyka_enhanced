import pygame
import os

class Save:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.Font(None, 36)
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False
        self.text = ''
        self.done = False

        # Buttons
        self.save_button = pygame.Rect(100, 200, 100, 50)
        self.dont_save_button = pygame.Rect(250, 200, 150, 50)
        self.cancel_button = pygame.Rect(450, 200, 100, 50)

    def run(self):
        while not self.done:
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
                    if self.save_button.collidepoint(event.pos):
                        self.save()
                    elif self.dont_save_button.collidepoint(event.pos):
                        self.done = True
                    elif self.cancel_button.collidepoint(event.pos):
                        self.cancel()

                if event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_RETURN:
                            self.save()
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode

            self.screen.fill((30, 30, 30))
            txt_surface = self.font.render(self.text, True, self.color)
            width = max(200, txt_surface.get_width() + 10)
            self.input_box.w = width
            self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
            pygame.draw.rect(self.screen, self.color, self.input_box, 2)

            # Draw buttons
            pygame.draw.rect(self.screen, (0, 255, 0), self.save_button)
            pygame.draw.rect(self.screen, (255, 0, 0), self.dont_save_button)
            pygame.draw.rect(self.screen, (255, 255, 0), self.cancel_button)

            # Draw button text
            save_text = self.font.render("Save", True, (0, 0, 0))
            dont_save_text = self.font.render("Don't Save", True, (0, 0, 0))
            cancel_text = self.font.render("Cancel", True, (0, 0, 0))
            self.screen.blit(save_text, (self.save_button.x + 10, self.save_button.y + 10))
            self.screen.blit(dont_save_text, (self.dont_save_button.x + 10, self.dont_save_button.y + 10))
            self.screen.blit(cancel_text, (self.cancel_button.x + 10, self.cancel_button.y + 10))

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