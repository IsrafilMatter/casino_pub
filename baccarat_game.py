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


# colors, and betting amounts
# Set up file directories for assets and data
# GUI Setup 
# Defining BaccaratGame class inheriting from CasinoGame
# Main entry