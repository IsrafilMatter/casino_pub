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
# Defining BaccaratGame class inheriting from CasinoGame
# Main entry