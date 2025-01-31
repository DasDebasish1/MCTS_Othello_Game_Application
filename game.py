from copy import deepcopy
class Game:
    def __init__(self, board):
        self.board = board
        self.direction = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        self.reset_board()
    def reset_board(self):
        self.board =  [[0] * 8 for _ in range(8)]
        self.board[3][3] = 1
        self.board[3][4] = 2
        self.board[4][3] = 2
        self.board[4][4] = 1
        self.currentPlayer = 1
        
    def is_decisive_move(self, player, move):
        test_game = deepcopy(self)
        test_game.make_move(move)
        result = test_game.get_result()
        if self.validMoves():
            return False
        if player == 1:
            return result == 1
        else:
            return result == -1
    
    def InsideBoard(self, row, col):
        
        return 0 <= row and row < 8 and 0 <= col and col < 8


    def valid_move(self, start):

        if start != () and self.InsideBoard(start[0], start[1]) and self.board[start[0]][start[1]] == 0:
            for direction in self.direction:
                if self.has_tile_to_flip(start, direction):
                    return True
                     
        return False

    

    def has_tile_to_flip(self, start, direction):
        i = 1
        if self.InsideBoard(start[0], start[1]):
            while True:
                row = start[0] + direction[0] * i
                col = start[1] + direction[1] * i
                if not self.InsideBoard(row, col) or \
                    self.board[row][col] == 0:
                    return False
                elif self.board[row][col] == self.currentPlayer:
                    break
                else:
                    i += 1
        return i > 1
    
    def validMoves(self):
        return [(row, col) for row in range(8) for col in range(8) if self.valid_move((row, col))]

    def flip_tile(self, start):
        for direction in self.direction:
            if self.has_tile_to_flip(start, direction):
                i = 1
                while True:
                    row = start[0] + direction[0] * i
                    col = start[1] + direction[1] * i
                    if self.board[row][col] == self.currentPlayer:
                        break
                    else:
                        self.board[row][col] = self.currentPlayer
                        i += 1

    

    def make_move(self, start):
        if self.valid_move(start):
            self.board[start[0]][start[1]] = self.currentPlayer
            self.flip_tile(start)
            self.currentPlayer = 2 if self.currentPlayer == 1 else 1
        

    def copy(self):
        new_game = Game([row.copy() for row in self.board])
        new_game.currentPlayer = self.currentPlayer
        return new_game

    
    def get_result(self):
        player_one_tiles = sum(row.count(1) for row in self.board)
        player_two_tiles = sum(row.count(2) for row in self.board)
        
        if player_one_tiles > player_two_tiles:
            return 1
        elif player_two_tiles > player_one_tiles:
            return -1
        else:
            return 0


