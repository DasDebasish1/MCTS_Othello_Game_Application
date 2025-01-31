import math
from random import choice
import time
from copy import deepcopy
import pickle

class Node:
    def __init__(self, state, parent=None, move=None, expanded=False):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0
        self.expanded = expanded

    def select(self):
        totalVisits = 0
        for child in self.children:
            totalVisits += child.visits

        best_node = None
        best_score = float('-inf')
        for node in self.children:
            score = self.calculate_score(node, totalVisits)

            if score > best_score:
                best_score = score
                best_node = node
            if node.relative_pruning_condition():
                return node
        return best_node

    def expand(self):
        possibleMoves = self.state.validMoves()
        if possibleMoves:
            for move in possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandedState = deepcopy(self.state)
                    expandedState.make_move(move)
                    self.children.append(Node(expandedState, parent=self, move=move))

            return self.children[-1]
        else:
            return self

    def rollout(self, player):
        currentState = deepcopy(self.state)
        while currentState.validMoves():
            all_move = currentState.validMoves()
            move = choice(all_move)
            currentState.make_move(move)
        result = currentState.get_result()
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

    def calculate_score(self, node, totalVisits):
        return node.score / (1 + node.visits) + 2.801 * math.sqrt(math.log(totalVisits) / (1 + node.visits))

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

