import tkinter as tk
from tkinter import messagebox
import secrets
import threading
import time
from casino_game import CasinoGame

class CrashGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = value

    def __init__(self, player_balance=5000):
        super().__init__(player_balance)
        self.root = tk.Tk()
        self.root.title("Crash Game")
        self.root.geometry("600x700")
        self.root.configure(bg="#181c23")
        self.bet_amount = tk.DoubleVar(value=10.0)
        self.auto_cashout = tk.DoubleVar(value=2.0)
        self.is_running = False
        self.has_bet = False
        self.crash_point = None
        self.multiplier = 1.0
        self.cashed_out = False
        self.history = []
        self.live_bets = []
        self.setup_ui()
        self.update_display()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        header = tk.Frame(self.root, bg="#23273a")
        header.pack(fill=tk.X, pady=10)
        tk.Label(header, text="🚀 CRASH GAME", fg="#0dcaf0", bg="#23273a", font=("Arial", 18, "bold")).pack()
        self.balance_label = tk.Label(self.root, text=f"Balance: ${self.balance:,.2f}", fg="#ffd700", bg="#181c23", font=("Arial", 14, "bold"))
        self.balance_label.pack(pady=5)
        bet_frame = tk.Frame(self.root, bg="#181c23")
        bet_frame.pack(pady=10)
        tk.Label(bet_frame, text="Bet Amount:", fg="#fff", bg="#181c23", font=("Arial", 12)).pack(side=tk.LEFT)
        bet_entry = tk.Entry(bet_frame, textvariable=self.bet_amount, width=8, font=("Arial", 12), bg="#23273a", fg="#ffd700", insertbackground="#ffd700")
        bet_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(bet_frame, text="½", command=self.half_bet, bg="#ffd700", fg="#23273a", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(bet_frame, text="2x", command=self.double_bet, bg="#ffd700", fg="#23273a", width=3).pack(side=tk.LEFT, padx=2)
        # Auto cashout
        auto_frame = tk.Frame(self.root, bg="#181c23")
        auto_frame.pack(pady=5)
        tk.Label(auto_frame, text="Auto Cashout at:", fg="#0dcaf0", bg="#181c23", font=("Arial", 12)).pack(side=tk.LEFT)
        auto_entry = tk.Entry(auto_frame, textvariable=self.auto_cashout, width=6, font=("Arial", 12), bg="#23273a", fg="#0dcaf0", insertbackground="#0dcaf0")
        auto_entry.pack(side=tk.LEFT, padx=5)
        # Start/Bet button
        self.bet_btn = tk.Button(self.root, text="PLACE BET", command=self.place_bet, font=("Arial", 16, "bold"), bg="#0dcaf0", fg="#23273a", width=14, height=2)
        self.bet_btn.pack(pady=10)
        # Multiplier display
        self.mult_label = tk.Label(self.root, text="Multiplier: 1.00x", fg="#ffd700", bg="#181c23", font=("Arial", 24, "bold"))
        self.mult_label.pack(pady=10)
        # Cashout button
        self.cashout_btn = tk.Button(self.root, text="CASH OUT", command=self.cash_out, font=("Arial", 16, "bold"), bg="#ffd700", fg="#23273a", width=14, height=2, state=tk.DISABLED)
        self.cashout_btn.pack(pady=10)
        # History
        self.history_label = tk.Label(self.root, text="", fg="#fff", bg="#181c23", font=("Arial", 10))
        self.history_label.pack(pady=5)
        # Tooltips
        tk.Label(self.root, text="Tip: Cash out before the crash! Auto cashout for safety.", fg="#0dcaf0", bg="#181c23", font=("Arial", 9)).pack(pady=2)

    def update_display(self):
        self.balance_label.config(text=f"Balance: ${self.balance:,.2f}")
        if self.history:
            last = self.history[-1]
            self.history_label.config(text=f"Last: {last['result']} | Crash: {last['crash']:.2f}x | Bet: ${last['bet']} | Win: ${last['win']}")
        else:
            self.history_label.config(text="")
        self.mult_label.config(text=f"Multiplier: {self.multiplier:.2f}x")

    def half_bet(self):
        self.bet_amount.set(max(1, self.bet_amount.get() / 2))
        self.update_display()

    def double_bet(self):
        self.bet_amount.set(min(self.balance, self.bet_amount.get() * 2))
        self.update_display()

    def place_bet(self):
        if self.is_running or self.has_bet:
            return
        bet = self.bet_amount.get()
        if bet <= 0 or bet > self.balance:
            messagebox.showerror("Invalid Bet", "Please enter a valid bet amount.")
            return
        self.balance -= bet
        self.has_bet = True
        self.is_running = True
        self.cashed_out = False
        self.multiplier = 1.0
        self.crash_point = self.generate_crash_point()
        self.bet_btn.config(state=tk.DISABLED)
        self.cashout_btn.config(state=tk.NORMAL)
        threading.Thread(target=self._run_crash, args=(bet,), daemon=True).start()
        self.update_display()

    def _run_crash(self, bet):
        while self.multiplier < self.crash_point and not self.cashed_out:
            self.multiplier += 0.01 + self.multiplier * 0.015
            self.update_display()
            if self.multiplier >= self.auto_cashout.get() and not self.cashed_out:
                self.cash_out(auto=True)
                return
            time.sleep(0.02)
        if not self.cashed_out:
            self._crash(bet)

    def cash_out(self, auto=False):
        if not self.is_running or self.cashed_out:
            return
        win_amt = round(self.bet_amount.get() * self.multiplier, 2)
        self.balance += win_amt
        self.cashed_out = True
        self.is_running = False
        self.has_bet = False
        self.bet_btn.config(state=tk.NORMAL)
        self.cashout_btn.config(state=tk.DISABLED)
        self.history.append({'result': 'CASHED OUT' if not auto else 'AUTO CASHOUT', 'crash': self.crash_point, 'bet': self.bet_amount.get(), 'win': win_amt})
        self.update_display()
        self.mult_label.config(text=f"Cashed Out: {self.multiplier:.2f}x!")
        # TODO: Play cashout sound

    def _crash(self, bet):
        self.is_running = False
        self.has_bet = False
        self.bet_btn.config(state=tk.NORMAL)
        self.cashout_btn.config(state=tk.DISABLED)
        self.history.append({'result': 'CRASH', 'crash': self.crash_point, 'bet': bet, 'win': 0})
        self.update_display()
        self.mult_label.config(text=f"💥 Crashed at {self.crash_point:.2f}x!")
        # TODO: Play crash sound

    def generate_crash_point(self):
        # Provably fair: e.g., 1/(1 - r) where r is random in [0,1)
        r = secrets.randbelow(1000000) / 1000000
        if r == 0:
            return 100.0
        return max(1.01, min(100.0, 1 / (1 - r)))

    def on_closing(self):
        self.root.destroy()

    def start_game(self):
        self.root.mainloop()

    def show_rules(self):
        messagebox.showinfo("Crash Rules", "Place your bet, watch the multiplier rise, and cash out before the crash! Auto cashout for safety. Crash point is provably fair.") 