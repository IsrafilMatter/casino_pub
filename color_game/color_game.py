# Color Casino Game
# Israfil Palabay
# 2025-06-24

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from datetime import datetime
import json
import os
from casino_game import CasinoGame

class ColorGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = value

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
        
    def setup_betting_area(self, parent):
        betting_frame = tk.LabelFrame(
            parent,
            text="BETTING AREA",
            font=("Arial", 14, "bold"),
            fg="#fbbf24",
            bg="#7f1d1d"
        )
        betting_frame.pack(fill=tk.X, pady=10)
        
        # Create betting grid
        self.betting_buttons = {}
        self.bet_labels = {}
        
        for i, color in enumerate(self.COLORS):
            row = i // 3
            col = i % 3
            
            # Color frame
            color_frame = tk.Frame(betting_frame, bg="#374151", relief=tk.RAISED, bd=2)
            color_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Color button
            color_button = tk.Label(
                color_frame,
                text=self.color_names[color],
                font=("Arial", 12, "bold"),
                bg=self.color_map[color],
                fg="black" if color in ["white", "yellow"] else "white",
                width=12,
                height=2,
                relief=tk.RAISED,
                bd=2
            )
            color_button.pack(pady=5)
            
            # Bet amount label
            bet_label = tk.Label(
                color_frame,
                text="$0",
                font=("Arial", 10, "bold"),
                fg="#fbbf24",
                bg="#374151"
            )
            bet_label.pack()
            self.bet_labels[color] = bet_label
            
            # Betting buttons frame
            buttons_frame = tk.Frame(color_frame, bg="#374151")
            buttons_frame.pack(pady=5)
            
            # Small bet buttons
            small_frame = tk.Frame(buttons_frame, bg="#374151")
            small_frame.pack()
            
            for amount in self.BET_AMOUNTS[:4]:
                btn = tk.Button(
                    small_frame,
                    text=f"${amount}",
                    font=("Arial", 8),
                    bg="#15803d",
                    fg="white",
                    width=6,
                    command=lambda c=color, a=amount: self.add_bet(c, a)
                )
                btn.pack(side=tk.LEFT, padx=1)
                
            # Large bet buttons
            large_frame = tk.Frame(buttons_frame, bg="#374151")
            large_frame.pack()
            
            for amount in self.BET_AMOUNTS[4:]:
                display = f"${amount//1000}K" if amount >= 1000 else f"${amount}"
                btn = tk.Button(
                    large_frame,
                    text=display,
                    font=("Arial", 8),
                    bg="#1d4ed8",
                    fg="white",
                    width=6,
                    command=lambda c=color, a=amount: self.add_bet(c, a)
                )
                btn.pack(side=tk.LEFT, padx=1)
        
        # Configure grid weights
        for i in range(3):
            betting_frame.grid_columnconfigure(i, weight=1)
            
    def setup_controls(self, parent):
        controls_frame = tk.Frame(parent, bg="#7f1d1d")
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Control buttons
        self.play_again_btn = tk.Button(
            controls_frame,
            text="Play Again",
            font=("Arial", 10, "bold"),
            bg="#15803d",
            fg="white",
            padx=15,
            pady=5,
            command=self.play_again
        )
        self.play_again_btn.pack(side=tk.LEFT, padx=5)
        
        self.double_bet_btn = tk.Button(
            controls_frame,
            text="Double Bet",
            font=("Arial", 10, "bold"),
            bg="#1d4ed8",
            fg="white",
            padx=15,
            pady=5,
            command=self.double_bets
        )
        self.double_bet_btn.pack(side=tk.LEFT, padx=5)
        
        self.undo_bet_btn = tk.Button(
            controls_frame,
            text="Undo Bet",
            font=("Arial", 10, "bold"),
            bg="#eab308",
            fg="black",
            padx=15,
            pady=5,
            command=self.undo_last_bet
        )
        self.undo_bet_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_bets_btn = tk.Button(
            controls_frame,
            text="Clear Bets",
            font=("Arial", 10, "bold"),
            bg="#dc2626",
            fg="white",
            padx=15,
            pady=5,
            command=self.clear_all_bets
        )
        self.clear_bets_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_stats(self, parent):
        stats_label = tk.Label(
            parent,
            text="GAME STATS",
            font=("Arial", 14, "bold"),
            fg="#fbbf24",
            bg="#374151"
        )
        stats_label.pack(pady=10)
        
        # Games played
        self.games_played_label = tk.Label(
            parent,
            text=f"Games Played: {len(self.game_history)}",
            font=("Arial", 10),
            fg="white",
            bg="#374151"
        )
        self.games_played_label.pack(pady=5)
        
        # Current streak
        self.streak_label = tk.Label(
            parent,
            text="Current Streak: NONE",
            font=("Arial", 10),
            fg="white",
            bg="#374151"
        )
        self.streak_label.pack(pady=5)
        
        # Color win rates
        win_rates_label = tk.Label(
            parent,
            text="Color Win Rates:",
            font=("Arial", 10, "bold"),
            fg="#fbbf24",
            bg="#374151"
        )
        win_rates_label.pack(pady=(20, 5))
        
        self.win_rate_labels = {}
        for color in self.COLORS:
            label = tk.Label(
                parent,
                text=f"{self.color_names[color]}: 0%",
                font=("Arial", 9),
                fg="white",
                bg="#374151"
            )
            label.pack(pady=1)
            self.win_rate_labels[color] = label
            
    def setup_history(self, parent):
        history_frame = tk.LabelFrame(
            parent,
            text="RECENT RESULTS",
            font=("Arial", 12, "bold"),
            fg="#fbbf24",
            bg="#7f1d1d"
        )
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create scrollable text widget
        self.history_text = tk.Text(
            history_frame,
            height=8,
            bg="#374151",
            fg="white",
            font=("Arial", 9),
            state=tk.DISABLED
        )
        
        scrollbar = tk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def add_bet(self, color, amount):
        if self.is_rolling:
            return
            
        if self.balance >= amount:
            if color in self.bets:
                self.bets[color] += amount
            else:
                self.bets[color] = amount
                
            self.balance -= amount
            self.update_display()
            
    def roll_dice(self):
        if self.is_rolling or not self.bets:
            return
            
        self.is_rolling = True
        self.last_winnings = 0
        self.winning_colors = []
        self.show_celebration = False
        
        # Update button state
        self.roll_button.config(text="ROLLING...", state=tk.DISABLED)
        
        # Start rolling animation
        self.animate_dice_roll()
        
    def animate_dice_roll(self):
        # Animate for 3 seconds
        start_time = time.time()
        
        def update_dice():
            if time.time() - start_time < 3:
                # Random colors during animation
                for i, label in enumerate(self.dice_labels):
                    random_color = random.choice(self.COLORS)
                    label.config(
                        text=self.color_names[random_color],
                        bg=self.color_map[random_color],
                        fg="black" if random_color in ["white", "yellow"] else "white"
                    )
                self.root.after(100, update_dice)
            else:
                self.finish_roll()
                
        update_dice()
        
    def finish_roll(self):
        # Generate final dice results
        self.dice = [random.choice(self.COLORS) for _ in range(3)]
        
        # Update dice display
        for i, label in enumerate(self.dice_labels):
            color = self.dice[i]
            label.config(
                text=self.color_names[color],
                bg=self.color_map[color],
                fg="black" if color in ["white", "yellow"] else "white"
            )
            
        # Calculate winnings
        self.calculate_winnings()
        
        # Update game state
        self.game_number += 1
        self.is_rolling = False
        
        # Add to history
        result = {
            'dice': self.dice.copy(),
            'timestamp': datetime.now(),
            'winning_colors': self.winning_colors.copy(),
            'winnings': self.last_winnings
        }
        self.game_history.append(result)
        
        # Reset button
        self.roll_button.config(text="ROLL DICE", state=tk.NORMAL)
        
        # Update display
        self.update_display()
        
        # Show results
        if self.last_winnings > 0:
            if self.last_winnings >= 10000:
                messagebox.showinfo("JACKPOT!", f"TRIPLE JACKPOT! You won ${self.last_winnings:,}!")
            else:
                messagebox.showinfo("Winner!", f"You won ${self.last_winnings:,}!")
                
    def calculate_winnings(self):
        # Count dice colors
        color_counts = {}
        for color in self.dice:
            color_counts[color] = color_counts.get(color, 0) + 1
            
        total_winnings = 0
        winners = []
        
        # Calculate regular winnings
        for color, bet_amount in self.bets.items():
            matches = color_counts.get(color, 0)
            if matches > 0:
                if matches == 1:
                    multiplier = 2
                elif matches == 2:
                    multiplier = 3
                else:  # matches == 3
                    multiplier = 6
                    
                win_amount = bet_amount * multiplier
                total_winnings += win_amount
                winners.append(color)
                
        # Check for triple jackpot
        total_bet = sum(self.bets.values())
        if len(set(self.dice)) == 1 and total_bet >= 1000:  # All same color and eligible
            jackpot_color = self.dice[0]
            if jackpot_color in self.bets:
                total_winnings += 10000
                
        self.balance += total_winnings
        self.last_winnings = total_winnings
        self.winning_colors = winners
        
    def play_again(self):
        if not self.bets or self.is_rolling:
            return
            
        total_bet = sum(self.bets.values())
        if self.balance >= total_bet:
            self.balance -= total_bet
            self.roll_dice()
            
    def double_bets(self):
        if not self.bets or self.is_rolling:
            return
            
        total_bet = sum(self.bets.values())
        if self.balance >= total_bet:
            for color in self.bets:
                self.bets[color] *= 2
            self.balance -= total_bet
            self.update_display()
            
    def undo_last_bet(self):
        if not self.bets or self.is_rolling:
            return
            
        # Find the last bet (this is simplified - in a real implementation, 
        # you'd want to track bet order)
        last_color = list(self.bets.keys())[-1]
        last_amount = self.bets[last_color]
        
        if last_amount <= 50:  # Assume minimum bet increment
            del self.bets[last_color]
        else:
            self.bets[last_color] -= 50  # Remove one increment
            
        self.balance += 50
        self.update_display()
        
    def clear_all_bets(self):
        if self.is_rolling:
            return
            
        refund = sum(self.bets.values())
        self.bets.clear()
        self.balance += refund
        self.update_display()
        
    def update_display(self):
        # Update balance
        self.balance_label.config(text=f"Balance: ${self.balance:,}")
        
        # Update total bet
        total_bet = sum(self.bets.values())
        self.total_bet_label.config(text=f"Total Bet: ${total_bet:,}")
        
        # Update winnings
        if self.last_winnings > 0:
            self.winnings_label.config(text=f"Won: ${self.last_winnings:,}")
            self.winnings_label.pack(side=tk.LEFT, padx=5)
        else:
            self.winnings_label.pack_forget()
            
        # Update game number
        self.game_number_label.config(text=f"Game #{self.game_number}")
        
        # Update bet labels
        for color in self.COLORS:
            amount = self.bets.get(color, 0)
            self.bet_labels[color].config(text=f"${amount:,}")
            
        # Update stats
        self.games_played_label.config(text=f"Games Played: {len(self.game_history)}")
        
        # Update streak
        if self.last_winnings > 0:
            streak_text = "WIN"
        elif len(self.game_history) > 0:
            streak_text = "LOSE"
        else:
            streak_text = "NONE"
        self.streak_label.config(text=f"Current Streak: {streak_text}")
        
        # Update win rates
        for color in self.COLORS:
            win_rate = self.get_color_win_rate(color)
            self.win_rate_labels[color].config(text=f"{self.color_names[color]}: {win_rate}%")
            
        # Update history
        self.update_history_display()
        
        # Update button states
        self.update_button_states()
        
    def get_color_win_rate(self, color):
        if not self.game_history:
            return 0
            
        wins = sum(1 for result in self.game_history if color in result['winning_colors'])
        return round((wins / len(self.game_history)) * 100)
        
    def update_history_display(self):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        for i, result in enumerate(reversed(self.game_history[-20:])):
            game_num = len(self.game_history) - i
            dice_str = " ".join([self.color_names[color][0] for color in result['dice']])
            win_str = " WIN" if result['winnings'] > 0 else ""
            time_str = result['timestamp'].strftime("%H:%M:%S")
            
            line = f"#{game_num}: {dice_str}{win_str} ({time_str})\n"
            self.history_text.insert(tk.END, line)
            
        self.history_text.config(state=tk.DISABLED)
        
    def update_button_states(self):
        total_bet = sum(self.bets.values())
        has_bets = bool(self.bets)
        can_afford_double = self.balance >= total_bet
        
        # Roll button
        self.roll_button.config(state=tk.NORMAL if has_bets and not self.is_rolling else tk.DISABLED)
        
        # Control buttons
        self.play_again_btn.config(state=tk.NORMAL if has_bets and can_afford_double and not self.is_rolling else tk.DISABLED)
        self.double_bet_btn.config(state=tk.NORMAL if has_bets and can_afford_double and not self.is_rolling else tk.DISABLED)
        self.undo_bet_btn.config(state=tk.NORMAL if has_bets and not self.is_rolling else tk.DISABLED)
        self.clear_bets_btn.config(state=tk.NORMAL if has_bets and not self.is_rolling else tk.DISABLED)
        
    def save_game_data(self):
        data = {
            'balance': self.balance,
            'game_number': self.game_number,
            'game_history': []
        }
        
        # Convert history to serializable format
        for result in self.game_history:
            data['game_history'].append({
                'dice': result['dice'],
                'timestamp': result['timestamp'].isoformat(),
                'winning_colors': result['winning_colors'],
                'winnings': result['winnings']
            })
            
        try:
            with open('perya_game_save.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving game data: {e}")
            
    def load_game_data(self):
        try:
            if os.path.exists('perya_game_save.json'):
                with open('perya_game_save.json', 'r') as f:
                    data = json.load(f)
                    
                self.balance = data.get('balance', 5000)
                self.game_number = data.get('game_number', 1)
                
                # Load history
                for result_data in data.get('game_history', []):
                    result = {
                        'dice': result_data['dice'],
                        'timestamp': datetime.fromisoformat(result_data['timestamp']),
                        'winning_colors': result_data['winning_colors'],
                        'winnings': result_data['winnings']
                    }
                    self.game_history.append(result)
                    
        except Exception as e:
            print(f"Error loading game data: {e}")
            
    def on_closing(self):
        self.save_game_data()
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

    def start_game(self):
        self.run()

    def show_rules(self):
        print("Color Game Rules: Bet on colors. Dice are rolled. Payouts depend on matches. Triple jackpot for 3 of a kind and high bet.")

if __name__ == "__main__":
    game = ColorGame()
    game.run()
