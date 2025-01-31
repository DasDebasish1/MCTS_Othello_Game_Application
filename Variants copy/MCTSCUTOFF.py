import math
from random import choice
import time
from copy import deepcopy
import pickle

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

class Node:
    def __init__(self, state, parent=None, move=None,expanded=False):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0
        self.expanded=expanded
        self.amaf_visits = {}
        self.amaf_score = {}
        self.cutoff=False
    
    def select(self):
        totalVisits = 0
        for child in self.children:
            totalVisits += child.visits

        total_visits = sum(child.visits for child in self.children)
        if self.cutoff:
            return max(self.children, key=lambda node: self.calculate_score(node,totalVisits))
        else:
            return max(self.children, key=lambda node: (node.score + node.amaf_score.get(node.move, 0)) 
                    / 
                    (1 + node.visits) + math.sqrt(8 * math.log(total_visits) / (1 + node.visits)))
       
    
    def expand(self):
        possibleMoves = self.state.validMoves()
        if self.state.validMoves() and possibleMoves:
            for move in possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandedState = deepcopy(self.state)
                    expandedState.make_move(move)
                    self.children.append(Node(expandedState, parent=self, move=move))
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
            if not self.cutoff:
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
        if not self.cutoff:
        
            for move, visits in self.amaf_visits.items():
                self.amaf_score[move] += result * visits
    def calculate_score(self,node,totalVisits):
        return node.score / (1 + node.visits) + 2.801* math.sqrt(math.log(totalVisits) / (1 + node.visits))



def MCTS(root_state,player=2,ttime=1,mode="Time",queue=None):

    root = Node(root_state,expanded=True)
    n=0
    if mode=="Time":
        start = time.time()
        while time.time()-start<ttime:
            node = root
            while len(node.children) > 0:
                if node == root and len(node.children) < len(root.state.validMoves()):
                    break
                node = node.select()
            node = node.expand()
            result = node.rollout(player)
            node.backpropagate(result)
            n+=1
        print(n)
        
    else:
        print(mode)
        for i in range(ttime):
            node = root
            while len(node.children) > 0:
                if node == root and len(node.children) < len(root.state.validMoves()):
                    break
                node = node.select()
            node = node.expand()
            result = node.rollout(player)
            node.backpropagate(result)
            with open('filename.pickle', 'wb') as handle:
                    pickle.dump(root, handle, protocol=pickle.HIGHEST_PROTOCOL)
            n+=1
    if queue:
       queue.put((max(root.children, key=lambda node: node.visits).move,n))
    return  max(root.children, key=lambda node: node.visits).move,n,root

