from flask import Flask, render_template, url_for, request, redirect
import random

app = Flask(__name__)

class PlayingCard:
    def __init__(self, number):
        self.number = int(number)

    def __repr__(self):
        return str(self.number)

    def to_dict(self):
        return {'number': self.number}

class CardDeck:
    def __init__(self):
        self.cards = []

    def generateDeck(self):
        # 4 cards of each number from -1 to 8 representing smoki
        for number in range(-1, 9):
            for _ in range(4):
                self.cards.append(PlayingCard(number))

        # 12 cards with the numbers 9, 10, 11 representing kruki
        for number in range(9, 12):
            for _ in range(4):
                self.cards.append(PlayingCard(number))

        random.shuffle(self.cards)

class Game:
    def __init__(self):
        self.num_players = 2
        self.players = [[] for _ in range(2)]
        self.current_player = 0
        self.turn_counter = 0
        self.face_up_pile_1 = []
        self.face_up_pile_2 = []
        self.face_down_pile = []

    def dealCards(self, deck):
        for _ in range(6):
            for player in self.players:
                player.append(deck.cards.pop(0))

    def revealDeckCards(self, deck):
        card_1 = deck.cards.pop(0)
        card_2 = deck.cards.pop(0)
        card_3 = deck.cards.pop(0)
        self.face_up_pile_1.append(card_1)
        self.face_up_pile_2.append(card_2)
        self.face_down_pile.append(card_3)

    def takeFaceUpCard(self, pile_index, exchange_index):
        if pile_index not in [1, 2]:
            return None

        face_up_piles = {1: self.face_up_pile_1, 2: self.face_up_pile_2}
        selected_pile = face_up_piles[pile_index]

        if not selected_pile or not (0 <= exchange_index < len(self.players[self.current_player])):
            return None

        new_card = selected_pile.pop()
        old_card = self.players[self.current_player].pop(exchange_index)
        self.players[self.current_player].insert(exchange_index, new_card)
        selected_pile.append(old_card)

        self.switchToNextPlayer()

        return old_card

    def takeFaceDownCard(self, exchange_index):
        if not self.face_down_pile or not self.players[self.current_player]:
            return None

        new_card = self.face_down_pile.pop()

        if 0 <= exchange_index < len(self.players[self.current_player]):
            old_card = self.players[self.current_player].pop(exchange_index)
            self.players[self.current_player].insert(exchange_index, new_card)

            self.face_up_pile_1.append(old_card)
            self.fillPiles()
            self.switchToNextPlayer()

            return old_card
        else:
            return None

    def leaveFaceDownCard(self):
        if not self.face_down_pile:
            return None

        card = self.face_down_pile.pop()
        self.face_up_pile_1.append(card)
        self.fillPiles()
        self.switchToNextPlayer()

        return card

    def fillPile(self, pile, desired_length, deck):
        while len(pile) < desired_length:
            if not deck.cards:
                self.shuffleDiscardPiles()
            pile.append(deck.cards.pop(0))

    def fillPiles(self):
        self.fillPile(self.face_up_pile_1, 2, deck)
        self.fillPile(self.face_up_pile_2, 2, deck)
        self.fillPile(self.face_down_pile, 2, deck)

    def shuffleDiscardPiles(self):
        random.shuffle(self.face_up_pile_1)
        random.shuffle(self.face_up_pile_2)
        random.shuffle(self.face_down_pile)
        deck.cards.extend(self.face_up_pile_1)
        deck.cards.extend(self.face_up_pile_2)
        deck.cards.extend(self.face_down_pile)
        random.shuffle(deck.cards)

    def switchToNextPlayer(self):
        self.current_player = (self.current_player + 1) % self.num_players
        self.turn_counter += 1

@app.route('/new_game', methods=['POST'])
def new_game():
    global game, deck
    game = Game()
    deck = CardDeck()
    deck.generateDeck()
    game.dealCards(deck)
    game.revealDeckCards(deck)
    return redirect(url_for('game'))

@app.route('/endgame', methods=['GET', 'POST'])
def endgame():
    player_sums = []
    if request.method == 'POST':
        for player_hand in game.players:
            for i, card in enumerate(player_hand):
                if card.number == 11:
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

    return render_template('endgame.html', players=game.players, sums=player_sums, winner=winner_index)

@app.route('/rules', methods=['GET', 'POST'])
def rules():
    return render_template('rules.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    revealed = False
    game_state = {
        'players': game.players,
        'current_player': game.current_player,
        'face_down_top': game.face_down_pile[-1] if game.face_down_pile else None,
        'face_up_top_1': game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
        'face_up_top_2': game.face_up_pile_2[-1] if game.face_up_pile_2 else None,
        'revealed': revealed,
        'turn_counter': game.turn_counter
    }

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'take_face_up':
            exchange_index = int(request.form.get('exchange_index', 0))
            pile_index = int(request.form.get('pile_index', 0))
            game.takeFaceUpCard(pile_index, exchange_index)
        elif action == 'take_face_down':
            exchange_index = int(request.form.get('exchange_index', 0))
            game.takeFaceDownCard(exchange_index)
            game_state['revealed'] = True
        elif action == 'leave_face_down':
            game.leaveFaceDownCard()
            game_state['revealed'] = False

        game_state.update({
            'face_down_top': game.face_down_pile[-1] if game.face_down_pile else None,
            'face_up_top_1': game.face_up_pile_1[-1] if game.face_up_pile_1 else None,
            'face_up_top_2': game.face_up_pile_2[-1] if game.face_up_pile_2 else None,
            'current_player': game.current_player,
            'turn_counter': game.turn_counter
        })

    return render_template('game.html', **game_state)

if __name__ == '__main__':
    game = Game()
    deck = CardDeck()
    deck.generateDeck()
    game.dealCards(deck)
    game.revealDeckCards(deck)
    app.run(host='0.0.0.0', port=12131, debug=True)
