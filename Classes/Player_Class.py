from datetime import datetime


class Player:
    def __init__(self, first_name, last_name, email, password, balance=0, total_games_played=0, total_wins=0, total_losses=0, total_draws=0):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.balance = balance
        self.total_wins = total_wins
        self.total_losses = total_losses
        self.total_games_played = total_games_played
        self.last_login = datetime.now()
        self.total_draws = total_draws

    def add_money(self, deposit):
        self.balance += deposit

    def remove_money(self, withdrawal):
        self.balance -= withdrawal

    def get_win_loss_ratio(self):
        return round((self.total_wins/self.total_games_played) * 100, 2)

    def update_games_played(self):
        self.total_games_played += 1

    def update_total_wins(self):
        self.total_wins += 1

    def update_total_losses(self):
        self.total_losses += 1

    def update_total_draws(self):
        self.total_draws += 1
