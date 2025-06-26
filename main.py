import tkinter as tk
from baccarat_game.baccarat_game import BaccaratGame
from color_game.color_game import ColorGame
from mines_game.mines_game import MinesGame
import json
import os

game_classes = {
    'Baccarat': BaccaratGame,
    'Color Game': ColorGame,
    'Mines': MinesGame
}

class CasinoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Casino App")
        self.root.geometry("400x400")
        self.selected_game = tk.StringVar(value='Baccarat')
        self.shared_balance = self.load_shared_balance()
        self.setup_ui()

    def setup_ui(self):
        label = tk.Label(self.root, text="Welcome to the Casino!", font=("Arial", 18, "bold"))
        label.pack(pady=20)

        # Balance display
        balance_label = tk.Label(self.root, text=f"Current Balance: ${self.shared_balance:,.2f}", font=("Arial", 14))
        balance_label.pack(pady=10)

        # Game selection
        for game_name in game_classes:
            rb = tk.Radiobutton(self.root, text=game_name, variable=self.selected_game, value=game_name, font=("Arial", 14))
            rb.pack(anchor=tk.W, padx=40)

        start_button = tk.Button(self.root, text="Start Game", font=("Arial", 14, "bold"), command=self.launch_game)
        start_button.pack(pady=30)

        rules_button = tk.Button(self.root, text="Show Rules", font=("Arial", 12), command=self.show_rules)
        rules_button.pack()

    def launch_game(self):
        game_name = self.selected_game.get()
        game_class = game_classes[game_name]
        self.root.withdraw()  # Hide main menu instead of destroying
        game_instance = game_class(self.shared_balance)
        game_instance.start_game()
        # Update shared balance after game ends
        self.shared_balance = game_instance.balance
        self.save_shared_balance()
        self.root.deiconify()  # Show main menu again
        self.setup_ui()  # Refresh UI to show updated balance

    def show_rules(self):
        game_name = self.selected_game.get()
        game_class = game_classes[game_name]
        game_instance = game_class(self.shared_balance)
        game_instance.show_rules()

    def load_shared_balance(self):
        try:
            if os.path.exists('casino_balance.json'):
                with open('casino_balance.json', 'r') as f:
                    data = json.load(f)
                    return data.get('balance', 5000.0)
        except Exception as e:
            print(f"Error loading balance: {e}")
        return 5000.0  # Default starting balance

    def save_shared_balance(self):
        try:
            with open('casino_balance.json', 'w') as f:
                json.dump({'balance': self.shared_balance}, f)
        except Exception as e:
            print(f"Error saving balance: {e}")

if __name__ == "__main__":
    app = CasinoApp()
    app.root.mainloop() 