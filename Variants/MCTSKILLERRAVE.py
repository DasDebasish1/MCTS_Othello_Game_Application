import math
from random import choice
import time
from copy import deepcopy
import pickle
from .MCTS import Node as MCTSNODE

class Node:
    def __init__(self, *args, **kwrgs):
        super().__init__(*args , **kwrgs)
        self.rave_visits = 0
        self.rave_score = 0

   

    def expand(self):
        possible_moves = self.state.validMoves()
        if self.state.validMoves() and possible_moves:
            for move in possible_moves:
                if move not in [child.move for child in self.children]:
                    expanded_state = deepcopy(self.state)
                    expanded_state.make_move(move)
                    self.children.append(Node(expanded_state, parent=self, move=move))

            return self.children[-1]
        else:
            return self

    def rollout(self, player):
        current_state = deepcopy(self.state)
        while current_state.validMoves():
            all_moves = current_state.validMoves()
            move = choice(all_moves)
            current_state.make_move(move)
        result = current_state.get_result()
        if abs(result) == 1:
            if player == 1:
                return result
            else:
                return -result
        else:
            return 0

    def backpropagate(self, result):
        self.visits += 1
        self.score += result
        if self.parent:
            self.parent.backpropagate(result)

    def calculate_score(self, node, total_visits):
        rave_weight = 0.01
        return (node.score / (1 + node.visits)) + self.C * math.sqrt(math.log(total_visits) / (1 + node.visits)) + (rave_weight * node.rave_score / (1 + node.rave_visits))



def MCTS(root_state,player=2,C=2.801,ttime=1,mode="Time",queue=None):
    root = Node(root_state,C=C)
    n=0
    if mode=="Time":
        start = time.time()
        while time.time()-start<ttime:
            node = root
            node = node.select()
            node = node.expand()
            result = node.rollout(player)
            node.backpropagate(result)
            n+=1
        
        
    else:
        n=ttime
        for i in range(ttime):
            node = root
            node = node.select()
            node = node.expand()
            result = node.rollout(player)
            node.backpropagate(result)
            n+=1
            if queue:
                with open('filename.pickle', 'wb') as handle:
                    pickle.dump(root, handle, protocol=pickle.HIGHEST_PROTOCOL)
                try:
                    PauseStatus=True
                    while PauseStatus:
                        f= open("setting.ini","r")
                        PauseStatus=f.read()=="1"
                        f.close()
                except:
                    pass
                time.sleep(0.5)
    if queue:
       queue.put((max(root.children, key=lambda node: node.visits).move,n))
    return  max(root.children, key=lambda node: node.visits).move,n,root

