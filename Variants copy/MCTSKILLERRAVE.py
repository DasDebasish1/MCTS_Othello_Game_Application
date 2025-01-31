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
        self.rave_visits = 0
        self.rave_score = 0

    def select(self):
        total_visits = 0
        for child in self.children:
            total_visits += child.visits

        best_node = None
        best_score = float('-inf')
        for node in self.children:
            score = self.calculate_score(node, total_visits)

            if score > best_score:
                best_score = score
                best_node = node
        return best_node

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
        exploration_weight = 2.801
        rave_weight = 0.01
        return (node.score / (1 + node.visits)) + exploration_weight * math.sqrt(math.log(total_visits) / (1 + node.visits)) + (rave_weight * node.rave_score / (1 + node.rave_visits))


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

