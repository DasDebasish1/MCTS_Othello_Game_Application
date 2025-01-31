import math
from random import choice
import time
from copy import deepcopy
import pickle
from .MCTS import Node as MCTSNODE


weights = [
            [120, -20, 20, 5, 5, 20, -20, 120],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [120, -20, 20, 5, 5, 20, -20, 120]
        ]

class Node(MCTSNODE):
    def __init__(self, *args, **kwrgs):
        super().__init__(*args , **kwrgs)
        self.amaf_visits = {}
        self.amaf_score = {}

    
   
    def calculate_score(self, node, total_visits):
        alpha = 0.9
        return (alpha * node.amaf_score.get(node.move, 0) / (1 + node.amaf_visits.get(node.move, 0)) +
                (1 - alpha) * node.score / (1 + node.visits) +
                self.C * math.sqrt(math.log(total_visits) / (1 + node.visits)))
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
            self.amaf_visits[move] = 0
            self.amaf_score[move] = 0
            return self.children[-1]
        else:
            return self
    
    def rollout(self,player):
        currentState = deepcopy(self.state)
        while currentState.validMoves():  
            all_move = currentState.validMoves()
            move=choice(all_move)
            currentState.make_move(move)
            self.amaf_visits[move] = self.amaf_visits.get(move, 0) + 1
            self.amaf_score[move] = self.amaf_score.get(move, 0) + self.evaluate(currentState,move,player)
        result = currentState.get_result()
        if abs(result)==1:
            if player==1:
                return result
            else:
                return -result
        else:
            return 0
    
    def evaluate(self,current_state, move,player):
        boardcopy = current_state.copy()
        boardcopy.make_move(move)
        score = 0
        for i in range(8):
            for j in range(8):
                if boardcopy.board[i][j] == player:
                    score += weights[i][j]
                elif boardcopy.board[i][j] == 1 if player==2 else 2: 
                    score -= weights[i][j]
        return score
        
    def backpropagate(self, result):
        self.visits += 1
        self.score += result
        if self.parent:
            self.parent.backpropagate(result)
        for move, visits in self.amaf_visits.items():
            self.amaf_score[move] += result * visits
   


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

