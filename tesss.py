from Variants import MCTS
from game import Game
import cProfile
def a():
    g=Game([])
    g.reset_board()
    MCTS.MCTS(g,1,100,"")


cProfile.run('a()')