import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import secrets
import threading
import time
import os
from casino_game import CasinoGame

SLOT_SYMBOLS = [
    '🍒', '🔔', '🍋', '⭐', '💎', '7️⃣', '🍀', 'BAR'
]
SYMBOL_MULTIPLIERS = {
    '🍒': 2,
    '🔔': 3,
    '🍋': 4,
    '⭐': 5,
    '💎': 10,
    '7️⃣': 20,
    '🍀': 8,
    'BAR': 15
}

class SlotsGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = value

    def __init__(self, player_balance=5000):
        super().__init__(player_balance)
        self.root = tk.Tk()
        self.root.title("Slots Machine")
        self.root.geometry("500x650")
        self.root.configure(bg="#181c23")
        self.bet_amount = tk.DoubleVar(value=10.0)
        self.is_spinning = False
        self.grid_symbols = [[None]*3 for _ in range(3)]
        self.history = []
        self.setup_ui()
        self.update_display()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Header
        header = tk.Frame(self.root, bg="#23273a")
        header.pack(fill=tk.X, pady=10)
        tk.Label(header, text="🎰 SLOTS MACHINE", fg="#ffd700", bg="#23273a", font=("Arial", 18, "bold")).pack()
        # Balance
        self.balance_label = tk.Label(self.root, text=f"Balance: ${self.balance:,.2f}", fg="#ffd700", bg="#181c23", font=("Arial", 14, "bold"))
        self.balance_label.pack(pady=5)
        # Bet controls
        bet_frame = tk.Frame(self.root, bg="#181c23")
        bet_frame.pack(pady=10)
        tk.Label(bet_frame, text="Bet Amount:", fg="#fff", bg="#181c23", font=("Arial", 12)).pack(side=tk.LEFT)
        bet_entry = tk.Entry(bet_frame, textvariable=self.bet_amount, width=8, font=("Arial", 12), bg="#23273a", fg="#ffd700", insertbackground="#ffd700")
        bet_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(bet_frame, text="½", command=self.half_bet, bg="#ffd700", fg="#23273a", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(bet_frame, text="2x", command=self.double_bet, bg="#ffd700", fg="#23273a", width=3).pack(side=tk.LEFT, padx=2)
        # Slot grid
        self.grid_frame = tk.Frame(self.root, bg="#23273a", bd=4, relief=tk.RIDGE)
        self.grid_frame.pack(pady=20)
        self.symbol_labels = [[None]*3 for _ in range(3)]
        for r in range(3):
            for c in range(3):
                lbl = tk.Label(self.grid_frame, text="❓", font=("Arial", 36, "bold"), width=3, height=1, bg="#181c23", fg="#fff", bd=2, relief=tk.GROOVE)
                lbl.grid(row=r, column=c, padx=8, pady=8)
                self.symbol_labels[r][c] = lbl
        # Spin button
        self.spin_btn = tk.Button(self.root, text="SPIN", command=self.spin, font=("Arial", 16, "bold"), bg="#ffd700", fg="#23273a", width=12, height=2)
        self.spin_btn.pack(pady=10)
        # History
        self.history_label = tk.Label(self.root, text="", fg="#fff", bg="#181c23", font=("Arial", 10))
        self.history_label.pack(pady=5)
        # Stats
        self.stats_label = tk.Label(self.root, text="", fg="#ffd700", bg="#181c23", font=("Arial", 10, "bold"))
        self.stats_label.pack(pady=5)
        # Tooltips and help
        tk.Label(self.root, text="Tip: Win by matching lines!", fg="#0dcaf0", bg="#181c23", font=("Arial", 9)).pack(pady=2)

    def update_display(self):
        self.balance_label.config(text=f"Balance: ${self.balance:,.2f}")
        self.stats_label.config(text=f"Total Spins: {len(self.history)} | Last Win: {self.history[-1]['win'] if self.history else 0}")
        if self.history:
            self.history_label.config(text=f"Last: {self.history[-1]['result']} | Bet: ${self.history[-1]['bet']} | Win: ${self.history[-1]['win']}")
        else:
            self.history_label.config(text="")

    def half_bet(self):
        self.bet_amount.set(max(1, self.bet_amount.get() / 2))
        self.update_display()

    def double_bet(self):
        self.bet_amount.set(min(self.balance, self.bet_amount.get() * 2))
        self.update_display()

    def spin(self):
        if self.is_spinning:
            return
        bet = self.bet_amount.get()
        if bet <= 0 or bet > self.balance:
            messagebox.showerror("Invalid Bet", "Please enter a valid bet amount.")
            return
        self.is_spinning = True
        self.spin_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._spin_animation, args=(bet,), daemon=True).start()

    def _spin_animation(self, bet):
        # Animate reels
        for t in range(15):
            for r in range(3):
                for c in range(3):
                    symbol = secrets.choice(SLOT_SYMBOLS)
                    self.symbol_labels[r][c].config(text=symbol, fg="#fff")
            time.sleep(0.07 + t*0.01)
        # Final outcome
        grid = [[secrets.choice(SLOT_SYMBOLS) for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.symbol_labels[r][c].config(text=grid[r][c], fg="#ffd700")
        win, result, lines = self.calculate_win(grid, bet)
        self.balance -= bet
        self.balance += win
        self.history.append({'result': result, 'bet': bet, 'win': win})
        self.is_spinning = False
        self.spin_btn.config(state=tk.NORMAL)
        self.update_display()
        if win > 0:
            self._show_win_animation(lines)
            # TODO: Play win sound
        else:
            # TODO: Play lose sound
            pass

    def calculate_win(self, grid, bet):
        lines = self.get_winning_lines(grid)
        total_multiplier = sum(SYMBOL_MULTIPLIERS[grid[r][c]] for (r, c) in lines) if lines else 0
        win = bet * total_multiplier if total_multiplier else 0
        result = f"{'WIN' if win else 'LOSE'} ({len(lines)} lines)"
        return win, result, lines

    def get_winning_lines(self, grid):
        lines = []
        # Rows
        for r in range(3):
            if grid[r][0] == grid[r][1] == grid[r][2]:
                lines.extend([(r, 0), (r, 1), (r, 2)])
        # Columns
        for c in range(3):
            if grid[0][c] == grid[1][c] == grid[2][c]:
                lines.extend([(0, c), (1, c), (2, c)])
        # Diagonals
        if grid[0][0] == grid[1][1] == grid[2][2]:
            lines.extend([(0, 0), (1, 1), (2, 2)])
        if grid[0][2] == grid[1][1] == grid[2][0]:
            lines.extend([(0, 2), (1, 1), (2, 0)])
        return lines

    def _show_win_animation(self, lines):
        for (r, c) in lines:
            self.symbol_labels[r][c].config(bg="#238636")
        self.root.after(800, lambda: [self.symbol_labels[r][c].config(bg="#181c23") for (r, c) in lines])

    def on_closing(self):
        self.root.destroy()

    def start_game(self):
        self.root.mainloop()

    def show_rules(self):
        messagebox.showinfo("Slots Rules", "Spin the reels. Match 3 symbols in a row, column, or diagonal to win! Each symbol has a different multiplier. Good luck!") 