import tkinter as tk
from PIL import Image, ImageTk
from baccarat_game.baccarat_game import BaccaratGame
from color_game.color_game import ColorGame
from mines_game.mines_game import MinesGame
from slots_game.slots_game import SlotsGame
from dice_game.dice_game import DiceGame
from crash_game.crash_game import CrashGame
from roulette_game.roulette_game import RouletteGame
import json
import os
import threading
import pygame

game_classes = {
    'Baccarat': BaccaratGame,
    'Mines': MinesGame,
    'Color Game': ColorGame,
    'Slots': SlotsGame,
    'Dice': DiceGame,
    'Crash': CrashGame,
    'Roulette': RouletteGame
}

game_images = {
    'Baccarat': 'baccarat_game/assets/BaccaratTable.jpg',
    'Mines': 'baccarat_game/assets/pokerchip1.png',
    'Color Game': 'baccarat_game/assets/pokerchip3.png',
    'Slots': None,  # Use emoji or placeholder
    'Dice': None,   # Use emoji or placeholder
    'Crash': None,  # Use emoji or placeholder
    'Roulette': None  # Use emoji or placeholder
}

class CasinoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Casino App")
        self.root.configure(bg="#181c23")
        self.root.geometry("600x400")
        self.root.minsize(400, 300)
        self.selected_game = None
        self.shared_balance = self.load_shared_balance()
        self.music_thread = None
        self.music_playing = False
        self.setup_ui()
        self.start_background_music()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Top Navigation Bar
        nav = tk.Frame(self.root, bg="#23273a", height=50)
        nav.pack(fill=tk.X, side=tk.TOP)
        tk.Label(nav, text="🎮 Lobby", fg="#fff", bg="#23273a", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)

        # Recent Section
        recent = tk.Frame(self.root, bg="#181c23")
        recent.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(recent, text="🎮 Recent", fg="#fff", bg="#181c23", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        # Game Cards
        cards = tk.Frame(recent, bg="#181c23")
        cards.pack()
        for game_name in game_classes:
            img_path = game_images[game_name]
            if img_path:
                self.add_game_card(cards, game_name, img_path)
            else:
                self.add_game_card(cards, game_name, None)

        # Balance display at the bottom
        balance_label = tk.Label(self.root, text=f"Current Balance: ${self.shared_balance:,.2f}", font=("Arial", 14), fg="#ffd700", bg="#181c23")
        balance_label.pack(side=tk.BOTTOM, pady=10)

    def add_game_card(self, parent, name, img_path):
        card = tk.Frame(parent, bg="#23273a", bd=0, relief=tk.RIDGE, cursor="hand2")
        card.pack(side=tk.LEFT, padx=10)
        if img_path:
            try:
                from PIL import Image, ImageTk
                img = Image.open(img_path).resize((80, 80))
                photo = ImageTk.PhotoImage(img)
                label_img = tk.Label(card, image=photo, bg="#23273a")
                label_img.image = photo
                label_img.pack()
            except Exception:
                tk.Label(card, text="No Img", bg="#23273a", fg="#fff").pack()
        else:
            # Use emoji for special games
            emoji = (
                "🎰" if name == "Slots" else
                "🎲" if name == "Dice" else
                "🚀" if name == "Crash" else
                "🎡" if name == "Roulette" else
                "❓"
            )
            tk.Label(card, text=emoji, font=("Arial", 36), bg="#23273a", fg="#ffd700").pack()
        tk.Label(card, text=name.upper(), fg="#fff", bg="#23273a", font=("Arial", 10, "bold")).pack(pady=5)
        card.bind("<Button-1>", lambda e, g=name: self.launch_game(g))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, g=name: self.launch_game(g))

    def launch_game(self, game_name):
        game_class = game_classes[game_name]
        self.root.withdraw()  # Hide main menu instead of destroying
        game_instance = game_class(self.shared_balance)
        game_instance.start_game()
        # Update shared balance after game ends
        self.shared_balance = game_instance.balance
        self.save_shared_balance()
        self.root.deiconify()  # Show main menu again
        self.setup_ui()  # Refresh UI to show updated balance

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

    def start_background_music(self):
        def play_music():
            try:
                pygame.mixer.init()
                pygame.mixer.music.load('baccarat_game/assets/Las Vegas Casino Music.mp3')
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception as e:
                print(f"Error playing music: {e}")
        if not pygame.mixer.get_init():
            self.music_thread = threading.Thread(target=play_music, daemon=True)
            self.music_thread.start()
        else:
            try:
                pygame.mixer.music.load('baccarat_game/assets/Las Vegas Casino Music.mp3')
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception as e:
                print(f"Error playing music: {e}")

    def stop_background_music(self):
        try:
            if pygame.mixer.get_init() and self.music_playing:
                pygame.mixer.music.stop()
                self.music_playing = False
        except Exception as e:
            print(f"Error stopping music: {e}")

    def on_closing(self):
        self.stop_background_music()
        self.root.destroy()

if __name__ == "__main__":
    app = CasinoApp()
    app.root.mainloop() 