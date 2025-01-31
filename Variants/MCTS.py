import math
from random import choice
import time
import pickle
from copy import deepcopy
import sys

sys.setrecursionlimit(1000000)

class Node:
    def __init__(self, state, parent=None, move=None , C = 2.801):
        self.state = state
        self.parent = parent
        self.move = move
        self.possibleMoves=self.state.validMoves()
        self.children = []
        self.visits = 0
        self.score = 0
        self.C = C
        
    def select(self):
        if len(self.possibleMoves)!=len(self.children) or not self.possibleMoves:
            return self
        else:
            totalVisits = sum([child.visits for child in self.children])
            return (max(self.children, key=lambda node: self.calculate_score(node, totalVisits))).select()

    def expand(self):
        if self.possibleMoves:
            expandableMoves=[]
            for move in self.possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandableMoves.append(move)
            if expandableMoves:
                expandedMove=choice(expandableMoves)
                expandedState = deepcopy(self.state)
                expandedState.make_move(expandedMove)
                self.children.append(Node(expandedState, parent=self, move=expandedMove))
                return self.children[-1]
            else:
                return self
        else:
            return self
    def rollout(self,player):
        currentState = deepcopy(self.state)
        while currentState.validMoves():  
            all_move = currentState.validMoves()
            move=choice(all_move)
            currentState.make_move(move)
        result = currentState.get_result()
        if abs(result)==1:
            if player==1:
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

    def calculate_score(self,node,totalVisits):
        return node.score / (1 + node.visits) + self.C * math.sqrt(math.log(totalVisits+1) / (1 + node.visits))




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

