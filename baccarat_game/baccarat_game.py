# Baccarat Casino Game
# Israfil Palabay
# 2025-06-24

# Import necessary libraries for graphics, sound, system, data, and game logic
import pygame
import random
import sys
import os
import json
import time
import webbrowser
from typing import List, Tuple, Dict, Optional
from casino_game import CasinoGame

# Initialization
pygame.init()

# Initialize the Pygame mixer for sound effects
pygame.mixer.init()

# Set up the main window size and card sizes
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CARD_WIDTH = 100
CARD_HEIGHT = 140
HOLE_RADIUS = 50
CORNER_RADIUS = 20
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SAVES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")

# Create directories if they do not exist
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(SAVES_DIR, exist_ok=True)

# Save file paths
SAVE_FILES = [os.path.join(SAVES_DIR, f"save{i}.json") for i in range(1, 4)]

# Betting amounts
BET_AMOUNTS = [5, 10, 20, 40, 50, 80, 100, 200, 300, 500, 1000, 5000, 10000]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
GOLD = (212, 175, 55)
GRAY = (128, 128, 128)
TRANSPARENT = (0, 0, 0, 128)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)

# Game states
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
BETTING = "betting"
SAVE_MENU = "save_menu"
LOAD_MENU = "load_menu"

# GUI Setup 
class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.active = True

    def draw(self, surface):
        pygame.draw.rect(surface, self.color if self.active else GRAY, self.rect)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.active:
                return True
        return False
class BetbButton:
    def __init__(self, x: int, y: int, width: int, height: int, amount: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.amount = amount
        self.color = GOLD
        self.active = True

    def draw(self, surface):
        pygame.draw.rect(surface, self.color if self.active else GRAY, self.rect)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(f"${self.amount}", True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.active:
                return True
        return False
class Confetti:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice([(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)])
        self.size = random.randint(5, 10)
        self.speed_y = random.randint(2, 6)
        self.speed_x = random.randint(-3, 3)
        self.angle = random.randint(0, 360)
        self.angle_speed = random.randint(-5, 5)

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.angle += self.angle_speed
        return self.y < WINDOW_HEIGHT

    def draw(self, screen):
        surface = pygame.Surface((self.size, self.size))
        surface.fill(self.color)
        rotated_surface = pygame.transform.rotate(surface, self.angle)
        screen.blit(rotated_surface, (self.x - rotated_surface.get_width()//2, 
                                    self.y - rotated_surface.get_height()//2))
class Menu:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buttons = {
            'start': Button(width//2 - 100, height//2 - 60, 200, 50, "Start Game", GREEN),
            'continue': Button(width//2 - 100, height//2 - 60, 200, 50, "Continue", GREEN),
            'exit': Button(width//2 - 100, height//2 + 70, 200, 50, "Exit", RED),
            'save': Button(width//2 - 100, height//2 - 130, 200, 50, "Save Game", GOLD),
            'load': Button(width//2 - 100, height//2 + 10, 200, 50, "Load Game", GOLD),
            'save1': Button(width//2 - 100, height//2 - 130, 200, 50, "Save Game 1", GOLD),
            'save2': Button(width//2 - 100, height//2 - 70, 200, 50, "Save Game 2", GOLD),
            'save3': Button(width//2 - 100, height//2 - 10, 200, 50, "Save Game 3", GOLD),
            'load1': Button(width//2 - 100, height//2 - 130, 200, 50, "Load Game 1", GOLD),
            'load2': Button(width//2 - 100, height//2 - 70, 200, 50, "Load Game 2", GOLD),
            'load3': Button(width//2 - 100, height//2 - 10, 200, 50, "Load Game 3", GOLD),
            'back': Button(width//2 - 100, height//2 + 70, 200, 50, "Back", GRAY),
            'main_menu': Button(width//2 - 100, height//2 + 70, 200, 50, "Main Menu", GRAY)
        }

    def draw(self, screen, state):
        # Draw semi-transparent background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*BLACK[:3], 128), (0, 0, self.width, self.height))
        screen.blit(overlay, (0, 0))

        # Draw title
        font = pygame.font.Font(None, 74)
        titles = {
            MENU: "Baccarat Casino",
            PAUSED: "Game Paused",
            SAVE_MENU: "Save Game",
            LOAD_MENU: "Load Game"
        }
        title = titles.get(state, "Baccarat Casino")
        title_surface = font.render(title, True, WHITE)
        screen.blit(title_surface, (self.width//2 - title_surface.get_width()//2, 100))

        # Draw buttons based on state
        if state == MENU:
            self.buttons['start'].draw(screen)
            self.buttons['load'].draw(screen)
            self.buttons['exit'].draw(screen)
        elif state == PAUSED:
            self.buttons['continue'].draw(screen)
            self.buttons['save'].draw(screen)
            self.buttons['load'].draw(screen)
            self.buttons['exit'].draw(screen)
            self.buttons['main_menu'].draw(screen)
        elif state == SAVE_MENU:
            self.buttons['save1'].draw(screen)
            self.buttons['save2'].draw(screen)
            self.buttons['save3'].draw(screen)
            self.buttons['back'].draw(screen)
        elif state == LOAD_MENU:
            self.buttons['load1'].draw(screen)
            self.buttons['load2'].draw(screen)
            self.buttons['load3'].draw(screen)
            self.buttons['back'].draw(screen)
class CardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            return {'suit': obj.suit, 'value': obj.value, 'numeric_value': obj.numeric_value}
        return super().default(obj)
class Card:
    def __init__(self, suit: str, value: str, numeric_value: int):
        self.suit = suit.lower()
        self.value = value
        self.numeric_value = numeric_value
        self.image = None
        self._load_image()

    def _load_image(self):
        value_map = {'A': 'ace', 'K': 'king', 'Q': 'queen', 'J': 'jack'}
        value_str = value_map.get(self.value, self.value)
        filename = f"{value_str}_of_{self.suit}.png"
        image_path = os.path.join(ASSETS_DIR, "cards", filename)
        
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
        except pygame.error:
            print(f"Error loading card image: {image_path}")
            self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.image.fill(WHITE)
            font = pygame.font.Font(None, 36)
            text = font.render(f"{self.value}{self.suit[0]}", True, BLACK)
            self.image.blit(text, (10, 10))

    def to_dict(self):
        return {
            'suit': self.suit,
            'value': self.value,
            'numeric_value': self.numeric_value
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['suit'], data['value'], data['numeric_value'])
    
# Defining BaccaratGame class inheriting from CasinoGame
# Main entry