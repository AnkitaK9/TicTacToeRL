import numpy as np
import tkinter as tk
import copy
import pickle    # cPickle is for Python 2.x only; in Python 3, simply "import pickle" and the accelerated version will be used automatically if available
from run_exp import Game, Player, HumanPlayer, ComputerPlayer, RandomPlayer, THandPlayer, QPlayer
from board import Board


tk.wantobjects = False
root = tk.Tk()
epsilon = 0.9
player1 = QPlayer(mark="X",epsilon = epsilon)
player2 = QPlayer(mark="O",epsilon = epsilon)
game = Game(root, player1, player2)

N_episodes = 20000
for episodes in range(N_episodes):
    game.play()
    game.reset()

Q = game.Q

filename = "Q_table_dictionary.p" 
pickle.dump(Q, open(filename, "wb"))
