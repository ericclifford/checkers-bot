import pygame
import time
from .constants import RED, WHITE, BLUE, SQUARE_SIZE, WIDTH, HEIGHT
from checkers.board import Board
from copy import deepcopy

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        self.automating = False

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
            
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            if not self.automating:
                self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
            if not self.automating and self.board.white_left > 0 and self.board.red_left > 0:
                self.automate()
        else:
            self.turn = RED

    def get_score(self):
        score = self.board.white_left - self.board.red_left + (self.board.white_kings * 1.5) - (self.board.red_kings * 1.5)
        return score

    def get_move_tree(self, newBoard, level, final = False):
        all_moves = []
        if level != 1:
            pieces = newBoard.get_pieces_by_color(WHITE)
        else:
            pieces = newBoard.get_pieces_by_color(RED)

        for piece in pieces:
            valid_moves = newBoard.get_valid_moves(piece)
            for move in valid_moves:
                row, col = move
                temp_board = deepcopy(newBoard)
                temp_game = Game(WIN)
                temp_game.board = temp_board
                temp_game.automating = True
                temp_game.valid_moves = valid_moves
                temp_game.selected = temp_game.board.get_piece(piece.row, piece.col)
                temp_game.select(row, col)
                if level != 1:
                    temp_game.turn = RED
                else:
                    temp_game.turn = WHITE
                if level == 0:
                    score = temp_game.get_score()
                    all_moves.append([piece, move, temp_game.get_move_tree(temp_game.board, 1)])
                if level == 1:
                    all_moves.append(temp_game.get_move_tree(temp_game.board, 2))
                if level == 2:
                    score = temp_game.get_score()
                    if final:
                        all_moves.append([piece, move, score])
                    else:
                        all_moves.append(score)

        return all_moves

    def minimax(self, final = False):
        if(final):
            score_tree = self.get_move_tree(self.board, 2, True)
        else:
            score_tree = self.get_move_tree(self.board, 0)
        best_move = []
        lows = []
        lowInd = []
        if not final:
            for mov in range(0,len(score_tree)):
                white_move = score_tree[mov]
                highs = []
                if len(white_move[2]) > 1:
                    for mov2 in range(0, len(white_move[2])):
                        red_move = white_move[2][mov2]
                        if len(red_move) > 0:
                            highs.append(max(red_move))
                elif len(white_move[2]) == 1:
                    if len(white_move[2][0]) > 0:
                        highs.append(max(white_move[2][0]))
                if len(highs) > 0:
                    lows.append(min(highs))
                    lowInd.append(white_move)
                
            if(len(lows) > 0):
                max_val = lows[0]
                max_ind = 0
                for i in range(0, len(lows)):
                    if lows[i] > max_val:
                        max_val = lows[i]
                        max_ind = i
                move = lowInd[max_ind]
                best_move.append(move[0])
                best_move.append(move[1])
            elif(len(score_tree) > 0):
                move = score_tree[0]
                best_move.append(move[0])
                best_move.append(move[1])
            else:
                best_move = []

        else:
            maxval = 0
            maxind = 0
            for i in range(0, len(score_tree)):
                if score_tree[i][2] > maxval:
                    maxval = score_tree[i][2]
                    maxind = i
            best_move.append(score_tree[maxind][0])
            best_move.append(score_tree[maxind][1])
        return best_move

    def automate(self):
        self.automating = True
        if(self.board.white_left == 1 or self.board.red_left == 1):
            best = self.minimax(True)
        else:
            best = self.minimax()
        if len(best) > 0:
            piece = best[0]
            row, col = best[1]
            self.select(piece.row, piece.col)
            self.select(row, col)
        self.automating = False
        self.change_turn()
        return self
