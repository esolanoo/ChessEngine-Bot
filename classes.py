import numpy as np

initFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


# Cells  
val2str_pieces = {1: 'k', 2: 'q', 3: 'r', 4: 'b', 5: 'n', 6: 'p', 9: 'K', 10: 'Q', 11: 'R', 12: 'B', 13: 'N', 14: 'P'}
str2val_pieces = {v: k for k, v in val2str_pieces.items()}
class Cell:
    def __init__(self, row, column) -> None:
        self.column = column
        self.row = 8-row
        self.id = chr(97+column) + str(row)
        self.empty=True
        self.first_move=True
        self.val=0
        self.color = ''
        self.c = ''
    
    def __str__(self) -> str:
        return '.' if self.empty else self.c
    def __repr__(self) -> str: 
        return '.' if self.empty else self.c
    
    def make_empty(self):
        setattr(self, 'empty', True)
        setattr(self, 'val', 0)
        setattr(self, 'color', '')
    
    def set_piece(self, c):
        setattr(self, 'c', c)
        setattr(self, 'empty', False)
        setattr(self, 'color', 'b' if c.lower()==c else 'w')
        setattr(self, 'val', str2val_pieces[c])
    
    def import_piece(self, new_piece):
        setattr(self, 'c', new_piece.c)
        setattr(self, 'empty', False)
        setattr(self, 'color', new_piece.color)
        setattr(self, 'val', str2val_pieces[new_piece.c])
        setattr(self, 'first_move', False)
        
    
# Game  
class Game:
    def __init__(self):
        self.fromFEN(initFEN)
        self.pos_moves = []
        self.hist = []
        self.game = self.toFEN()
    
    def __str__(self):
        return self.game
    def __repr__(self):
        return self.game
    
    def show(self):
        print(self.toFEN())
        for i, row in enumerate(self.board):
            print(str(8-i)+ "    " + ' '.join(str(piece) for piece in row))
        print("\n     a b c d e f g h\n")
        
    def history(self):
        print(' '.join(self.hist))
            
    def id2cord(self, id):
        return (8-int(id[-1]), ord(id[0])-97)
    
    def cord2id(self, row, col):
        return chr(97+col) + str(8-row)
    
    def find_piece(self, pos):
        row, col = self.id2cord(pos)
        return self.board[row][col]
    
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
                board[row][col].set_piece(x)
                aux -= 1
                
        self.board=board
    
    def toFEN(self):
        FEN = ''
        for i in range(8):
            aux = 0
            for j in range(8):
                if self.board[i][j].empty:
                    aux += 1
                    if aux>1:
                        FEN = FEN[:-1]
                    FEN += str(aux)
                else:
                    aux=0
                    FEN += self.board[i][j].c
            if i<7:
                FEN += '/'
        FEN += ' '
        FEN += ' '.join([self.turn, self.castling, self.passant, self.halfmove, str(self.step)])
        return FEN +'\n'  
        
    def valid_pos(self, row, col):
        return col<8 and col>=0 and row<8 and row>=0
    
    def enemy(self, row1, col1, row2, col2):
        return (self.board[row1][col1].color != self.board[row2][col2].color)
        
    def posible_moves_ind(self, pos):
        row, col = self.id2cord(pos)
        traveler = self.board[row][col]
        pos_moves = list()
        if not traveler.empty: 
            aux = 1 if traveler.color == 'b' else -1
            if traveler.c.lower()=='p':
                if self.board[row+1*aux][col].empty:
                    pos_moves.append((row+1*aux, col))
                for i in [-1,+1]:
                    if self.valid_pos(row+1*aux, col+i) and not(self.board[row+1*aux][col+i].empty) and self.enemy(row, col, row+1*aux, col+i):
                        pos_moves.append((row+1*aux, col+i, 'x'))
                if self.board[row+2*aux][col].empty and self.board[row][col].first_move:
                    pos_moves.append((row+2*aux, col))
                    
            if traveler.c.lower()=='n':
                for i in [-2,-1,1,2]:
                    for j in [-2,-1,1,2]:
                        if abs(i)!=abs(j):
                            if self.valid_pos(row+i, col+j):
                                if self.board[row+i][col+j].empty:
                                    pos_moves.append((row+i, col+j))
                                elif self.enemy(row, col, row+i, col+j):
                                    pos_moves.append((row+i, col+j, 'x'))
                                else:
                                    pass
                          
            if traveler.c.lower()=='b':
                for i in [-1,1]:
                    for j in [-1,1]:
                        r, c = row+i, col+j
                        while self.valid_pos(r,c):
                            if self.board[r][c].empty:
                                pos_moves.append((r,c))
                            elif self.enemy(row, col, r, c):
                                pos_moves.append((r,c,'x'))
                                break
                            else:
                                break
                            r+=i
                            c+=j
                            
        if pos_moves:                
            for i in set(pos_moves):
                self.pos_moves.append(self.board[row][col].c + pos + (i[2] if len(i)>2 else '') + self.cord2id(i[0], i[1]))
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
    
    def move(self, move_id):
        move = self.pos_moves[move_id]
        self.pos_moves = []
        self.hist.append(move)
        capture = False
        if 'x'in move:
            capture = True
            move.replace('x', '')
        
        origin = move[1:3]
        traveler = self.find_piece(origin)
        
        destiny = move[-2:]
        destination = self.find_piece(destiny)
        destination.import_piece(traveler)
        traveler.make_empty()
        
        setattr(self, 'step', self.step + 1 if self.turn=='b' else self.step)
        setattr(self, 'turn', 'w' if self.turn=='b' else 'b')
        self.game = self.toFEN()
        