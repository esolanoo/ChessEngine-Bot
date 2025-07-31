from classes import Game
import time, random, os


g = Game()
g.show()

for i in range(150):
    os.system('cls')
    g.possible_moves(g.turn)
    g.move(random.randint(0, len(g.pos_moves)-1))
    g.show()
    time.sleep(.1)
    
print(g.history())