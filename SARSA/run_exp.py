import numpy as np
import tkinter as tk
import copy
import pdb
import pickle
from board import Board
import tkinter.messagebox as messagebox
# from players import Player, HumanPlayer, ComputerPlayer, RandomPlayer, THandPlayer, QPlayer

class Game:
    def __init__(self, master, player1, player2, Q_learn=None, Q={}, alpha=0.3, gamma=0.9):
        frame = tk.Frame(bg="#B4BDFF", bd=10)  # Light gray background color, border width=10, ridge relief
        frame.grid(padx=10, pady=10)  # Add padding around the frame

# You can add more styling options as needed

        self.master = master
        master.title("Tic Tac Toe")
        master.iconbitmap('favicon.ico')

        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.other_player = player2
        self.empty_text = ""
        self.board = Board()

        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(
                    frame,
                    text=self.empty_text,
                    width=4,
                    height=2,
                    font=("Helvetica", 30, "bold"),
                    command=lambda i=i, j=j: self.callback(self.buttons[i][j]),
                    bg="#83A2FF",  # Button color
                    fg="#676767"     # Text color
                )
                self.buttons[i][j].grid(row=i, column=j, padx=5, pady=5)  # Add some padding


        self.reset_button = tk.Button(text="Play Again??", command=self.reset, bg="#2E97A7", fg="white", font=("Helvetica", 12, "bold"), relief=tk.GROOVE)
        self.reset_button.grid(row=6, pady=(0, 10))


        self.Q_learn = Q_learn
        self.Q_learn_or_not()
        if self.Q_learn:
            self.Q = Q
            self.alpha = alpha          # Learning rate
            self.gamma = gamma          # Discount rate
            self.share_Q_with_players()

    def Q_learn_or_not(self):       # If either player is a QPlayer, turn on Q-learning
        if self.Q_learn is None:
            if isinstance(self.player1, QPlayer) or isinstance(self.player2, QPlayer):
                self.Q_learn = True

    def share_Q_with_players(self):             # The action value table Q is shared with the QPlayers to help them make their move decisions
        if isinstance(self.player1, QPlayer):
            self.player1.Q = self.Q
        if isinstance(self.player2, QPlayer):
            self.player2.Q = self.Q

    def callback(self, button):
        if self.board.over():
            pass                # Do nothing if the game is already over
        else:
            if isinstance(self.current_player, HumanPlayer) and isinstance(self.other_player, HumanPlayer):
                if self.empty(button):
                    move = self.get_move(button)
                    self.handle_move(move)
            elif isinstance(self.current_player, HumanPlayer) and isinstance(self.other_player, ComputerPlayer):
                computer_player = self.other_player
                if self.empty(button):
                    human_move = self.get_move(button)
                    self.handle_move(human_move)
                    if not self.board.over():               # Trigger the computer's next move
                        computer_move = computer_player.get_move(self.board)
                        self.handle_move(computer_move)

    def empty(self, button):
        return button["text"] == self.empty_text

    def get_move(self, button):
        info = button.grid_info()
        move = (int(info["row"]), int(info["column"]))                # Get move coordinates from the button's metadata
        return move

    def handle_move(self, move):
        if self.Q_learn:
            self.learn_Q(move)
        i, j = move         # Get row and column number of the corresponding button
        self.buttons[i][j].configure(text=self.current_player.mark)     # Change the label on the button to the current player's mark
        self.board.place_mark(move, self.current_player.mark)           # Update the board
        if self.board.over():
            self.declare_outcome_test()
        else:
            self.switch_players()


    def declare_outcome(self):
        if self.board.winner() is None:
            print ("Draw match")
        else:
            print("The game is over. The player with mark %s won!" % self.current_player.mark)

    def declare_outcome_test(self):
        if self.board.winner() is None:
            print ("Draw match")
            messagebox.showinfo("Game Over", "Draw match")
        else:
            print("The game is over. The player with mark %s won!" % self.current_player.mark)
            winner_mark = self.current_player.mark
            messagebox.showinfo("Game Over", f"The game is over. The player with mark {winner_mark} won!")

    def reset(self):
        print("Resetting...")
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].configure(text=self.empty_text)
        self.board = Board(grid=np.ones((3,3))*np.nan)
        self.current_player = self.player1
        self.other_player = self.player2
        # np.random.seed(seed=0)      # Set the random seed to zero to see the Q-learning 'in action' or for debugging purposes
        self.play()

    def switch_players(self):
        if self.current_player == self.player1:
            self.current_player = self.player2
            self.other_player = self.player1
        else:
            self.current_player = self.player1
            self.other_player = self.player2

    def play(self):
        if isinstance(self.player1, HumanPlayer) and isinstance(self.player2, HumanPlayer):
            pass        # For human vs. human, play relies on the callback from button presses
        elif isinstance(self.player1, HumanPlayer) and isinstance(self.player2, ComputerPlayer):
            pass
        elif isinstance(self.player1, ComputerPlayer) and isinstance(self.player2, HumanPlayer):
            first_computer_move = self.player1.get_move(self.board)      # If player 1 is a computer, it needs to be triggered to make the first move.
            self.handle_move(first_computer_move)
        elif isinstance(self.player1, ComputerPlayer) and isinstance(self.player2, ComputerPlayer):
            while not self.board.over():        # Make the two computer players play against each other without button presses
                self.play_turn()
                # move = self.current_player.get_move(self.board)
                # self.handle_move(move)

    def play_turn(self):
        move = self.current_player.get_move(self.board)
        self.handle_move(move)

    def learn_Q(self, move):                        
        state_key = QPlayer.make_and_maybe_add_key(self.board, self.current_player.mark, self.Q)   # Extract state key for the current board state
        next_board = self.board.get_next_board(move, self.current_player.mark)                     # Get the next board state after the current move
        next_state_key = QPlayer.make_and_maybe_add_key(next_board, self.other_player.mark, self.Q)   # Extract state key for the next board state

        if next_board.over():                 # Check if the next board state is terminal
            next_action = None
            expected = next_board.give_reward()
        else:                                 # Get the next action from the opponent player
            next_action = self.player2.get_move(next_board)
            next_Q = self.Q[next_state_key][next_action]   # Retrieve Q-value for the next state-action pair
            expected = next_board.give_reward() + self.gamma * next_Q   # Calculate the expected reward considering the future reward with discount

        current_action = move          # Current action is the move taken in the current state
        change = self.alpha * (expected - self.Q[state_key][current_action])     # Update the Q-value based on the SARSA algorithm
        self.Q[state_key][current_action] += change


class Player(object):
    def __init__(self, mark):
        self.mark = mark
        self.get_opponent_mark()

    def get_opponent_mark(self):
        if self.mark == 'X':
            self.opponent_mark = 'O'
        elif self.mark == 'O':
            self.opponent_mark = 'X'
        else:
            print("The player's mark must be either 'X' or 'O'.")

class HumanPlayer(Player):
    pass

class ComputerPlayer(Player):
    pass

class RandomPlayer(ComputerPlayer):
    @staticmethod
    def get_move(board):
        moves = board.available_moves()
        if moves:   # If "moves" is not an empty list (as it would be if cat's game were reached)
            return moves[np.random.choice(len(moves))]    # Apply random selection to the index, as otherwise it will be seen as a 2D array

class THandPlayer(ComputerPlayer):
    def __init__(self, mark):
        super(THandPlayer, self).__init__(mark=mark)

    def get_move(self, board):
        moves = board.available_moves()
        if moves:
            for move in moves:
                if THandPlayer.next_move_winner(board, move, self.mark):
                    return move
                elif THandPlayer.next_move_winner(board, move, self.opponent_mark):
                    return move
            else:
                return RandomPlayer.get_move(board)

    @staticmethod
    def next_move_winner(board, move, mark):
        return board.get_next_board(move, mark).winner() == mark


class QPlayer(ComputerPlayer):
    def __init__(self, mark, Q={}, epsilon=0.2):
        super(QPlayer, self).__init__(mark=mark)
        self.Q = Q
        self.epsilon = epsilon

    def get_move(self, board):
        if np.random.uniform() < self.epsilon:              # With probability epsilon, choose a move at random ("epsilon-greedy" exploration)
            return RandomPlayer.get_move(board)
        else:
            state_key = QPlayer.make_and_maybe_add_key(board, self.mark, self.Q)
            print(state_key)
            Qs = self.Q[state_key]
            print(Qs)

            if self.mark == "X":
                print(QPlayer.stochastic_argminmax(Qs, max))
                return QPlayer.stochastic_argminmax(Qs, max)
            elif self.mark == "O":
                print(QPlayer.stochastic_argminmax(Qs, min))
                return QPlayer.stochastic_argminmax(Qs, min)

    @staticmethod
    def make_and_maybe_add_key(board, mark, Q):     # Make a dictionary key for the current state (board + player turn) and if Q does not yet have it, add it to Q
        default_Qvalue = 1.0       # Encourages exploration
        state_key = board.make_key(mark)
        if Q.get(state_key) is None:
            moves = board.available_moves()
            Q[state_key] = {move: default_Qvalue for move in moves}    # The available moves in each state are initially given a default value of zero
        return state_key

    @staticmethod
    def stochastic_argminmax(Qs, min_or_max):       # Determines either the argmin or argmax of the array Qs such that if there are 'ties', one is chosen at random
        min_or_maxQ = min_or_max(Qs.values())
        count_of_min_or_max = list(Qs.values()).count(min_or_maxQ)
        if (count_of_min_or_max) > 1:      # If there is more than one move corresponding to the maximum Q-value, choose one at random
            best_options = [move for move in Qs.keys() if Qs[move] == min_or_maxQ]
            move = best_options[np.random.choice(len(best_options))]
        else:
            move = min_or_max(Qs, key=Qs.get)
        return move

