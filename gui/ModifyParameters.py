import pygame
from classes.font import Font


class Parameters:
    def __init__(self, obj):
        self.object = obj
        self.game = obj.game
        self.screen = self.game.screen
        self.parameters_dict = self.object.parameters

        self.fields = []
        self.active_input = None
        self.dragging_slider = None
        self.error_message = ""

        self.font = pygame.font.Font(Font, max(14, self.game.height // 40))
        self.small_font = pygame.font.Font(Font, max(12, self.game.height // 50))

        self.panel_width = 460
        self.row_height = 36
        self.padding = 16
        self.button_height = 32
        self._build_fields()
        self._layout()

        self.game.parameters_overlay = self

    def _build_fields(self):
        for param in self.parameters_dict:
            if param in ('points', 'curvature_radius', 'curvature_radius_2'):
                continue

            if param in ('red', 'green', 'blue'):
                self.fields.append(
                    {
                        "key": param,
                        "type": "slider",
                        "label": self._label_for_param(param),
                        "min": 0,
                        "max": 255,
                        "value": int(self.parameters_dict[param]),
                    }
                )
                continue

            if param == 'lazer':
                self.fields.append(
                    {
                        "key": param,
                        "type": "toggle",
                        "label": self._label_for_param(param),
                        "value": bool(self.parameters_dict[param]),
                    }
                )
                continue

            if param == 'transmittance':
                self.fields.append(
                    {
                        "key": param,
                        "type": "slider",
                        "label": self._label_for_param(param),
                        "min": 0,
                        "max": 100,
                        "value": int(self.parameters_dict[param] * 100),
                    }
                )
                continue

            if param == 'absorbsion_factor':
                self.fields.append(
                    {
                        "key": param,
                        "type": "slider",
                        "label": self._label_for_param(param),
                        "min": 0,
                        "max": 100,
                        "value": int(self.parameters_dict[param] * 100),
                    }
                )
                continue

            text_value = str(self.parameters_dict[param])
            if param == 'size':
                text_value = f"{self.parameters_dict[param] * 100}%"

            self.fields.append(
                {
                    "key": param,
                    "type": "input",
                    "label": self._label_for_param(param),
                    "text": text_value,
                }
            )

    def _layout(self):
        total_rows = len(self.fields)
        panel_height = (
            self.padding * 3
            + total_rows * self.row_height
            + self.button_height
            + self.small_font.get_height()
        )
        panel_x = (self.game.width - self.panel_width) // 2
        panel_y = (self.game.height - panel_height) // 2
        self.panel_rect = pygame.Rect(panel_x, panel_y, self.panel_width, panel_height)

        for idx, field in enumerate(self.fields):
            row_y = self.panel_rect.y + self.padding + idx * self.row_height
            label_rect = pygame.Rect(self.panel_rect.x + self.padding, row_y, 180, self.row_height)
            value_rect = pygame.Rect(self.panel_rect.x + 200, row_y + 6, 200, self.row_height - 12)
            field["label_rect"] = label_rect
            field["value_rect"] = value_rect

        button_y = self.panel_rect.bottom - self.padding - self.button_height
        self.apply_button_rect = pygame.Rect(
            self.panel_rect.right - self.padding - 200,
            button_y,
            90,
            self.button_height,
        )
        self.cancel_button_rect = pygame.Rect(
            self.panel_rect.right - self.padding - 100,
            button_y,
            90,
            self.button_height,
        )

    def _label_for_param(self, param):
        if param == 'absorbsion_factor':
            return "Absorption"
        if param == 'transmittance':
            return "Transmittance"
        if param == 'lazer':
            return "Laser"
        return param.capitalize()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.apply_button_rect.collidepoint(event.pos):
                    self.apply()
                    return
                if self.cancel_button_rect.collidepoint(event.pos):
                    self.close()
                    return

                self.active_input = None
                for field in self.fields:
                    if field["value_rect"].collidepoint(event.pos):
                        if field["type"] == "input":
                            self.active_input = field
                            return
                        if field["type"] == "toggle":
                            field["value"] = not field["value"]
                            return
                        if field["type"] == "slider":
                            self.dragging_slider = field
                            self._update_slider_value(field, event.pos[0])
                            return
            return

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = None
            return

        if event.type == pygame.MOUSEMOTION and self.dragging_slider:
            self._update_slider_value(self.dragging_slider, event.pos[0])
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return
            if event.key == pygame.K_RETURN and self.active_input is None:
                self.apply()
                return
            if self.active_input is not None:
                self._handle_input_key(event)

    def _handle_input_key(self, event):
        text = self.active_input["text"]
        if event.key == pygame.K_BACKSPACE:
            self.active_input["text"] = text[:-1]
            return
        if event.key == pygame.K_RETURN:
            self.active_input = None
            return
        if event.unicode and self._is_allowed_input(event.unicode):
            self.active_input["text"] = text + event.unicode

    def _is_allowed_input(self, char):
        return char.isdigit() or char in (".", "-", "%")

    def _update_slider_value(self, field, mouse_x):
        slider_rect = field["value_rect"]
        ratio = (mouse_x - slider_rect.x) / max(1, slider_rect.width)
        ratio = max(0.0, min(1.0, ratio))
        field["value"] = int(field["min"] + (field["max"] - field["min"]) * ratio)

    def apply(self):
        self.error_message = ""
        new_parameters = {}

        for field in self.fields:
            if field["type"] == "slider":
                if field["key"] in ("transmittance", "absorbsion_factor"):
                    new_parameters[field["key"]] = field["value"] / 100
                else:
                    new_parameters[field["key"]] = int(field["value"])
            elif field["type"] == "toggle":
                new_parameters[field["key"]] = bool(field["value"])

        for field in self.fields:
            if field["type"] != "input":
                continue
            key = field["key"]
            try:
                value = self._parse_input_value(key, field["text"])
            except ValueError as exc:
                self.error_message = str(exc)
                return
            new_parameters[key] = value

        if "transmittance" in new_parameters or "absorbsion_factor" in new_parameters:
            transmittance = new_parameters.get("transmittance", self.parameters_dict.get("transmittance", 0))
            absorbsion = new_parameters.get("absorbsion_factor", self.parameters_dict.get("absorbsion_factor", 0))
            if transmittance < 0 or absorbsion < 0 or transmittance + absorbsion > 1:
                self.error_message = "Transmittance + absorption must be between 0% and 100%."
                return

        if self.parameters_dict.get("points") is not None:
            new_parameters["points"] = self.parameters_dict["points"]

        self.object.parameters.update(new_parameters)
        self.object.change_parameters("overlay")
        self.close()

    def _parse_input_value(self, key, text):
        if key == "size":
            cleaned = text.strip().replace("%", "")
            value = float(cleaned) / 100
            if value <= 0:
                raise ValueError("Size cannot be below or equal to 0%.")
            return value
        if key == "refraction index":
            value = float(text)
            return max(1.0, min(2.0, value))
        return float(text)

    def close(self):
        if self.game.parameters_overlay == self:
            self.game.parameters_overlay = None

    def render(self):
        overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, (30, 30, 30), self.panel_rect, 0, 8)
        pygame.draw.rect(self.screen, (220, 220, 220), self.panel_rect, 2, 8)

        title_surface = self.font.render("Enter Parameters", True, (255, 255, 255))
        self.screen.blit(title_surface, (self.panel_rect.x + self.padding, self.panel_rect.y + 8))

        for field in self.fields:
            label_surface = self.small_font.render(field["label"], True, (200, 200, 200))
            self.screen.blit(label_surface, (field["label_rect"].x, field["label_rect"].y + 8))

            if field["type"] == "input":
                is_active = self.active_input == field
                color = (255, 255, 255) if is_active else (180, 180, 180)
                pygame.draw.rect(self.screen, (50, 50, 50), field["value_rect"], 0, 4)
                pygame.draw.rect(self.screen, color, field["value_rect"], 2, 4)
                text_surface = self.small_font.render(field["text"], True, (255, 255, 255))
                self.screen.blit(text_surface, (field["value_rect"].x + 6, field["value_rect"].y + 6))

            elif field["type"] == "toggle":
                pygame.draw.rect(self.screen, (50, 50, 50), field["value_rect"], 0, 12)
                knob_x = field["value_rect"].x + (field["value_rect"].width - 20 if field["value"] else 4)
                knob_color = (188, 149, 26) if field["value"] else (169, 169, 169)
                pygame.draw.circle(self.screen, knob_color, (knob_x + 8, field["value_rect"].centery), 8)

            elif field["type"] == "slider":
                pygame.draw.rect(self.screen, (60, 60, 60), field["value_rect"], 0, 4)
                slider_ratio = (field["value"] - field["min"]) / max(1, field["max"] - field["min"])
                knob_x = field["value_rect"].x + int(slider_ratio * field["value_rect"].width)
                pygame.draw.circle(self.screen, (220, 220, 220), (knob_x, field["value_rect"].centery), 7)
                value_text = self.small_font.render(str(field["value"]), True, (255, 255, 255))
                self.screen.blit(value_text, (field["value_rect"].right + 6, field["value_rect"].y + 4))

        if self._has_color_fields():
            color = self._current_color()
            preview_rect = pygame.Rect(self.panel_rect.right - 60, self.panel_rect.y + 20, 40, 40)
            pygame.draw.rect(self.screen, color, preview_rect, 0, 4)
            pygame.draw.rect(self.screen, (255, 255, 255), preview_rect, 2, 4)

        pygame.draw.rect(self.screen, (70, 120, 70), self.apply_button_rect, 0, 6)
        pygame.draw.rect(self.screen, (200, 200, 200), self.apply_button_rect, 2, 6)
        apply_text = self.small_font.render("Apply", True, (255, 255, 255))
        self.screen.blit(apply_text, apply_text.get_rect(center=self.apply_button_rect.center))

        pygame.draw.rect(self.screen, (120, 70, 70), self.cancel_button_rect, 0, 6)
        pygame.draw.rect(self.screen, (200, 200, 200), self.cancel_button_rect, 2, 6)
        cancel_text = self.small_font.render("Cancel", True, (255, 255, 255))
        self.screen.blit(cancel_text, cancel_text.get_rect(center=self.cancel_button_rect.center))

        if self.error_message:
            error_surface = self.small_font.render(self.error_message, True, (255, 80, 80))
            self.screen.blit(
                error_surface,
                (self.panel_rect.x + self.padding, self.panel_rect.bottom - self.button_height - self.padding - 18),
            )

    def _has_color_fields(self):
        return all(self._get_field(key) is not None for key in ("red", "green", "blue"))

    def _current_color(self):
        red = self._get_field_value("red", 255)
        green = self._get_field_value("green", 255)
        blue = self._get_field_value("blue", 255)
        return (int(red), int(green), int(blue))

    def _get_field(self, key):
        for field in self.fields:
            if field["key"] == key:
                return field
        return None

    def _get_field_value(self, key, default):
        field = self._get_field(key)
        if field is None:
            return default
        if field["type"] == "slider":
            return field["value"]
        return default
