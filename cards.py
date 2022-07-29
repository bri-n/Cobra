import copy
import random
from functools import total_ordering

# constants
NUM_SUITS = 4
CARDS_PER_SUIT = 13
CARDS_PER_DECK = 52
SUIT_SYMBOLS = ["C", "D", "H", "S"]
SOUTH = 0
WEST = 1
NORTH = 2
EAST = 3
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
SEATS = ["South", "West", "North", "East"]
VULNERABILITY = ["None", "N/S", "E/W", "Both",
                 "N/S", "E/W", "Both", "None",
                 "E/W", "Both", "None", "N/S",
                 "Both", "None", "N/S", "E/W"]
A = 12
K = 11
Q = 10
J = 9
T = 8


@total_ordering
class Card:
    def __init__(self, c_id):
        self.c_id = c_id
        self.suit = c_id // CARDS_PER_SUIT
        self.suit_symbol = SUIT_SYMBOLS[self.suit]
        self.rank = c_id % CARDS_PER_SUIT
        self.rank_symbol = RANKS[self.rank]

    def __str__(self):
        return self.card_symbol

    def __repr__(self):
        return f"{self.suit_symbol}{self.rank_symbol}"

    def card_symbol(self):
        return self.suit_symbol + self.rank_symbol

    def show_symbol(self):
        print(f"{self.card_symbol}")

    def __lt__(self, other_card):
        return self.c_id < other_card.c_id


class Deck:
    def __init__(self):
        self.cards = []
        for c in range(CARDS_PER_DECK):
            self.cards.append(Card(c))

    def __str__(self):
        return self.cards

    def __repr__(self):
        return f"{self.cards}"
        # return "cards"  # f"{self.suit_symbol}{self.rank_symbol}"

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, players: []):
        i = 0
        for player in players:
            player.hand = Hand(self.cards[i:i + 13])
            i += 13


class Hand:
    def __init__(self, crds: 'List of Card instances'):
        self.cards = crds
        self.cards.sort(reverse=True)
        self._calc_dist()
        self._extract_suits()
        self.bpc = self._calc_bpc()

    def _calc_dist(self):
        self.distribution = [0, 0, 0, 0]
        for card in self.cards:
            suit_ndx = 3 - SUIT_SYMBOLS.index(card.suit_symbol)
            self.distribution[suit_ndx] += 1

    def _extract_suits(self):
        self.suits = []  # a list of 4 suit instances
        end = 0
        for i in range(NUM_SUITS):
            start = end
            end = start + self.distribution[i]
            cards_in_suit = self.cards[start:end]
            suit = Suit(cards_in_suit, SUIT_SYMBOLS[3 - i])
            self.suits.append(suit)

    def _calc_bpc(self):
        bpc = 0
        for suit in self.suits:
            bpc += suit.hcp
            bpc += suit.biddable
            bpc -= suit.unprotected_hnrs
        return bpc

    def display_hand_eval(self):
        print(f"BPC {self.bpc}")


class Suit:
    def __init__(self, crds: [], suit_sym: str):
        self.cards = crds
        self.suit_symbol = suit_sym
        self.num_cards = len(crds)
        self.rank_symbols = self._gather_rank_symbols(self.cards)
        self.ranks = self._gather_ranks(self.cards)
        self._eval_suit()

    def solidarity(self, ranks: []):
        solid = False
        if ranks[0] == A:
            if self.num_cards >= 11:
                solid = True
            if self.num_cards == 10 and ranks[1] >= Q:
                solid = True
            if ranks[1] == K:
                if self.num_cards == 9:
                    solid = True
                if self.num_cards == 8 and ranks[2] >= J:
                    solid = True
                if ranks[1] == Q:
                    if self.num_cards == 7:
                        solid = True
                    if self.num_cards == 6 and ranks[3] >= T:
                        solid = True
                if ranks[3] == J:
                    solid = True
        return solid

    def semi_solidarity(self, ranks: []):
        ranks_copy = copy.copy(ranks)
        if ranks[0] != A:
            ranks_copy[-1] = A
            ranks_copy.sort(reverse=True)
            return self.solidarity(ranks_copy)
        if ranks[1] != K:
            ranks_copy[-1] = K
            ranks_copy.sort(reverse=True)
            return self.solidarity(ranks_copy)
        if ranks[2] != Q:
            ranks_copy[-1] = Q
            ranks_copy.sort(reverse=True)
            return self.solidarity(ranks_copy)
        if ranks[1] != K:
            ranks_copy[-1] = J
            ranks_copy.sort(reverse=True)
            return self.solidarity(ranks_copy)

    def _eval_suit(self):
        self.hcp = 0
        self.hnrs = 0
        self.top_hnrs = 0
        # Loop through cards once
        for card in self.cards:
            self.hcp += max(card.rank - 8, 0)
            self.hnrs += (card.rank > 8)
            self.top_hnrs += (card.rank > 9)
        self.solid = False
        self.semi_solid = False
        if self.num_cards >= 4:
            self.solid = self.solidarity(self.ranks)
            if not self.solid:
                self.semi_solid = self.semi_solidarity(self.ranks)
        self.hnr_tricks = self._calc_hnr_tricks()
        self.biddable = self._calc_biddability()
        self.unprotected_hnrs = self.unprot_hnrs()

    @staticmethod
    def _gather_rank_symbols(crds):
        rank_symbols = ""
        for card in crds:
            rank_symbols += card.rank_symbol
        return rank_symbols

    @staticmethod
    def _gather_ranks(crds):
        ranks = []
        for card in crds:
            ranks.append(card.rank)
        return ranks

    def display_suit_eval(self):
        print(f"Suit = {self.suit_symbol}")
        print(f"hcp {self.hcp}")
        print(f"hnrs {self.hnrs}")
        print(f"top hnrs {self.top_hnrs}")
        print(f"solid {self.solid}")
        print(f"semi-solid {self.semi_solid}")
        print(f"Hnr tricks {self.hnr_tricks}")
        print(f"biddable {self.biddable}")

    def _calc_hnr_tricks(self):
        hnr_tricks = 0
        if self.num_cards == 0:
            return hnr_tricks
        if self.ranks[0] == A:
            hnr_tricks = 1
            if self.num_cards >= 2:
                if self.ranks[1] == K:
                    hnr_tricks = 2
                if self.num_cards >= 3 and self.ranks[1] == Q and self.ranks[2] == J:
                    hnr_tricks = 2
                if self.num_cards >= 3 and self.ranks[1] == J and self.ranks[1] == T:
                    hnr_tricks = 1.5
        if self.ranks[0] == K:
            if self.num_cards >= 1:
                hnr_tricks = 1
                if self.num_cards >= 2 and self.ranks[1] == Q:
                    hnr_tricks = 1
                if self.num_cards >= 3 and self.ranks[1] == Q and self.ranks[2] == J:
                    hnr_tricks = 1.5
                if self.num_cards >= 3 and self.ranks[1] == J and self.ranks[1] == T:
                    hnr_tricks = 1
        return hnr_tricks

    def _calc_biddability(self):
        biddable = 0
        if self.num_cards >= 4:
            base_len = 4
            if self.hnrs >= 3 or self.hcp >= 4:
                biddable = 1
            elif self.num_cards >= 5:
                biddable = 1
                base_len = 5
            extra_len = self.num_cards - base_len
            if extra_len == 1:
                biddable = 2
            if extra_len == 2:
                biddable = 3
            if extra_len >= 3:
                biddable = 3 * (extra_len - 1)
        return biddable

    def unprot_hnrs(self):
        unprot = 0
        if self.num_cards == 1 and self.hcp > 0:
            unprot = 1
        if self.num_cards == 2 and self.ranks[1] == J:
            unprot = 1
        return unprot


class Board:
    def __init__(self, b_number=1, dealer=None):
        self.b_number = b_number
        self.vulnerability = VULNERABILITY[self.b_number % 16]
        if dealer is None:
            self.dealer = b_number % 4
        else:
            dealer = dealer % 4
        self.dealer = dealer

    @staticmethod
    def display_n_s(hand: []):
        for suit in range(NUM_SUITS):
            card_ranks = hand.suits[suit].rank_symbols
            if card_ranks == "":
                card_ranks = "-"
            suit_symbol = hand.suits[suit].suit_symbol
            print(" " * 10 + f"{suit_symbol}", card_ranks)
        print()

    @staticmethod
    def display_w_e(w_hand: [], e_hand: []):
        for suit in range(NUM_SUITS):
            suit_symbol = w_hand.suits[suit].suit_symbol
            w_card_ranks = w_hand.suits[suit].rank_symbols
            if w_card_ranks == "":
                w_card_ranks = "-"
            e_card_ranks = e_hand.suits[suit].rank_symbols
            if e_card_ranks == "":
                e_card_ranks = "-"
            print(f"{suit_symbol} {w_card_ranks}" + " " * (18 - len(w_card_ranks)) + f"{suit_symbol} {e_card_ranks}")

    def display_all(self, players: []):
        print(" " * 10 + "North")
        player = players[NORTH]
        self.display_n_s(player.hand)

        print("West" + " " * 16 + "East")
        w_player = players[WEST]
        e_player = players[EAST]
        self.display_w_e(w_player.hand, e_player.hand)

        print(" " * 10 + "South")
        player = players[SOUTH]
        self.display_n_s(player.hand)
        print("==========================")
