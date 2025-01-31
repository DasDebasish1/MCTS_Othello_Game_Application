import math
from random import choice
import time
from copy import deepcopy
import pickle
from .MCTS import Node as MCTSNODE

class Node(MCTSNODE):
        
   
    def select(self):
        if len(self.possibleMoves)!=len(self.children) or not self.possibleMoves:
            return self
        else:
            totalVisits = sum([child.visits for child in self.children])
            best_node = None
            best_score = float('-inf')
            for node in self.children:
                score = self.calculate_score(node, totalVisits)
                if score > best_score:
                    best_score = score
                    best_node = node
                if node.relative_pruning_condition():
                    return node.select()

            return best_node.select()
    
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


   
    def calculate_score(self, node, totalVisits):
        return node.score / (1 + node.visits) + self.C * math.sqrt(math.log(totalVisits) / (1 + node.visits))

    def relative_pruning_condition(self):
        if not self.parent:
            return True
        totalVisits = 0
        for child in self.parent.children:
            totalVisits += child.visits
        if totalVisits<len(self.parent.children)*2:
            return True
        for sibling in self.parent.children:
            if sibling != self:
                if sibling.visits > self.visits + sibling.upper_bound():
                    return True
        return False

    def upper_bound(self):
        amax=max(self.parent.children, key=lambda node: node.visits)
        maxwinrate= amax.score/(amax.visits+1)
        delta_i=maxwinrate-(self.score/(self.visits+1))
        return (8 * math.log(self.visits + 1) / (delta_i**2 + 1)) +1+ (math.pi ** 2) / 3



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

