import tkinter as tk
from tkinter import messagebox, ttk
import secrets
import threading
import time
from casino_game import CasinoGame

class DiceGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = value

    def __init__(self, player_balance=5000):
        super().__init__(player_balance)
        self.root = tk.Tk()
        self.root.title("Crypto Dice Game")
        self.root.geometry("500x600")
        self.root.configure(bg="#181c23")
        self.bet_amount = tk.DoubleVar(value=10.0)
        self.chosen_number = tk.IntVar(value=50)
        self.over_under = tk.StringVar(value="over")
        self.is_rolling = False
        self.history = []
        self.setup_ui()
        self.update_display()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        header = tk.Frame(self.root, bg="#23273a")
        header.pack(fill=tk.X, pady=10)
        tk.Label(header, text="🎲 CRYPTO DICE", fg="#0dcaf0", bg="#23273a", font=("Arial", 18, "bold")).pack()
        self.balance_label = tk.Label(self.root, text=f"Balance: ${self.balance:,.2f}", fg="#ffd700", bg="#181c23", font=("Arial", 14, "bold"))
        self.balance_label.pack(pady=5)
        bet_frame = tk.Frame(self.root, bg="#181c23")
        bet_frame.pack(pady=10)
        tk.Label(bet_frame, text="Bet Amount:", fg="#fff", bg="#181c23", font=("Arial", 12)).pack(side=tk.LEFT)
        bet_entry = tk.Entry(bet_frame, textvariable=self.bet_amount, width=8, font=("Arial", 12), bg="#23273a", fg="#ffd700", insertbackground="#ffd700")
        bet_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(bet_frame, text="½", command=self.half_bet, bg="#ffd700", fg="#23273a", width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(bet_frame, text="2x", command=self.double_bet, bg="#ffd700", fg="#23273a", width=3).pack(side=tk.LEFT, padx=2)
        # Over/Under controls
        ou_frame = tk.Frame(self.root, bg="#181c23")
        ou_frame.pack(pady=5)
        tk.Label(ou_frame, text="Choose Number (1-100):", fg="#fff", bg="#181c23", font=("Arial", 12)).pack(side=tk.LEFT)
        num_spin = tk.Spinbox(ou_frame, from_=1, to=100, textvariable=self.chosen_number, width=5, font=("Arial", 12), bg="#23273a", fg="#ffd700")
        num_spin.pack(side=tk.LEFT, padx=5)
        over_btn = tk.Radiobutton(ou_frame, text="Over", variable=self.over_under, value="over", fg="#0dcaf0", bg="#181c23", selectcolor="#23273a", font=("Arial", 12, "bold"))
        over_btn.pack(side=tk.LEFT, padx=5)
        under_btn = tk.Radiobutton(ou_frame, text="Under", variable=self.over_under, value="under", fg="#ffd700", bg="#181c23", selectcolor="#23273a", font=("Arial", 12, "bold"))
        under_btn.pack(side=tk.LEFT, padx=5)
        # Probability and payout
        self.prob_label = tk.Label(self.root, text="", fg="#0dcaf0", bg="#181c23", font=("Arial", 12, "bold"))
        self.prob_label.pack(pady=5)
        # Roll button
        self.roll_btn = tk.Button(self.root, text="ROLL", command=self.roll, font=("Arial", 16, "bold"), bg="#0dcaf0", fg="#23273a", width=12, height=2)
        self.roll_btn.pack(pady=10)
        # Result display
        self.result_label = tk.Label(self.root, text="", fg="#fff", bg="#181c23", font=("Arial", 16, "bold"))
        self.result_label.pack(pady=5)
        # History
        self.history_label = tk.Label(self.root, text="", fg="#fff", bg="#181c23", font=("Arial", 10))
        self.history_label.pack(pady=5)
        # Tooltips
        tk.Label(self.root, text="Tip: Bet over/under your number. Win if the dice lands in your range!", fg="#0dcaf0", bg="#181c23", font=("Arial", 9)).pack(pady=2)
        # Bindings
        self.chosen_number.trace_add('write', lambda *args: self.update_display())
        self.over_under.trace_add('write', lambda *args: self.update_display())

    def update_display(self):
        self.balance_label.config(text=f"Balance: ${self.balance:,.2f}")
        num = self.chosen_number.get()
        ou = self.over_under.get()
        if ou == "over":
            prob = (100 - num) / 100
        else:
            prob = (num - 1) / 100
        payout = round((1 / prob) * 0.98, 2) if prob > 0 else 0
        self.prob_label.config(text=f"Win Chance: {prob*100:.2f}% | Payout: x{payout}")
        if self.history:
            last = self.history[-1]
            self.history_label.config(text=f"Last: {last['result']} | Roll: {last['roll']} | Bet: ${last['bet']} | Win: ${last['win']}")
        else:
            self.history_label.config(text="")

    def half_bet(self):
        self.bet_amount.set(max(1, self.bet_amount.get() / 2))
        self.update_display()

    def double_bet(self):
        self.bet_amount.set(min(self.balance, self.bet_amount.get() * 2))
        self.update_display()

    def roll(self):
        if self.is_rolling:
            return
        bet = self.bet_amount.get()
        if bet <= 0 or bet > self.balance:
            messagebox.showerror("Invalid Bet", "Please enter a valid bet amount.")
            return
        self.is_rolling = True
        self.roll_btn.config(state=tk.DISABLED)
        self.result_label.config(text="Rolling...")
        threading.Thread(target=self._roll_animation, args=(bet,), daemon=True).start()

    def _roll_animation(self, bet):
        for t in range(10):
            roll = secrets.randbelow(100) + 1
            self.result_label.config(text=f"🎲 {roll}")
            time.sleep(0.07 + t*0.01)
        # Final roll
        roll = secrets.randbelow(100) + 1
        num = self.chosen_number.get()
        ou = self.over_under.get()
        if ou == "over":
            win = roll > num
            prob = (100 - num) / 100
        else:
            win = roll < num
            prob = (num - 1) / 100
        payout = round((1 / prob) * 0.98, 2) if prob > 0 else 0
        win_amt = bet * payout if win else 0
        self.balance -= bet
        self.balance += win_amt
        result = "WIN" if win else "LOSE"
        self.history.append({'result': result, 'roll': roll, 'bet': bet, 'win': win_amt})
        self.is_rolling = False
        self.roll_btn.config(state=tk.NORMAL)
        self.result_label.config(text=f"🎲 {roll} | {result} {'+${:.2f}'.format(win_amt) if win else ''}")
        self.update_display()
        # TODO: Play win/lose sound

    def on_closing(self):
        self.root.destroy()

    def start_game(self):
        self.root.mainloop()

    def show_rules(self):
        messagebox.showinfo("Dice Rules", "Choose a number and bet over or under. If the dice lands in your range, you win! Payout is based on probability.") 