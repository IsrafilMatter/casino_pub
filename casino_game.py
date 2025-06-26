from abc import ABC as AbstractBaseCasinoGame, abstractmethod

class CasinoGame(AbstractBaseCasinoGame):
    def __init__(self, player_account_balance):
        self._player_account_balance = player_account_balance

    @abstractmethod
    def start_game(self):
        pass

    @abstractmethod
    def show_rules(self):
        pass

    def get_balance(self):
        return self._player_account_balance

    def set_balance(self, new_balance):
        self._player_account_balance = new_balance 