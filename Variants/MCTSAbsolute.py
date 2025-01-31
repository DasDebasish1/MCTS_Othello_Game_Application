import time
import pickle
from .MCTS import Node as MCTSNODE
from random import choice
from copy import deepcopy
class Node(MCTSNODE):
        
   
    def select(self, absolute_pruning_threshold=0.6):
        if len(self.possibleMoves)!=len(self.children) or not self.possibleMoves:
            return self
        else:
            totalVisits = sum([child.visits for child in self.children])
            total_score = sum(self.calculate_score(child, totalVisits) for child in self.children)
            best_node = None
            best_score = float('-inf')
            for node in self.children:
                score = self.calculate_score(node, totalVisits)
                if score > best_score:
                    best_score = score
                    best_node = node
                if total_score!=0:
                    if score / total_score > absolute_pruning_threshold and totalVisits>=len(self.children)*absolute_pruning_threshold:
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

