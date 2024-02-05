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

        random.shuffle(self.cards)

class Game:
    def __init__(self):
        self.num_players = 2
        self.players = [[] for _ in range(2)]
        self.face_down_pile = []
        self.face_up_pile_1 = []
        self.face_up_pile_2 = []
        self.current_player = 0
        self.turn_counter = 0

    def switch_to_next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players
        self.turn_counter += 1

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
            return None

        if 0 <= exchange_index < len(self.players[self.current_player]):
            old_card = self.players[self.current_player].pop(exchange_index)
            self.players[self.current_player].insert(exchange_index, new_card)

            if pile_index == 1:
                self.face_up_pile_1.append(old_card)
            else:
                self.face_up_pile_2.append(old_card)

            self.switch_to_next_player()

            return old_card
        else:
            return None

    def fill_piles(self):
        while len(self.face_up_pile_1) < 2:
            if not deck.cards:
                self.shuffle_discard_piles()
            self.face_up_pile_1.append(deck.cards.pop(0))

        while len(self.face_up_pile_2) < 2:
            if not deck.cards:
                self.shuffle_discard_piles()
            self.face_up_pile_2.append(deck.cards.pop(0))

        while len(self.face_down_pile) < 2:
            if not deck.cards:
                self.shuffle_discard_piles()
            self.face_down_pile.append(deck.cards.pop(0))

    def shuffle_discard_piles(self):
        random.shuffle(self.face_up_pile_1)
        random.shuffle(self.face_up_pile_2)
        random.shuffle(self.face_down_pile)
        deck.cards.extend(self.face_up_pile_1)
        deck.cards.extend(self.face_up_pile_2)
        deck.cards.extend(self.face_down_pile)
        random.shuffle(deck.cards)

    def take_face_down_card(self, exchange_index):
        if not self.face_down_pile or not self.players[self.current_player]:
            return None

        new_card = self.face_down_pile.pop()

        if 0 <= exchange_index < len(self.players[self.current_player]):
            old_card = self.players[self.current_player].pop(exchange_index)
            self.players[self.current_player].insert(exchange_index, new_card)

            self.face_up_pile_1.append(old_card)
            self.fill_piles()
            self.switch_to_next_player()
            return old_card
        else:
            return None

    def leave_face_down_card(self):
        if not self.face_down_pile:
            return None

        card = self.face_down_pile.pop()
        self.face_up_pile_1.append(card)
        self.fill_piles()
        self.switch_to_next_player()

        return card

@app.route('/new_game', methods=['POST'])
def new_game():
    global game, deck
    game = Game()
    deck = Deck()
    deck.generate_deck()
    game.deal_cards(deck)
    game.reveal_deck_cards(deck)
    return redirect(url_for('game'))

@app.route('/end_screen', methods=['GET', 'POST'])
def end_screen():
    player_sums = []
    if request.method == 'POST':
        for player_hand in game.players:
            for i, card in enumerate(player_hand):
                if card.number == 11:
                    # Handle edge cases for the card with number 11
                    if i == 0:
                        card.number = min(player_hand[i + 1].number, card.number)
                    elif i == len(player_hand) - 1:
                        card.number = min(player_hand[i - 1].number, card.number)
                    elif i % 3 == 0:
                        card.number = min(player_hand[i + 1].number, card.number)
                    elif i % 3 == 2:
                        card.number = min(player_hand[i - 1].number, card.number)
                    else:
                        card.number = min(player_hand[i - 1].number, player_hand[i + 1].number, card.number)

            for i in range(0, len(player_hand) - 3, 3):
                if player_hand[i].number == player_hand[i + 3].number:
                    player_hand[i].number = 0
                    player_hand[i + 3].number = 0

                if player_hand[i + 1].number == player_hand[i + 4].number:
                    player_hand[i + 1].number = 0
                    player_hand[i + 4].number = 0

                if player_hand[i + 2].number == player_hand[i + 5].number:
                    player_hand[i + 2].number = 0
                    player_hand[i + 5].number = 0

            player_sum = sum(card.number for card in player_hand)
            player_sums.append(player_sum)

    winner_index = min(range(len(player_sums)), key=player_sums.__getitem__)

    return render_template('end_screen.html', players=game.players, sums=player_sums, winner=winner_index)

@app.route('/rules', methods=['GET', 'POST'])
def rules():
    return render_template('rules.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    revealed = False
    if request.method == 'POST':
        action = request.form['action']
        pile_index = int(request.form['pile_index'])

        if action == 'take_face_up':
            exchange_index = int(request.form['exchange_index'])
            card = game.take_face_up_card(pile_index, exchange_index)
        elif action == 'take_face_down':
            exchange_index = int(request.form['exchange_index'])
            card = game.take_face_down_card(exchange_index)
            revealed = True
        elif action == 'leave_face_down':
            card = game.leave_face_down_card()
            revealed = False

        return render_template('game.html',
                               players=game.players,
                               current_player=game.current_player,
                               face_down_top=game.face_down_pile[-1] if game.face_down_pile else None,
                               face_up_top_1=game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
                               face_up_top_2=game.face_up_pile_2[-1] if game.face_up_pile_2 else None,
                               revealed=revealed,
                               turn_counter=game.turn_counter)

    return render_template('game.html',
                           players=game.players,
                           current_player=game.current_player,
                           face_down_top=game.face_down_pile[-1] if game.face_down_pile else None,
                           face_up_top_1=game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
                           face_up_top_2=game.face_up_pile_2[-1] if game.face_up_pile_2 else None,
                           revealed=revealed,
                           turn_counter=game.turn_counter)



if __name__ == '__main__':
    game = Game()

    deck = Deck()
    deck.generate_deck()

    game.deal_cards(deck)

    game.reveal_deck_cards(deck)

    app.run(host='0.0.0.0', port=12131, debug=True)
