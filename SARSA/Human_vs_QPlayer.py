import numpy as np
import tkinter as tk
import copy
import pickle    # cPickle is available in Python 2.x only, otherwise use pickle
from run_exp import Game, Player, HumanPlayer, ComputerPlayer, RandomPlayer, THandPlayer, QPlayer
from board import Board
tk.wantobjects = False

Q = pickle.load(open("Q_table_dictionary.p", "rb"))

root = tk.Tk()
player1 = HumanPlayer(mark="X")
player2 = QPlayer(mark="O", epsilon=0)

game = Game(root, player1, player2, Q=Q)

game.play()
root.mainloop()
