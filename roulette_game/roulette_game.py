import tkinter as tk
from tkinter import messagebox
import secrets
import threading
import time
from casino_game import CasinoGame

ROULETTE_NUMBERS = [
    '00', '0', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36
]
RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

CHIP_VALUES = [1, 5, 10, 25, 100, 500]

PAYOUTS = {
    'straight': 35,
    'split': 17,
    'street': 11,
    'corner': 8,
    'line': 5,
    'dozen': 2,
    'column': 2,
    'red': 1,
    'black': 1,
    'even': 1,
    'odd': 1,
    'low': 1,
    'high': 1
}

class RouletteGame(CasinoGame):
    @property
    def balance(self):
        return self._player_account_balance

    @balance.setter
    def balance(self, value):
        self._player_account_balance = value

    def __init__(self, player_balance=5000):
        super().__init__(player_balance)
        self.root = tk.Tk()
        self.root.title("Roulette Game")
        self.root.geometry("900x700")
        self.root.configure(bg="#181c23")
        self.selected_chip = tk.IntVar(value=CHIP_VALUES[0])
        self.bets = {}  # {(bet_type, bet_value): amount}
        self.is_spinning = False
        self.history = []
        self.last_result = None
        self.setup_ui()
        self.update_display()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        header = tk.Frame(self.root, bg="#23273a")
        header.pack(fill=tk.X, pady=10)
        tk.Label(header, text="🎡 ROULETTE", fg="#ffd700", bg="#23273a", font=("Arial", 18, "bold")).pack()
        self.balance_label = tk.Label(self.root, text=f"Balance: ${self.balance:,.2f}", fg="#ffd700", bg="#181c23", font=("Arial", 14, "bold"))
        self.balance_label.pack(pady=5)
        # Chips
        chip_frame = tk.Frame(self.root, bg="#181c23")
        chip_frame.pack(pady=5)
        tk.Label(chip_frame, text="Select Chip:", fg="#fff", bg="#181c23", font=("Arial", 12)).pack(side=tk.LEFT)
        for val in CHIP_VALUES:
            btn = tk.Radiobutton(chip_frame, text=f"${val}", variable=self.selected_chip, value=val, fg="#23273a", bg="#ffd700", selectcolor="#ffd700", font=("Arial", 12, "bold"))
            btn.pack(side=tk.LEFT, padx=5)
        # Betting table
        table_frame = tk.Frame(self.root, bg="#181c23")
        table_frame.pack(pady=10)
        self.bet_buttons = {}
        # Numbers grid (3 rows x 12 cols)
        for r in range(3):
            for c in range(12):
                num = 3*c + (3-r)
                if num == 0:
                    continue
                btn = tk.Button(table_frame, text=str(num), width=4, height=2,
                                 bg="#dc2626" if num in RED_NUMBERS else ("#23273a" if num in BLACK_NUMBERS else "#0dcaf0"),
                                 fg="#fff", font=("Arial", 10, "bold"),
                                 command=lambda n=num: self.place_bet('straight', n))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.bet_buttons[("straight", num)] = btn
        # 0 and 00
        btn0 = tk.Button(table_frame, text="0", width=4, height=2, bg="#0dcaf0", fg="#fff", font=("Arial", 10, "bold"), command=lambda: self.place_bet('straight', 0))
        btn0.grid(row=0, column=12, rowspan=2, padx=2, pady=2)
        self.bet_buttons[("straight", 0)] = btn0
        btn00 = tk.Button(table_frame, text="00", width=4, height=2, bg="#0dcaf0", fg="#fff", font=("Arial", 10, "bold"), command=lambda: self.place_bet('straight', '00'))
        btn00.grid(row=2, column=12, padx=2, pady=2)
        self.bet_buttons[("straight", '00')] = btn00
        # Dozens, columns, outside bets
        outside_frame = tk.Frame(self.root, bg="#181c23")
        outside_frame.pack(pady=5)
        # Dozens
        for i, label in enumerate(["1st 12", "2nd 12", "3rd 12"]):
            btn = tk.Button(outside_frame, text=label, width=8, bg="#23273a", fg="#ffd700", font=("Arial", 10, "bold"), command=lambda d=i+1: self.place_bet('dozen', d))
            btn.grid(row=0, column=i, padx=5, pady=2)
            self.bet_buttons[("dozen", i+1)] = btn
        # Columns
        for i, label in enumerate(["1st Col", "2nd Col", "3rd Col"]):
            btn = tk.Button(outside_frame, text=label, width=8, bg="#23273a", fg="#ffd700", font=("Arial", 10, "bold"), command=lambda c=i+1: self.place_bet('column', c))
            btn.grid(row=1, column=i, padx=5, pady=2)
            self.bet_buttons[("column", i+1)] = btn
        # Red/Black, Even/Odd, High/Low
        for i, (label, btype) in enumerate([
            ("Red", 'red'), ("Black", 'black'), ("Even", 'even'), ("Odd", 'odd'), ("1-18", 'low'), ("19-36", 'high')
        ]):
            btn = tk.Button(outside_frame, text=label, width=8, bg="#dc2626" if btype=="red" else ("#23273a" if btype=="black" else "#0dcaf0"), fg="#fff", font=("Arial", 10, "bold"), command=lambda t=btype: self.place_bet(t, None))
            btn.grid(row=2, column=i, padx=5, pady=2)
            self.bet_buttons[(btype, None)] = btn
        # Bets display
        self.bets_label = tk.Label(self.root, text="", fg="#0dcaf0", bg="#181c23", font=("Arial", 12, "bold"))
        self.bets_label.pack(pady=5)
        # Spin button
        self.spin_btn = tk.Button(self.root, text="SPIN WHEEL", command=self.spin, font=("Arial", 16, "bold"), bg="#ffd700", fg="#23273a", width=16, height=2)
        self.spin_btn.pack(pady=10)
        # Result display
        self.result_label = tk.Label(self.root, text="", fg="#fff", bg="#181c23", font=("Arial", 16, "bold"))
        self.result_label.pack(pady=5)
        # History
        self.history_label = tk.Label(self.root, text="", fg="#fff", bg="#181c23", font=("Arial", 10))
        self.history_label.pack(pady=5)
        # Tooltips
        tk.Label(self.root, text="Tip: Click a number or bet type to place a bet. Multiple bets allowed.", fg="#0dcaf0", bg="#181c23", font=("Arial", 9)).pack(pady=2)

    def update_display(self):
        self.balance_label.config(text=f"Balance: ${self.balance:,.2f}")
        bets_str = ", ".join([f"{k[0]} {k[1] if k[1] is not None else ''}: ${v}" for k,v in self.bets.items()])
        self.bets_label.config(text=f"Bets: {bets_str if bets_str else 'None'}")
        if self.history:
            last = self.history[-1]
            self.history_label.config(text=f"Last: {last['result']} | Number: {last['number']} | Win: ${last['win']}")
        else:
            self.history_label.config(text="")

    def place_bet(self, bet_type, bet_value):
        if self.is_spinning:
            return
        chip = self.selected_chip.get()
        total_bet = sum(self.bets.values()) + chip
        if chip > self.balance or total_bet > self.balance:
            messagebox.showerror("Invalid Bet", "Not enough balance for this bet.")
            return
        key = (bet_type, bet_value)
        self.bets[key] = self.bets.get(key, 0) + chip
        self.update_display()

    def spin(self):
        if self.is_spinning or not self.bets:
            messagebox.showerror("No Bets", "Place at least one bet before spinning.")
            return
        self.is_spinning = True
        self.spin_btn.config(state=tk.DISABLED)
        self.result_label.config(text="Spinning...")
        threading.Thread(target=self._spin_animation, daemon=True).start()

    def _spin_animation(self):
        for t in range(20):
            n = secrets.choice(ROULETTE_NUMBERS)
            self.result_label.config(text=f"🎡 {n}")
            time.sleep(0.05 + t*0.01)
        # Final outcome
        number = secrets.choice(ROULETTE_NUMBERS)
        self.last_result = number
        win = self.calculate_win(number)
        self.balance -= sum(self.bets.values())
        self.balance += win
        self.history.append({'result': 'WIN' if win > 0 else 'LOSE', 'number': number, 'win': win})
        self.is_spinning = False
        self.spin_btn.config(state=tk.NORMAL)
        self.result_label.config(text=f"🎡 {number} | {'WIN' if win > 0 else 'LOSE'} {'+${:.2f}'.format(win) if win else ''}")
        self.bets.clear()
        self.update_display()
        # TODO: Play win/lose sound

    def calculate_win(self, number):
        total_win = 0
        for (bet_type, bet_value), amount in self.bets.items():
            if bet_type == 'straight':
                if str(number) == str(bet_value):
                    total_win += amount * (PAYOUTS['straight'] + 1)
            elif bet_type == 'dozen':
                if bet_value == 1 and number in range(1,13):
                    total_win += amount * (PAYOUTS['dozen'] + 1)
                elif bet_value == 2 and number in range(13,25):
                    total_win += amount * (PAYOUTS['dozen'] + 1)
                elif bet_value == 3 and number in range(25,37):
                    total_win += amount * (PAYOUTS['dozen'] + 1)
            elif bet_type == 'column':
                if bet_value == 1 and number in [1,4,7,10,13,16,19,22,25,28,31,34]:
                    total_win += amount * (PAYOUTS['column'] + 1)
                elif bet_value == 2 and number in [2,5,8,11,14,17,20,23,26,29,32,35]:
                    total_win += amount * (PAYOUTS['column'] + 1)
                elif bet_value == 3 and number in [3,6,9,12,15,18,21,24,27,30,33,36]:
                    total_win += amount * (PAYOUTS['column'] + 1)
            elif bet_type == 'red' and number in RED_NUMBERS:
                total_win += amount * (PAYOUTS['red'] + 1)
            elif bet_type == 'black' and number in BLACK_NUMBERS:
                total_win += amount * (PAYOUTS['black'] + 1)
            elif bet_type == 'even' and isinstance(number, int) and number % 2 == 0 and number != 0:
                total_win += amount * (PAYOUTS['even'] + 1)
            elif bet_type == 'odd' and isinstance(number, int) and number % 2 == 1:
                total_win += amount * (PAYOUTS['odd'] + 1)
            elif bet_type == 'low' and isinstance(number, int) and 1 <= number <= 18:
                total_win += amount * (PAYOUTS['low'] + 1)
            elif bet_type == 'high' and isinstance(number, int) and 19 <= number <= 36:
                total_win += amount * (PAYOUTS['high'] + 1)
        return total_win

    def on_closing(self):
        self.root.destroy()

    def start_game(self):
        self.root.mainloop()

    def show_rules(self):
        messagebox.showinfo("Roulette Rules", "Place bets on numbers, colors, or groups. Spin the wheel. If the ball lands on your bet, you win! Payouts depend on bet type.") 