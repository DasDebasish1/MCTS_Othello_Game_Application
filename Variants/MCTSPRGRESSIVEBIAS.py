import math
from random import choice
import time
from copy import deepcopy
import pickle
from .MCTS import Node as MCTSNODE

class Node(MCTSNODE):
    
    def calculate_score(self, node, totalVisits):
        return super().calculate_score(node, totalVisits)+ self.heuristic_function(node)
    def heuristic_function(self, node):
        Hi = 0.8
        return Hi / (node.visits + 1)


    def expand(self):
        if self.possibleMoves:
            expandableMoves=[]
            for move in self.possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandableMoves.append(move)
            expandedMove=choice(expandableMoves)
            expandedState = deepcopy(self.state)
            expandedState.make_move(expandedMove)
            self.children.append(Node(expandedState, parent=self, move=expandedMove))
            
            return self.children[-1]
        else:
            return self
   


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

