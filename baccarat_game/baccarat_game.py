# Baccarat Casino Game
# Israfil Palabay
# 2025-06-24

import pygame
import random
import sys
import os
import json
import time
import webbrowser
from typing import List, Tuple, Dict, Optional
from casino_game import CasinoGame

# Initialize Pygame
pygame.init()

# Initialize pygame mixer
pygame.mixer.init()

# Constants
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

# Create directories if they don't exist
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

# Game States
MENU = 'menu'
PLAYING = 'playing'
PAUSED = 'paused'
BETTING = 'betting'
SAVE_MENU = 'save_menu'
LOAD_MENU = 'load_menu'

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

class BetButton:
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

class BaccaratGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = value

    def __init__(self, player_balance=1000):
        super().__init__(player_balance)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Baccarat Casino Simulator")
        self.menu = Menu(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.state = MENU
        
        # Create bet buttons
        self.bet_buttons = []
        button_width = 80
        button_height = 30
        button_margin = 10
        buttons_per_row = 7
        start_x = 20  
        start_y = 20  
        
        for i, amount in enumerate(BET_AMOUNTS):
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + (button_width + button_margin) * col
            y = start_y + (button_height + button_margin) * row
            self.bet_buttons.append(BetButton(x, y, button_width, button_height, amount))
        
        # Load background image
        try:
            self.background = pygame.image.load(os.path.join(ASSETS_DIR, "BaccaratTable.jpg"))
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
            
            # Load shoe image
            self.shoe_image = pygame.image.load(os.path.join(ASSETS_DIR, "SHOE-removebg-preview.png"))
            
            # Load win sound
            self.win_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "WIN sound effect no copyright.mp3"))
            
            # Load background music
            pygame.mixer.music.load(os.path.join(ASSETS_DIR, "Las Vegas Casino Music.mp3"))
            pygame.mixer.music.play(-1)
            
        except Exception as e:
            print(f"Error loading assets: {e}")
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.background.fill(GREEN)
        
        # Load poker chip images
        self.red_chip = pygame.image.load(os.path.join(ASSETS_DIR, "pokerchip1.png"))
        self.blue_chip = pygame.image.load(os.path.join(ASSETS_DIR, "pokerchip3.png"))
        self.yellow_chip = pygame.image.load(os.path.join(ASSETS_DIR, "pokerchip4.png"))
        self.current_chip = None
        
        self.reset_game()
        self.confetti = []
        self.show_confetti = False
        self.confetti_timer = 0
        self.current_save_slot = None
        self.game_results = []  # Track game results
        self.banker_hands = []  # Track banker hands for pair counting
        self.player_hands = []  # Track player hands for pair counting

    def reset_game(self):
        self.deck = self._create_deck()
        self.player_hand = []
        self.banker_hand = []
        self.player_score = 0
        self.banker_score = 0
        self.player_balance = 5000  
        self.current_bet = 0
        self.bet_on = "Banker"  # Default to Banker
        self.game_state = BETTING
        self.last_result = None
        self.last_win_amount = 0
        self.player_wins = 0
        self.banker_wins = 0
        self.ties = 0
        self.total_games = 0

    def reset_cards(self):
        self.deck = self._create_deck()
        self.player_hand = []
        self.banker_hand = []
        self.player_score = 0
        self.banker_score = 0
        self.game_state = BETTING
        self.last_result = None

    def save_game(self, slot: int):
        game_state = {
            'player_hand': [{'suit': card.suit, 'value': card.value, 'numeric_value': card.numeric_value} for card in self.player_hand],
            'banker_hand': [{'suit': card.suit, 'value': card.value, 'numeric_value': card.numeric_value} for card in self.banker_hand],
            'deck': [{'suit': card.suit, 'value': card.value, 'numeric_value': card.numeric_value} for card in self.deck],
            'player_score': self.player_score,
            'banker_score': self.banker_score,
            'current_bet': self.current_bet,
            'player_balance': self.player_balance,
            'bet_on': self.bet_on,
            'player_wins': self.player_wins,
            'banker_wins': self.banker_wins,
            'ties': self.ties,
            'total_games': self.total_games,
            'game_results': self.game_results,
            'banker_hands': self.banker_hands,
            'player_hands': self.player_hands
        }
        
        filename = SAVE_FILES[slot - 1]
        with open(filename, 'w') as f:
            json.dump(game_state, f, cls=CardEncoder)
            
        print(f"Game saved to slot {slot}")

    def load_game(self, slot: int):
        try:
            filename = SAVE_FILES[slot - 1]
            with open(filename, 'r') as f:
                game_state = json.load(f)
                
            # Reconstruct card objects
            self.player_hand = [Card(card['suit'], card['value'], card['numeric_value']) for card in game_state['player_hand']]
            self.banker_hand = [Card(card['suit'], card['value'], card['numeric_value']) for card in game_state['banker_hand']]
            self.deck = [Card(card['suit'], card['value'], card['numeric_value']) for card in game_state['deck']]
            
            # Load other game state
            self.player_score = game_state['player_score']
            self.banker_score = game_state['banker_score']
            self.current_bet = game_state['current_bet']
            self.player_balance = game_state.get('player_balance', 1000)  # Default to 1000 if not found in save
            self.bet_on = game_state.get('bet_on', 'Banker')  # Default to Banker if not found
            self.player_wins = game_state['player_wins']
            self.banker_wins = game_state['banker_wins']
            self.ties = game_state['ties']
            self.total_games = game_state['total_games']
            self.game_results = game_state.get('game_results', [])
            self.banker_hands = game_state.get('banker_hands', [])
            self.player_hands = game_state.get('player_hands', [])
            
            self.state = PLAYING
            print(f"Game loaded from slot {slot}")
            
        except FileNotFoundError:
            print(f"No save file found in slot {slot}")
        except json.JSONDecodeError:
            print(f"Error loading save file from slot {slot}")

    def calculate_win_percentages(self):
        if self.total_games == 0:
            return 0, 0, 0
        
        player_pct = (self.player_wins / self.total_games) * 100
        banker_pct = (self.banker_wins / self.total_games) * 100
        tie_pct = (self.ties / self.total_games) * 100
        
        return player_pct, banker_pct, tie_pct

    def draw_results_tracker(self):
        # Background for statistics - moved up with solid black background
        stats_rect = pygame.Rect(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 250, 280, 200)
        
        # Draw black background with border
        pygame.draw.rect(self.screen, BLACK, stats_rect)
        pygame.draw.rect(self.screen, GOLD, stats_rect, 2)  # Gold border
        
        # Draw title with larger font and centered
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("SCOREBOARD", True, GOLD)
        title_rect = title.get_rect(centerx=stats_rect.centerx, top=stats_rect.top + 10)
        self.screen.blit(title, title_rect)
        
        # Calculate statistics
        total_games = self.total_games
        banker_wins = self.banker_wins
        player_wins = self.player_wins
        ties = self.ties
        
        # Calculate percentages
        banker_percent = (banker_wins / total_games * 100) if total_games > 0 else 0
        player_percent = (player_wins / total_games * 100) if total_games > 0 else 0
        tie_percent = (ties / total_games * 100) if total_games > 0 else 0
        
        # Draw statistics with improved layout
        stats_font = pygame.font.Font(None, 28)
        y_start = stats_rect.top + 50
        line_height = 30
        
        # Draw divider line under title
        pygame.draw.line(self.screen, GOLD, 
                        (stats_rect.left + 10, y_start - 10),
                        (stats_rect.right - 10, y_start - 10), 2)
        
        # Function to draw stat line with count and percentage
        def draw_stat_line(text, count, percentage, color, y_pos):
            # Draw label
            label = stats_font.render(text, True, WHITE)
            self.screen.blit(label, (stats_rect.left + 20, y_pos))
            
            # Draw count and percentage
            count_text = f"{count:,} ({percentage:.1f}%)"
            count_surface = stats_font.render(count_text, True, color)
            self.screen.blit(count_surface, (stats_rect.right - count_surface.get_width() - 20, y_pos))
        
        # Draw statistics lines
        draw_stat_line("Banker:", banker_wins, banker_percent, RED, y_start)
        draw_stat_line("Player:", player_wins, player_percent, BLUE, y_start + line_height)
        draw_stat_line("Tie:", ties, tie_percent, GREEN, y_start + line_height * 2)
        
        # Draw divider line before total
        pygame.draw.line(self.screen, GOLD, 
                        (stats_rect.left + 10, y_start + line_height * 3),
                        (stats_rect.right - 10, y_start + line_height * 3), 2)
        
        # Draw total games with slightly larger font
        total_font = pygame.font.Font(None, 30)
        total_label = total_font.render("Total Games:", True, GOLD)
        total_count = total_font.render(f"{total_games:,}", True, GOLD)
        
        self.screen.blit(total_label, (stats_rect.left + 20, y_start + line_height * 3.3))
        self.screen.blit(total_count, (stats_rect.right - total_count.get_width() - 20, y_start + line_height * 3.3))

    def draw_game(self):
        self.screen.blit(self.background, (0, 0))
        
        # Draw shoe image in the red box area (upper left of playing area)
        shoe_x = 180  # Moved more to the right (was 150)
        shoe_y = 120  # Position to match red box
        shoe_width = 120  # Adjust size to fit the red box
        shoe_height = 120
        
        # Scale shoe image to fit the red box
        scaled_shoe = pygame.transform.scale(self.shoe_image, (shoe_width, shoe_height))
        self.screen.blit(scaled_shoe, (shoe_x, shoe_y))
        
        if self.state == PLAYING:
            # Draw game board
            font = pygame.font.Font(None, 36)
            center_x = WINDOW_WIDTH // 2
            
            # Calculate card positions to be centered
            banker_y = 200
            player_y = 400
            
            # Center the cards horizontally
            player_start_x = center_x - ((CARD_WIDTH + 10) * len(self.player_hand)) // 2 if self.player_hand else center_x - CARD_WIDTH - 5
            banker_start_x = center_x - ((CARD_WIDTH + 10) * len(self.banker_hand)) // 2 if self.banker_hand else center_x - CARD_WIDTH - 5

            # Draw empty card outlines if no cards dealt
            if not self.player_hand:
                # Draw two empty card outlines centered
                pygame.draw.rect(self.screen, WHITE, (player_start_x, player_y, CARD_WIDTH, CARD_HEIGHT), 2)
                pygame.draw.rect(self.screen, WHITE, (player_start_x + CARD_WIDTH + 10, player_y, CARD_WIDTH, CARD_HEIGHT), 2)
            if not self.banker_hand:
                pygame.draw.rect(self.screen, WHITE, (banker_start_x, banker_y, CARD_WIDTH, CARD_HEIGHT), 2)
                pygame.draw.rect(self.screen, WHITE, (banker_start_x + CARD_WIDTH + 10, banker_y, CARD_WIDTH, CARD_HEIGHT), 2)

            # Draw cards
            for i, card in enumerate(self.player_hand):
                card_x = player_start_x + i * (CARD_WIDTH + 10)
                self.screen.blit(card.image, (card_x, player_y))

            for i, card in enumerate(self.banker_hand):
                card_x = banker_start_x + i * (CARD_WIDTH + 10)
                self.screen.blit(card.image, (card_x, banker_y))

            # Draw scores
            player_text = font.render(f"Player (Score: {self.player_score})", True, WHITE)
            banker_text = font.render(f"Banker (Score: {self.banker_score})", True, WHITE)
            player_rect = player_text.get_rect(center=(center_x, player_y - 30))
            banker_rect = banker_text.get_rect(center=(center_x, banker_y - 50))
            self.screen.blit(player_text, player_rect)
            self.screen.blit(banker_text, banker_rect)

            # Draw bet buttons and other UI elements
            for button in self.bet_buttons:
                button.active = self.player_balance >= button.amount
                button.draw(self.screen)

            # Draw current bet and balance in top right
            balance_text = font.render(f"Balance: ${self.player_balance}", True, WHITE)
            bet_text = font.render(f"Current Bet: ${self.current_bet} on {self.bet_on or 'None'}", True, WHITE)
            
            # Position texts in top right corner
            balance_rect = balance_text.get_rect(topright=(WINDOW_WIDTH - 20, 20))
            bet_rect = bet_text.get_rect(topright=(WINDOW_WIDTH - 20, 60))
            
            self.screen.blit(balance_text, balance_rect)
            self.screen.blit(bet_text, bet_rect)

            # Draw betting instructions (left-aligned)
            if self.game_state == BETTING:
                instructions = [
                    "Press SPACE to switch between Player/Banker/Tie",
                    "Press ENTER to deal cards",
                    "Press R to continue",
                    "Press ESC for menu"
                ]
                
                font = pygame.font.Font(None, 24)
                y_offset = WINDOW_HEIGHT - 120
                for instruction in instructions:
                    text = font.render(instruction, True, WHITE)
                    self.screen.blit(text, (20, y_offset))  
                    y_offset += 30

            # Draw winner declaration with confetti and outline
            if self.last_result:
                # Use larger font for winner declaration
                font = pygame.font.Font(None, 72)
                win_text = f"{self.last_result} Wins!"
                
                # Calculate vertical position (moved down)
                vertical_pos = WINDOW_HEIGHT // 2 + 50
                
                # Draw thin black outline
                outline_offsets = [(-1,-1), (-1,1), (1,-1), (1,1)]
                for dx, dy in outline_offsets:
                    outline_text = font.render(win_text, True, BLACK)
                    text_rect = outline_text.get_rect(center=(WINDOW_WIDTH//2 + dx, vertical_pos + dy))
                    self.screen.blit(outline_text, text_rect)
                
                # Draw gold text
                gold_text = font.render(win_text, True, GOLD)
                text_rect = gold_text.get_rect(center=(WINDOW_WIDTH//2, vertical_pos))
                self.screen.blit(gold_text, text_rect)
                
                # Show confetti effect
                if self.show_confetti:
                    # Add new confetti
                    if len(self.confetti) < 100 and self.confetti_timer < 60:
                        for _ in range(5):
                            self.confetti.append(Confetti(WINDOW_WIDTH//2, vertical_pos - 50))
                        self.confetti_timer += 1
                    
                    # Update and draw existing confetti
                    self.confetti = [conf for conf in self.confetti if conf.update()]
                    for conf in self.confetti:
                        conf.draw(self.screen)

            self.draw_chips()

    def draw_chips(self):
        if self.current_chip:
            if self.current_chip == self.red_chip:
                self.screen.blit(self.red_chip, (WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - self.red_chip.get_height() // 2))
            elif self.current_chip == self.blue_chip:
                self.screen.blit(self.blue_chip, (WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - self.blue_chip.get_height() // 2))
            elif self.current_chip == self.yellow_chip:
                self.screen.blit(self.yellow_chip, (WINDOW_WIDTH // 2 - self.yellow_chip.get_width() // 2, WINDOW_HEIGHT // 2 + 150))

    def draw_rounded_rect(self, surface, color, rect, radius):
        x, y, width, height = rect
        pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)

    def handle_bet_button_click(self, pos):
        if self.state == PLAYING:
            for button in self.bet_buttons:
                if button.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})):
                    if self.player_balance >= button.amount:
                        # Update bet amount
                        self.current_bet = button.amount
                        # Default to Banker bet if no bet type selected
                        if not self.bet_on:
                            self.bet_on = "Banker"
                        # Set game state to betting
                        self.game_state = BETTING
                        return True
        return False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            if self.state == MENU:
                if self.menu.buttons['start'].handle_event(event):
                    self.state = PLAYING
                elif self.menu.buttons['load'].handle_event(event):
                    self.state = LOAD_MENU
                elif self.menu.buttons['exit'].handle_event(event):
                    return False
                    
            elif self.state == PLAYING:
                if event.button == pygame.BUTTON_RIGHT:
                    self.state = PAUSED
                else:
                    self.handle_bet_button_click(pos)
                    
            elif self.state == PAUSED:
                if self.menu.buttons['continue'].handle_event(event):
                    self.state = PLAYING
                elif self.menu.buttons['save'].handle_event(event):
                    self.state = SAVE_MENU
                elif self.menu.buttons['load'].handle_event(event):
                    self.state = LOAD_MENU
                elif self.menu.buttons['main_menu'].handle_event(event):
                    self.state = MENU
                elif self.menu.buttons['exit'].handle_event(event):
                    return False
                    
            elif self.state == SAVE_MENU:
                if self.menu.buttons['save1'].handle_event(event):
                    self.save_game(1)
                    self.state = PLAYING
                elif self.menu.buttons['save2'].handle_event(event):
                    self.save_game(2)
                    self.state = PLAYING
                elif self.menu.buttons['save3'].handle_event(event):
                    self.save_game(3)
                    self.state = PLAYING
                elif self.menu.buttons['back'].handle_event(event):
                    self.state = PAUSED
                    
            elif self.state == LOAD_MENU:
                if self.menu.buttons['load1'].handle_event(event):
                    self.load_game(1)
                elif self.menu.buttons['load2'].handle_event(event):
                    self.load_game(2)
                elif self.menu.buttons['load3'].handle_event(event):
                    self.load_game(3)
                elif self.menu.buttons['back'].handle_event(event):
                    self.state = PAUSED if self.player_hand else MENU
                    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.current_chip = None
            if event.key == pygame.K_ESCAPE and self.state == PLAYING:
                self.state = PAUSED
            elif event.key == pygame.K_SPACE and self.state == PLAYING:
                # Cycle through bet types and set the current chip
                if self.bet_on == "Player":
                    self.bet_on = "Banker"
                    self.current_chip = self.red_chip
                elif self.bet_on == "Banker":
                    self.bet_on = "Tie"
                    self.current_chip = self.yellow_chip
                else:
                    self.bet_on = "Player"
                    self.current_chip = self.blue_chip
            elif event.key == pygame.K_RETURN and self.state == PLAYING:
                if self.current_bet > 0 and self.bet_on:
                    self.player_balance -= self.current_bet
                    self.deal_initial_cards()
                    self.determine_winner()
            elif event.key == pygame.K_r and self.state == PLAYING:
                self.reset_cards()

        return True

    def determine_winner(self):
        self.total_games += 1

        # Player's Third Card rules
        if self.player_score <= 5:
            self.player_hand.append(self.deck.pop())
            self.player_score = self.calculate_score(self.player_hand)

        # Banker's Third Card rules
        if self.banker_score <= 5:
            if self.banker_score == 2:
                self.banker_hand.append(self.deck.pop())
            elif self.banker_score == 3:
                if self.player_score != 8:
                    self.banker_hand.append(self.deck.pop())
            elif self.banker_score == 4:
                if self.player_score in [2, 3, 4, 5, 6, 7]:
                    self.banker_hand.append(self.deck.pop())
            elif self.banker_score == 5:
                if self.player_score in [4, 5, 6, 7]:
                    self.banker_hand.append(self.deck.pop())
            elif self.banker_score == 6:
                if self.player_score in [6, 7]:
                    self.banker_hand.append(self.deck.pop())

            self.banker_score = self.calculate_score(self.banker_hand)

        # Determine the winner
        if self.player_score == self.banker_score:
            self.last_result = "Tie"
            self.ties += 1
            if self.bet_on == "Tie":
                self.player_balance += self.current_bet * 4
            else:
                self.player_balance += self.current_bet
        elif self.player_score > self.banker_score:
            self.last_result = "Player"
            self.player_wins += 1
            if self.bet_on == "Player":
                self.player_balance += self.current_bet * 2
        else:
            self.last_result = "Banker"
            self.banker_wins += 1
            if self.bet_on == "Banker":
                self.player_balance += int(self.current_bet * 1.95)

        self.current_bet = 0
        self.bet_on = None
        self.game_state = BETTING

        # Store hands for statistics
        self.banker_hands.append(self.banker_hand.copy())
        self.player_hands.append(self.player_hand.copy())
        
        # Store result
        self.game_results.append(self.last_result)

        # Play win sound and show confetti
        self.win_sound.play()
        self.show_confetti = True
        self.confetti_timer = pygame.time.get_ticks()
        
        # Create confetti particles
        for _ in range(50):
            self.confetti.append(Confetti(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
        return self.last_result

    def calculate_score(self, hand: List[Card]) -> int:
        return sum(card.numeric_value for card in hand) % 10

    def deal_initial_cards(self):
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.banker_hand = [self.deck.pop(), self.deck.pop()]
        self.player_score = self.calculate_score(self.player_hand)
        self.banker_score = self.calculate_score(self.banker_hand)

    def _create_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = {
            'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '10': 0, 'J': 0, 'Q': 0, 'K': 0
        }
        deck = []
        for suit in suits:
            for value, numeric_value in values.items():
                deck.append(Card(suit, value, numeric_value))
        random.shuffle(deck)
        return deck

    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if not self.handle_event(event):
                    running = False

            # Draw game
            self.screen.blit(self.background, (0, 0))
            
            if self.state == PLAYING:
                self.draw_game()
                self.draw_results_tracker()
            elif self.state in [MENU, PAUSED, SAVE_MENU, LOAD_MENU]:
                self.menu.draw(self.screen, self.state)

            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def start_game(self):
        self.run()

    def show_rules(self):
        print("Baccarat Rules: Bet on Player, Banker, or Tie. Closest to 9 wins. Face cards and 10s are worth 0. Aces are worth 1.")

if __name__ == "__main__":
    game = BaccaratGame()
    game.run()
