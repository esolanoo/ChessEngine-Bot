import numpy as np

initFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


# Cells  
class Cell:
    def __init__(self, row, column) -> None:
        self.column = column
        self.row = row
        self.id = chr(97+column) + str(row)
        self.empty=True
        self.val=0
    
    def __str__(self) -> str:
        return '.'
    def __repr__(self) -> str: 
        return '.'
    
    
# Pieces
val2str_pieces = {1: 'k', 2: 'q', 3: 'r', 4: 'b', 5: 'n', 6: 'p', 9: 'K', 10: 'Q', 11: 'R', 12: 'B', 13: 'N', 14: 'P'}
str2val_pieces = {v: k for k, v in val2str_pieces.items()}
class Piece(Cell):
    def __init__(self, row, column, c) -> None:
        super().__init__(row, column)
        self.id = chr(97+column) + str(row)
        self.c = c
        self.empty=False
        self.color = 0 if c.lower()==c else 1
        self.val = str2val_pieces[c]
        self.first_move = True
        
    def __str__(self) -> str:
        return self.c 
    def __repr__(self) -> str:
        return self.c 
    
    
# Game  
class Game:
    def __init__(self):
        self.fromFEN(initFEN)
        self.pos_moves = []
    
    def __str__(self):
        return str(self.board)
    def __repr__(self):
        return str(self.board)
    
    def show(self):
        print(self.toFEN())
        for i, row in enumerate(self.board):
            print(str(8-i)+ "    " + ' '.join(str(piece) for piece in row))
        print("\n     a b c d e f g h\n")
        
    def fromFEN(self, FEN):
        aux = 64
        FEN, self.turn, self.castling, self.passant, self.halfmove, m = FEN.split()
        self.step = int(m)
        
        board = list(np.zeros((8,8), dtype=object))
        for i in range(8):
            for j in range(8):
                board[7-i][j] = Cell(i+1, j)
                
        for x in [c for c in FEN if c!='/']:
            if ord(x)<65:
                aux -= int(x)
                pass
            else:
                row = 7-aux//8 + (1 if aux%8==0 else 0)
                col = 8-(aux%8) - (8 if aux%8==0 else 0)
                board[row][col] = Piece(8-row, col, x)
                board[row][col].empty=False
                aux -= 1
                
        self.board=board
    
    def toFEN(self):
        FEN = ''
        for i in range(8):
            aux = 0
            for j in range(8):
                if not (type(self.board[i][j]) is Piece):
                    aux += 1
                    if aux>1:
                        FEN = FEN[:-1]
                    FEN += str(aux)
                else:
                    aux=0
                    FEN += self.board[i][j].c
            if i<7:
                FEN += '/'
        FEN += ' w ' if self.turn == 1 else ' b '
        FEN += ' '.join([self.castling, self.passant, self.halfmove])
        FEN += ' ' + str(self.step)
        return FEN +'\n'  
        
    def valid_pos(self, col, row):
        return col<8 and col>=0 and row<8 and row>=0
    
    def enemy(self, col1, row1, col2, row2):
        return self.board[row1][col1].color != self.board[row2][col2].color
        
    def posible_moves_ind(self, pos):
        col = ord(pos[0])-97
        row = 8-int(pos[-1])
        pos_moves = list()
        if not self.board[row][col].empty: 
            aux = 1 if self.board[row][col].color == 0 else -1
            if self.board[row][col].c.lower()=='p':
                if self.board[row+1*aux][col].empty:
                    pos_moves.append((row+1*aux, col))
                for i in [-1,+1]:
                    if self.valid_pos(row+1*aux, col+i) and not(self.board[row+1*aux][col+i].empty) and self.enemy(row, col, row+1*aux, col+i):
                        pos_moves.append((row+1*aux, col+i, 'x'))
                if self.board[row+2*aux][col].empty and self.board[row][col].first_move:
                    pos_moves.append((row+2*aux, col, '+'))
        if pos_moves:                
            for i in pos_moves:
                self.pos_moves.append(self.board[row][col].c + pos + (i[2] if len(i)>2 else '') + chr(97+i[1]) + str(8-i[0]))
        return 0
    
    def possible_moves(self, color):
        self.pos_moves = []
        for mask, row in zip(self.mask(color), self.board):
            for m,i in zip(mask, row):
                if m:
                    self.posible_moves_ind(i.id)
        return None
    
    def mask(self, color):
        r = list()
        for row in self.board:
            r.append([not(i.empty) and (i.val>7 if color=='w' else i.val<7) for i in row])
        return np.array(r)