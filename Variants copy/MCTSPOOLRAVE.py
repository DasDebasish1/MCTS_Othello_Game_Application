import math
from random import choice
import time
import pickle

from copy import deepcopy



class Node:
    def __init__(self, state, parent=None, move=None,expanded=False):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0
        self.expanded=expanded
        self.action_scores = {}

    
    def select(self):
        totalVisits = 0
        for child in self.children:
            totalVisits += child.visits

        exploration_bonus = math.sqrt(8 * math.log(totalVisits + 1) / (1 + self.visits))

        def ucb1(node):
            if node.visits == 0:
                return float('inf')
            return (node.score / node.visits) + exploration_bonus + self.rave_score(node.move)

        return max(self.children, key=ucb1)
    
    def rave_score(self, move):
        if move in self.action_scores:
            return self.action_scores[move] / (1 + self.visits)
        return 0
    
    def expand(self):
        possibleMoves = self.state.validMoves()
        if self.state.validMoves() and possibleMoves:
            for move in possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandedState = deepcopy(self.state)
                    expandedState.make_move(move)
                    self.children.append(Node(expandedState, parent=self, move=move))
                    
            return self.children[-1]
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
        for child in self.children:
            if child.move in self.action_scores:
                self.action_scores[child.move] += child.score
            else:
                self.action_scores[child.move] = child.score

        
        
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
       queue.put((max(root.children, key=lambda node: node.visits).move,0))
    return  max(root.children, key=lambda node: node.visits).move,n,root

