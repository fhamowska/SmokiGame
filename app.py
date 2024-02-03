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

    def take_face_up_card(self, pile_index, exchange_index):
        if pile_index == 1 and self.face_up_pile_1:
            new_card = self.face_up_pile_1.pop()
        elif pile_index == 2 and self.face_up_pile_2:
            new_card = self.face_up_pile_2.pop()
        else:
            return None  # Invalid pile_index

        # Player chooses which card to exchange
        if 0 <= exchange_index < len(self.players[self.current_player]):
            old_card = self.players[self.current_player].pop(exchange_index)
            self.players[self.current_player].insert(exchange_index, new_card)

            # Place the old card on top of the face-up pile
            if pile_index == 1:
                self.face_up_pile_1.insert(0, old_card)
            else:
                self.face_up_pile_2.insert(0, old_card)

            self.switch_to_next_player()

            return old_card
        else:
            # Invalid exchange_index
            return None

    def fill_piles(self):

        while len(self.face_up_pile_1) < 2:
            self.face_up_pile_1.append(deck.cards.pop(0))

        while len(self.face_up_pile_2) < 2:
            self.face_up_pile_2.append(deck.cards.pop(0))

        while len(self.face_down_pile) < 2:
            self.face_down_pile.append(deck.cards.pop(0))

    def take_face_down_card(self, exchange_index):
        if not self.face_down_pile or not self.players[self.current_player]:
            return None  # No cards in the face-down pile or player's hand

        new_card = self.face_down_pile.pop()

        if 0 <= exchange_index < len(self.players[self.current_player]):
            old_card = self.players[self.current_player].pop(exchange_index)
            self.players[self.current_player].insert(exchange_index, new_card)

            self.face_up_pile_1.append(old_card)
            self.fill_piles()
            self.switch_to_next_player()
            return old_card
        else:
            # Invalid exchange_index
            return None

    def leave_face_down_card(self, leave_pile_index):
        if not self.face_down_pile:
            return None  # No cards in the face-down pile

        card = self.face_down_pile.pop()

        # Perform actions based on the game rules
        if leave_pile_index == 1:
            self.face_up_pile_1.append(card)
        elif leave_pile_index == 2:
            self.face_up_pile_2.append(card)
        else:
            return None  # Invalid leave_pile_index

        self.fill_piles()
        self.switch_to_next_player()

        return card


@app.route('/game', methods=['GET', 'POST'])
def game():
    revealed = False  # Initialize revealed status
    if request.method == 'POST':
        action = request.form['action']
        pile_index = int(request.form['pile_index'])

        if action == 'take_face_up':
            exchange_index = int(request.form['exchange_index'])
            card = game.take_face_up_card(pile_index, exchange_index)
        elif action == 'take_face_down':
            exchange_index = int(request.form['exchange_index'])
            card = game.take_face_down_card(exchange_index)
            revealed = True  # Set revealed status to True
        elif action == 'leave_face_down':
            leave_pile_index = int(request.form['leave_pile_index'])
            card = game.leave_face_down_card(leave_pile_index)
            revealed = False  # Reset revealed status

        return render_template('game.html',
                               players=game.players,
                               current_player=game.current_player,
                               face_down_top=game.face_down_pile[-1] if game.face_down_pile else None,
                               face_up_top_1=game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
                               face_up_top_2=game.face_up_pile_2[-1] if game.face_up_pile_2 else None,
                               revealed=revealed)  # Pass revealed status to the template

    return render_template('game.html',
                           players=game.players,
                           current_player=game.current_player,
                           face_down_top=game.face_down_pile[-1] if game.face_down_pile else None,
                           face_up_top_1=game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
                           face_up_top_2=game.face_up_pile_2[-1] if game.face_up_pile_2 else None,
                           revealed=revealed)  # Pass revealed status to the template



if __name__ == '__main__':
    game = Game()

    deck = Deck()
    deck.generate_deck()

    game.deal_cards(deck)

    game.reveal_deck_cards(deck)

    app.run(host='0.0.0.0', port=12131, debug=True)
