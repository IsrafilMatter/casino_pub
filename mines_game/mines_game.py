# Mines Casino Game
# Israfil Palabay
# 2025-06-24

import tkinter as tk
from tkinter import ttk, messagebox
import random
import secrets
import json
import os
from typing import List, Dict, Any
import logging
from casino_game import CasinoGame

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MinesGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = value

    def __init__(self, player_balance=1000.0):
        super().__init__(player_balance)
        self.root = tk.Tk()
        self.root.title("Mines Casino Game")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a1a")
        
        # Game state
        self.current_bet = 10.0
        self.mines_count = 3  # Default value only
        self.game_state = "betting"  # betting, playing, game_over
        self.grid = ["hidden"] * 25
        self.revealed_tiles = []
        self.mine_positions = []
        self.multiplier = 1.0
        
        # Load saved game state if exists
        self.load_game_state()
        
        # Colors and styles
        self.colors = {
            'bg': '#1a1a1a',
            'card_bg': '#21262d',
            'gold': '#ffd700',
            'dark_gold': '#b8860b',
            'success': '#238636',
            'danger': '#da3633',
            'warning': '#f85149',
            'info': '#0dcaf0',
            'text_light': '#f0f6fc',
            'border': '#30363d'
        }
        
        self.setup_ui()
        self.update_display()
        
        # Save game state on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header frame
        header_frame = tk.Frame(main_frame, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title and balance
        title_label = tk.Label(header_frame, text="💣 Mines Casino", 
                              font=("Arial", 16, "bold"), 
                              fg=self.colors['gold'], bg=self.colors['card_bg'])
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.balance_label = tk.Label(header_frame, text=f"Balance: ${self.balance:.2f}", 
                                     font=("Arial", 12, "bold"), 
                                     fg=self.colors['gold'], bg=self.colors['card_bg'])
        self.balance_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.multiplier_label = tk.Label(header_frame, text=f"Multiplier: {self.multiplier:.2f}x", 
                                        font=("Arial", 12, "bold"), 
                                        fg=self.colors['success'], bg=self.colors['card_bg'])
        self.multiplier_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Content frame
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - controls
        self.setup_controls_panel(content_frame)
        
        # Center panel - game grid
        self.setup_game_grid(content_frame)
        
        # Right panel - instructions
        self.setup_instructions_panel(content_frame)
        
    def setup_controls_panel(self, parent):
        """Setup the game controls panel"""
        controls_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0)
        
        # Title
        title = tk.Label(controls_frame, text="⚙️ Game Controls", 
                        font=("Arial", 12, "bold"), 
                        fg=self.colors['gold'], bg=self.colors['card_bg'])
        title.pack(pady=10)
        
        # Bet amount
        bet_frame = tk.Frame(controls_frame, bg=self.colors['card_bg'])
        bet_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(bet_frame, text="Bet Amount:", 
                fg=self.colors['text_light'], bg=self.colors['card_bg']).pack(anchor=tk.W)
        
        bet_input_frame = tk.Frame(bet_frame, bg=self.colors['card_bg'])
        bet_input_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(bet_input_frame, text="$", 
                fg=self.colors['gold'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
        
        self.bet_var = tk.DoubleVar(value=self.current_bet)
        self.bet_entry = tk.Entry(bet_input_frame, textvariable=self.bet_var, width=10,
                                 bg=self.colors['bg'], fg=self.colors['text_light'], 
                                 insertbackground=self.colors['text_light'])
        self.bet_entry.pack(side=tk.LEFT, padx=(2, 0))
        
        # Bet adjustment buttons
        bet_btn_frame = tk.Frame(bet_frame, bg=self.colors['card_bg'])
        bet_btn_frame.pack(fill=tk.X, pady=2)
        
        half_btn = tk.Button(bet_btn_frame, text="½", command=self.half_bet,
                            bg=self.colors['warning'], fg='black', font=("Arial", 8, "bold"))
        half_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        double_btn = tk.Button(bet_btn_frame, text="2x", command=self.double_bet,
                              bg=self.colors['warning'], fg='black', font=("Arial", 8, "bold"))
        double_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Mines count
        mines_frame = tk.Frame(controls_frame, bg=self.colors['card_bg'])
        mines_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(mines_frame, text="Number of Mines:", 
                fg=self.colors['text_light'], bg=self.colors['card_bg']).pack(anchor=tk.W)
        
        self.mines_var = tk.IntVar(value=self.mines_count)
        mines_spinbox = tk.Spinbox(mines_frame, from_=1, to=20, textvariable=self.mines_var,
                                  bg=self.colors['bg'], fg=self.colors['text_light'],
                                  buttonbackground=self.colors['card_bg'],
                                  width=5, wrap=True)
        mines_spinbox.pack(fill=tk.X, pady=2)
        
        # Game buttons
        self.start_btn = tk.Button(controls_frame, text="🎮 Start Game", 
                                  command=self.start_game, font=("Arial", 10, "bold"),
                                  bg=self.colors['success'], fg='white', height=2)
        self.start_btn.pack(fill=tk.X, padx=10, pady=5)
        
        self.cash_out_btn = tk.Button(controls_frame, text="💰 Cash Out", 
                                     command=self.cash_out, font=("Arial", 10, "bold"),
                                     bg=self.colors['warning'], fg='black', height=2)
        self.cash_out_btn.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_pick_btn = tk.Button(controls_frame, text="🤖 Auto Pick", 
                                      command=self.auto_pick, font=("Arial", 10, "bold"),
                                      bg=self.colors['info'], fg='black', height=2)
        self.auto_pick_btn.pack(fill=tk.X, padx=10, pady=5)
        
        self.reset_btn = tk.Button(controls_frame, text="🔄 New Game", 
                                  command=self.reset_game, font=("Arial", 10, "bold"),
                                  bg='#0d6efd', fg='white', height=2)
        self.reset_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Game stats
        stats_frame = tk.Frame(controls_frame, bg=self.colors['card_bg'])
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(stats_frame, text="📊 Game Stats", 
                font=("Arial", 10, "bold"), 
                fg=self.colors['gold'], bg=self.colors['card_bg']).pack()
        
        self.revealed_label = tk.Label(stats_frame, text="Revealed: 0", 
                                      fg=self.colors['text_light'], bg=self.colors['card_bg'])
        self.revealed_label.pack()
        
        self.remaining_label = tk.Label(stats_frame, text="Remaining: 25", 
                                       fg=self.colors['text_light'], bg=self.colors['card_bg'])
        self.remaining_label.pack()
        
        self.potential_win_label = tk.Label(stats_frame, text="Potential Win: $0.00", 
                                           fg=self.colors['success'], bg=self.colors['card_bg'],
                                           font=("Arial", 9, "bold"))
        self.potential_win_label.pack()
        
    def setup_game_grid(self, parent):
        """Setup the game grid"""
        grid_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Title
        title = tk.Label(grid_frame, text="🎯 Game Grid", 
                        font=("Arial", 12, "bold"), 
                        fg=self.colors['gold'], bg=self.colors['card_bg'])
        title.pack(pady=10)
        
        # Grid container
        self.grid_container = tk.Frame(grid_frame, bg=self.colors['bg'])
        self.grid_container.pack(expand=True)
        
        # Create grid buttons
        self.tile_buttons = []
        for i in range(25):
            row = i // 5
            col = i % 5
            
            btn = tk.Button(self.grid_container, text="❓", width=6, height=3,
                           font=("Arial", 12, "bold"), 
                           command=lambda idx=i: self.reveal_tile(idx),
                           bg=self.colors['card_bg'], fg=self.colors['text_light'],
                           relief=tk.RAISED, bd=2)
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.tile_buttons.append(btn)
        
    def setup_instructions_panel(self, parent):
        """Setup the instructions panel"""
        instructions_frame = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        instructions_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Title
        title = tk.Label(instructions_frame, text="ℹ️ How to Play", 
                        font=("Arial", 12, "bold"), 
                        fg=self.colors['gold'], bg=self.colors['card_bg'])
        title.pack(pady=10)
        
        # Instructions
        instructions = [
            "1. Set your bet amount",
            "2. Click tiles or use Auto Pick to reveal gems",
            "3. Each safe tile increases your multiplier",
            "4. Cash out anytime to secure winnings",
            "5. Hit a mine and lose your bet!"
        ]
        
        for instruction in instructions:
            label = tk.Label(instructions_frame, text=instruction, 
                           fg=self.colors['text_light'], bg=self.colors['card_bg'],
                           wraplength=200, justify=tk.LEFT)
            label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Separator
        separator = tk.Frame(instructions_frame, height=2, bg=self.colors['border'])
        separator.pack(fill=tk.X, padx=10, pady=10)
        
        # Legend
        legend_title = tk.Label(instructions_frame, text="🔍 Legend", 
                               font=("Arial", 10, "bold"), 
                               fg=self.colors['gold'], bg=self.colors['card_bg'])
        legend_title.pack(pady=(0, 5))
        
        legend_items = [
            ("❓", "Hidden Tile"),
            ("💎", "Safe Tile (Gem)"),
            ("💣", "Mine")
        ]
        
        for symbol, description in legend_items:
            legend_frame = tk.Frame(instructions_frame, bg=self.colors['card_bg'])
            legend_frame.pack(fill=tk.X, padx=10, pady=1)
            
            tk.Label(legend_frame, text=symbol, 
                    fg=self.colors['text_light'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
            tk.Label(legend_frame, text=description, 
                    fg=self.colors['text_light'], bg=self.colors['card_bg']).pack(side=tk.LEFT, padx=(5, 0))
        
        # Keyboard shortcuts
        separator2 = tk.Frame(instructions_frame, height=2, bg=self.colors['border'])
        separator2.pack(fill=tk.X, padx=10, pady=10)
        
        shortcuts_title = tk.Label(instructions_frame, text="⌨️ Shortcuts", 
                                  font=("Arial", 10, "bold"), 
                                  fg=self.colors['gold'], bg=self.colors['card_bg'])
        shortcuts_title.pack(pady=(0, 5))
        
        shortcuts = [
            ("Space", "Cash Out"),
            ("Enter", "Start Game"),
            ("A", "Auto Pick"),
            ("R", "Reset Game")
        ]
        
        for key, action in shortcuts:
            shortcut_frame = tk.Frame(instructions_frame, bg=self.colors['card_bg'])
            shortcut_frame.pack(fill=tk.X, padx=10, pady=1)
            
            key_label = tk.Label(shortcut_frame, text=key, 
                                font=("Arial", 8, "bold"),
                                fg='black', bg=self.colors['text_light'],
                                relief=tk.RAISED, bd=1, padx=3, pady=1)
            key_label.pack(side=tk.LEFT)
            
            tk.Label(shortcut_frame, text=action, 
                    fg=self.colors['text_light'], bg=self.colors['card_bg']).pack(side=tk.LEFT, padx=(5, 0))
    
    def calculate_multiplier(self, safe_tiles_revealed: int, total_mines: int, total_tiles: int = 25) -> float:
        """Calculate multiplier based on revealed safe tiles and mine count"""
        if safe_tiles_revealed == 0:
            return 1.0
        
        safe_tiles_total = total_tiles - total_mines
        multiplier = 1.0
        
        for i in range(safe_tiles_revealed):
            remaining_safe = safe_tiles_total - i
            remaining_total = total_tiles - i
            prob = remaining_safe / remaining_total
            multiplier *= (1 / prob) * 0.97  # 97% RTP (3% house edge)
        
        return round(multiplier, 2)
    
    def generate_mine_positions(self, mines_count: int) -> List[int]:
        """Generate mine positions using cryptographically secure randomness"""
        indices = list(range(25))
        secrets.SystemRandom().shuffle(indices)
        return indices[:mines_count]
    
    def start_game(self):
        """Start a new game"""
        try:
            bet_amount = self.bet_var.get()
            mines_count = self.mines_var.get()
            
            # Validate inputs
            if bet_amount <= 0:
                messagebox.showerror("Error", "Bet amount must be greater than 0")
                return
            
            if bet_amount > self.balance:
                messagebox.showerror("Error", "Insufficient balance")
                return
            
            if mines_count < 1 or mines_count > 20:
                messagebox.showerror("Error", "Number of mines must be between 1 and 20")
                return
            
            # Start new game
            self.current_bet = bet_amount
            self.mines_count = mines_count
            self.balance -= bet_amount
            self.game_state = "playing"
            self.revealed_tiles = []
            self.mine_positions = self.generate_mine_positions(mines_count)
            self.multiplier = 1.0
            self.grid = ["hidden"] * 25
            
            logging.debug(f"New game started: bet={bet_amount}, mines={mines_count}, positions={self.mine_positions}")
            
            self.update_display()
            messagebox.showinfo("Game Started", f"New game started with ${bet_amount:.2f} bet and {mines_count} mines!")
            
        except tk.TclError:
            messagebox.showerror("Error", "Invalid input values")
    
    def reveal_tile(self, tile_index: int):
        """Reveal a tile"""
        if self.game_state != "playing":
            return
        
        if tile_index in self.revealed_tiles:
            return
        
        # Add tile to revealed tiles
        self.revealed_tiles.append(tile_index)
        
        # Check if tile is a mine
        if tile_index in self.mine_positions:
            # Hit a mine - game over
            self.grid[tile_index] = "mine"
            self.game_state = "game_over"
            
            # Reveal all mines
            for mine_pos in self.mine_positions:
                self.grid[mine_pos] = "mine"
            
            self.update_display()
            messagebox.showerror("Game Over", "You hit a mine! Game over.")
        else:
            # Safe tile
            self.grid[tile_index] = "safe"
            
            # Calculate new multiplier
            safe_tiles_revealed = len([i for i in self.revealed_tiles if i not in self.mine_positions])
            self.multiplier = self.calculate_multiplier(safe_tiles_revealed, self.mines_count)
            
            # Check if all safe tiles are revealed (win condition)
            total_safe_tiles = 25 - self.mines_count
            if safe_tiles_revealed >= total_safe_tiles:
                # Auto cash out - player found all safe tiles
                payout = self.current_bet * self.multiplier
                self.balance += payout
                self.game_state = "game_over"
                self.update_display()
                messagebox.showinfo("Congratulations!", f"You found all safe tiles and won ${payout:.2f}!")
            else:
                self.update_display()
    
    def cash_out(self):
        """Cash out current winnings"""
        if self.game_state != "playing":
            return
        
        payout = self.current_bet * self.multiplier
        self.balance += payout
        self.game_state = "game_over"
        
        # Reveal all mines for transparency
        for mine_pos in self.mine_positions:
            if self.grid[mine_pos] == "hidden":
                self.grid[mine_pos] = "mine_revealed"
        
        self.update_display()
        messagebox.showinfo("Cash Out", f"You cashed out and won ${payout:.2f}!")
    
    def auto_pick(self):
        """Automatically pick a random unrevealed tile"""
        if self.game_state != "playing":
            return
        
        # Get all unrevealed tiles
        unrevealed_tiles = []
        for i in range(25):
            if i not in self.revealed_tiles and self.grid[i] == "hidden":
                unrevealed_tiles.append(i)
        
        if not unrevealed_tiles:
            return
        
        # Use cryptographically secure random selection
        selected_tile = secrets.choice(unrevealed_tiles)
        logging.debug(f"Auto-pick selected tile {selected_tile}")
        
        self.reveal_tile(selected_tile)
    
    def reset_game(self):
        """Reset the game"""
        self.game_state = "betting"
        self.grid = ["hidden"] * 25
        self.revealed_tiles = []
        self.mine_positions = []
        self.multiplier = 1.0
        # Always use the current value from the spinbox for the next game
        self.mines_count = self.mines_var.get()
        self.update_display()
    
    def half_bet(self):
        """Halve the bet amount"""
        if self.game_state == "betting":
            new_bet = max(0.1, self.bet_var.get() / 2)
            self.bet_var.set(new_bet)
    
    def double_bet(self):
        """Double the bet amount"""
        if self.game_state == "betting":
            new_bet = min(self.balance, self.bet_var.get() * 2)
            self.bet_var.set(new_bet)
    
    def update_display(self):
        """Update the display elements"""
        # Update labels
        self.balance_label.config(text=f"Balance: ${self.balance:.2f}")
        self.multiplier_label.config(text=f"Multiplier: {self.multiplier:.2f}x")
        self.revealed_label.config(text=f"Revealed: {len(self.revealed_tiles)}")
        self.remaining_label.config(text=f"Remaining: {25 - len(self.revealed_tiles)}")
        
        if self.game_state == "playing":
            potential_win = self.current_bet * self.multiplier
            self.potential_win_label.config(text=f"Potential Win: ${potential_win:.2f}")
        else:
            self.potential_win_label.config(text="Potential Win: $0.00")
        
        # Update button states
        if self.game_state == "betting" or self.game_state == "game_over":
            self.start_btn.config(state=tk.NORMAL)
            self.cash_out_btn.config(state=tk.DISABLED)
            self.auto_pick_btn.config(state=tk.DISABLED)
            self.bet_entry.config(state=tk.NORMAL)
        elif self.game_state == "playing":
            self.start_btn.config(state=tk.DISABLED)
            self.cash_out_btn.config(state=tk.NORMAL)
            self.auto_pick_btn.config(state=tk.NORMAL)
            self.bet_entry.config(state=tk.DISABLED)
        
        # Update grid tiles
        for i, btn in enumerate(self.tile_buttons):
            tile_state = self.grid[i]
            
            if tile_state == "hidden":
                btn.config(text="❓", bg=self.colors['card_bg'], fg=self.colors['text_light'],
                          state=tk.NORMAL if self.game_state == "playing" else tk.DISABLED)
            elif tile_state == "safe":
                btn.config(text="💎", bg=self.colors['success'], fg='white', state=tk.DISABLED)
            elif tile_state == "mine":
                btn.config(text="💣", bg=self.colors['danger'], fg='white', state=tk.DISABLED)
            elif tile_state == "mine_revealed":
                btn.config(text="💣", bg=self.colors['warning'], fg='black', state=tk.DISABLED)
        
        # Save game state
        self.save_game_state()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<KeyPress-space>', lambda e: self.cash_out())
        self.root.bind('<KeyPress-Return>', lambda e: self.start_game())
        self.root.bind('<KeyPress-a>', lambda e: self.auto_pick())
        self.root.bind('<KeyPress-A>', lambda e: self.auto_pick())
        self.root.bind('<KeyPress-r>', lambda e: self.reset_game())
        self.root.bind('<KeyPress-R>', lambda e: self.reset_game())
        
        # Make sure the window can receive key events
        self.root.focus_set()
    
    def save_game_state(self):
        """Save current game state to file"""
        try:
            state = {
                'balance': self.balance,
                'current_bet': self.current_bet,
                'mines_count': self.mines_count
            }
            with open('mines_game_save.json', 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logging.warning(f"Could not save game state: {e}")
    
    def load_game_state(self):
        """Load saved game state from file"""
        try:
            if os.path.exists('mines_game_save.json'):
                with open('mines_game_save.json', 'r') as f:
                    state = json.load(f)
                self.balance = state.get('balance', 1000.0)
                self.current_bet = state.get('current_bet', 10.0)
                self.mines_count = state.get('mines_count', 3)
        except Exception as e:
            logging.warning(f"Could not load game state: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.save_game_state()
        self.root.destroy()
    
    def run(self):
        """Start the game"""
        self.setup_keyboard_shortcuts()
        self.root.mainloop()

    def show_rules(self):
        print("Mines Game Rules: Set your bet and number of mines. Reveal safe tiles to increase multiplier. Cash out anytime. Hitting a mine ends the game.")

def main():
    """Main function to run the desktop Mines game"""
    game = MinesGame()
    game.run()

if __name__ == "__main__":
    main()