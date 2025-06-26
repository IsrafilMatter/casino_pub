# Color Casino Game
# Israfil Palabay
# 2025-06-24

# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from datetime import datetime
import json
import os
from casino_game import CasinoGame

# Inherit from CasinoGame class
class ColorGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = 
        
    def __init__(self, player_balance=5000):
        super().__init__(player_balance)
        self.root = tk.Tk()
        self.root.title("Perya Color Game")
        self.root.geometry("1200x800")
        self.root.configure(bg="#7f1d1d")
        
        # Game state
        self.bets = {}  # {color: amount}
        self.dice = ["red", "blue", "yellow"]
        self.is_rolling = False
        self.game_history = []
        self.last_winnings = 0
        self.winning_colors = []
        self.game_number = 1
        self.show_celebration = False
        
        # Colors and constants
        self.COLORS = ["red", "blue", "yellow", "green", "white", "pink"]
        self.BET_AMOUNTS = [5, 10, 20, 50, 100, 200, 500, 1000]
        
        self.color_map = {
            "red": "#dc2626",
            "blue": "#2563eb", 
            "yellow": "#eab308",
            "green": "#16a34a",
            "white": "#ffffff",
            "pink": "#ec4899"
        }
        
        self.color_names = {
            "red": "RED",
            "blue": "BLUE", 
            "yellow": "YELLOW",
            "green": "GREEN",
            "white": "WHITE",
            "pink": "PINK"
        } 
        
        # Load saved data
        self.load_game_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Start the application
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
# GUI Setup
    def setup_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#7f1d1d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.setup_header(main_frame)
        
        # Game area
        game_frame = tk.Frame(main_frame, bg="#7f1d1d")
        game_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left side - Dice and betting
        left_frame = tk.Frame(game_frame, bg="#7f1d1d")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right side - Stats
        right_frame = tk.Frame(game_frame, bg="#374151", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Setup sections
        self.setup_dice_area(left_frame)
        self.setup_betting_area(left_frame)
        self.setup_controls(left_frame)
        self.setup_stats(right_frame)
        self.setup_history(left_frame)
        
        # Update display
        self.update_display()

    def setup_header(self, parent):
        header_frame = tk.Frame(parent, bg="#7f1d1d")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="PERYA COLOR GAME",
            font=("Arial", 24, "bold"),
            fg="#fbbf24",
            bg="#7f1d1d"
        )
        title_label.pack()
        
        # Game number
        self.game_number_label = tk.Label(
            header_frame,
            text=f"Game #{self.game_number}",
            font=("Arial", 14),
            fg="#fde047",
            bg="#7f1d1d"
        )
        self.game_number_label.pack(pady=5)
        
        # Stats row
        stats_frame = tk.Frame(header_frame, bg="#7f1d1d")
        stats_frame.pack(pady=10)
        
        # Balance
        self.balance_label = tk.Label(
            stats_frame,
            text=f"Balance: ${self.balance:,}",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#15803d",
            padx=15,
            pady=8,
            relief=tk.RAISED,
            bd=2
        )
        self.balance_label.pack(side=tk.LEFT, padx=5)
        
        # Total bet
        self.total_bet_label = tk.Label(
            stats_frame,
            text="Total Bet: $0",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1d4ed8",
            padx=15,
            pady=8,
            relief=tk.RAISED,
            bd=2
        )
        self.total_bet_label.pack(side=tk.LEFT, padx=5)
        
        # Winnings
        self.winnings_label = tk.Label(
            stats_frame,
            text="",
            font=("Arial", 12, "bold"),
            fg="black",
            bg="#eab308",
            padx=15,
            pady=8,
            relief=tk.RAISED,
            bd=2
        )
        
    def setup_dice_area(self, parent):
        dice_frame = tk.LabelFrame(
            parent,
            text="DICE AREA",
            font=("Arial", 16, "bold"),
            fg="#fbbf24",
            bg="#92400e",
            relief=tk.RAISED,
            bd=3
        )
        dice_frame.pack(fill=tk.X, pady=10)
        
        # Dice container
        dice_container = tk.Frame(dice_frame, bg="#92400e")
        dice_container.pack(pady=20)
        
        self.dice_labels = []
        for i in range(3):
            dice_label = tk.Label(
                dice_container,
                text=self.color_names[self.dice[i]],
                font=("Arial", 14, "bold"),
                width=8,
                height=3,
                relief=tk.RAISED,
                bd=3
            )
            dice_label.pack(side=tk.LEFT, padx=10)
            self.dice_labels.append(dice_label)
            
        # Roll button
        self.roll_button = tk.Button(
            dice_frame,
            text="ROLL DICE",
            font=("Arial", 16, "bold"),
            bg="#dc2626",
            fg="white",
            padx=30,
            pady=10,
            relief=tk.RAISED,
            bd=3,
            command=self.roll_dice
        )
        self.roll_button.pack(pady=20)
        
# Game Logic
# Winning Calculation
# Game state updates
# Save/Load Game
# Exit handling
# Public methods
# Main entry