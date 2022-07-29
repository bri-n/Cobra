from tkinter import *
import cards
SOUTH = 0
WEST = 1
NORTH = 2
EAST = 3
SEATS = ["South", "West", "North", "East"]
PLAYER_NAMES = ["P1", "P2", "P3", "P4"]

# from PIL import Image, ImageTk

# root = Tk()
# root.title('Card Deck')
# root.iconbitmap('images/ace_clubs_icon.png')
# root.geometry("1400x900")
# root.configure(background="green")

# my_frame = Frame(root, bg="green")
# my_frame.pack(pady=20)


class Player:
    def __init__(self, name: str, p_seat: str):
        self.name = name
        self.seat = p_seat
        self.hand = []
        self.distribution = []

    def __repr__(self):
        return f"{self.name} - {self.seat}"


if __name__ == '__main__':
    # Create four players
    players = []
    for player, seat in zip(PLAYER_NAMES, SEATS):
        players.append(Player(player, seat))
    deck = cards.Deck()

    # Main loop creating boards
    board_num = 0
    look_further = True
    # while board_num < 16:
    while look_further:
        board_num += 1
        deck.shuffle()
        deck.deal(players)
        board = cards.Board(board_num)
        board.display_all(players)

        # player = players[SOUTH]
        # for suit in player.hand.suits:
        #     if suit.biddable > 2:
        #         suit.display_suit_eval()
        #         print(board_num)
        #         look_further = False
        # player.hand.display_hand_eval()
    # root.mainloop()
