from random import randrange


class BlackJack:
    def __init__(self):
        self.player_hand = []
        self.dealer_hand = []
        self.bet_amount = 0
        self.GAME_RESULTS = ["Win", "Lose", "Draw", "BlackJack"]
        self.game_result = ""
        self.deck = []

    def place_bet(self, bet):
        self.bet_amount = bet

    def calculate_points(self, hand):
        points = 0
        ace_counter = 0

        for card in hand:
            x = card.split("_")[0]
            if x == "jack" or x == "queen" or x == "king":
                points += 10
            elif x == "ace":
                points += 1
                ace_counter += 1
            else:
                points += int(x)

        if ace_counter == 1:
            if (points + 10) > 21:
                return str(points)
            else:
                points = f"{str(points)}/{str(points + 10)}"

        return str(points)

    def create_deck(self):
        SUITS = ["diamonds", "spades", "hearts", "clubs"]
        CARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]

        for suit in SUITS:
            for card in CARDS:
                suite_cards = f"{card}_of_{suit}"
                self.deck.append(suite_cards)

    def draw_card(self):
        if len(self.deck) == 0:
            self.shuffle_deck()

        card = self.deck.pop(randrange(0, len(self.deck)))

        yield card

    def calculate_winnings(self):
        def calculate_winnings(multi):
            return lambda x: x * multi
        if self.game_result == "Win":
            multiplier = 2
        elif self.game_result == "Draw":
            multiplier = 1
        elif self.game_result == "BlackJack":
            multiplier = 2.5
        else:
            multiplier = 0

        winnings = calculate_winnings(multiplier)

        return winnings(float(self.bet_amount))

    def new_game(self):
        self.player_hand.clear()
        self.dealer_hand.clear()
        self.bet_amount = 0
        self.game_result = ""

    def shuffle_deck(self):
        self.deck.clear()
        self.create_deck()
