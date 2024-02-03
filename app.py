from flask import Flask, render_template, url_for, request, session, redirect
import random

app = Flask(__name__)

class Card:
    def __init__(self, number):
        self.number = int(number)

    def __repr__(self):
        return str(self.number)

    def to_dict(self):
        return {'number': self.number}

class Deck:
    def __init__(self):
        self.cards = []

    def generate_deck(self):
        # Add 4 cards of each number from -1 to 8
        for number in range(-1, 9):
            for _ in range(4):
                self.cards.append(Card(number))

        # Add 12 cards with the numbers 9, 10, 11 representing crows
        for number in range(9, 12):
            for _ in range(4):
                self.cards.append(Card(number))

        # Shuffle the deck
        random.shuffle(self.cards)

class Game:
    def __init__(self):
        self.num_players = 2
        self.players = [[] for _ in range(2)]
        self.face_down_pile = []
        self.face_up_pile_1 = []
        self.face_up_pile_2 = []
        self.current_player = 0

    def switch_to_next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players

    def deal_cards(self, deck):
        for _ in range(6):
            for player in self.players:
                player.append(deck.cards.pop(0))

    def reveal_deck_cards(self, deck):
        card_1 = deck.cards.pop(0)
        card_2 = deck.cards.pop(0)
        card_3 = deck.cards.pop(0)
        self.face_up_pile_1.append(card_1)
        self.face_up_pile_2.append(card_2)
        self.face_down_pile.append(card_3)

    def take_face_up_card(self, pile_index):
        if pile_index == 1 and self.face_up_pile_1:
            card = self.face_up_pile_1.pop()
        elif pile_index == 2 and self.face_up_pile_2:
            card = self.face_up_pile_2.pop()
        else:
            return None  # Invalid pile_index

        # Perform actions based on the game rules
        self.players[self.current_player].append(card)
        self.fill_piles()
        self.switch_to_next_player()

        return card

    def fill_piles(self):

        while len(self.face_up_pile_1) < 2:
            self.face_up_pile_1.append(deck.cards.pop(0))

        while len(self.face_up_pile_2) < 2:
            self.face_up_pile_2.append(deck.cards.pop(0))

        while len(self.face_down_pile) < 2:
            self.face_down_pile.append(deck.cards.pop(0))

    def take_face_down_card(self):
        if not self.face_down_pile:
            return None  # No cards in the face-down pile

        card = self.face_down_pile.pop()

        # Perform actions based on the game rules
        if self.card_suits_player(card):
            self.players[self.current_player].append(card)
            self.fill_piles()
            self.switch_to_next_player()

        return card

    def card_suits_player(self, card):
        return True

@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        action = request.form['action']
        player_index = int(request.form['player_index'])
        pile_index = int(request.form['pile_index'])

        if action == 'take_face_up':
            card = game.take_face_up_card(pile_index)
        if action == 'take_face_down':
            card = game.take_face_down_card()
        else:
            card = None

        return render_template('game.html',
                               players=game.players,
                               current_player=game.current_player,
                               face_down_top=game.face_down_pile[-1] if game.face_down_pile else None,
                               face_up_top_1=game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
                               face_up_top_2=game.face_up_pile_2[-1] if game.face_up_pile_2 else None)

    return render_template('game.html',
                           players=game.players,
                           current_player=game.current_player,
                           face_down_top=game.face_down_pile[-1] if game.face_down_pile else None,
                           face_up_top_1=game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
                           face_up_top_2=game.face_up_pile_2[-1] if game.face_up_pile_2 else None)


if __name__ == '__main__':
    game = Game()

    deck = Deck()
    deck.generate_deck()

    game.deal_cards(deck)

    game.reveal_deck_cards(deck)

    app.run(host='0.0.0.0', port=12131, debug=True)
