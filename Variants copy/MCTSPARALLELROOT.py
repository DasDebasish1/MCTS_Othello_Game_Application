import math
import concurrent.futures
from random import choice
import time
from copy import deepcopy

class Node:
    def __init__(self, state, parent=None, move=None,C=2,expanded=False):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0
        self.C=C
        self.expanded=expanded
        

    
    def select(self):
        totalVisits = 0
        for child in self.children:
            totalVisits += child.visits

        best_node = None
        best_score = float('-inf')
        for node in self.children:
            score = self.calculate_score(node,totalVisits)
            
            if score > best_score:
                best_score = score
                best_node = node
        return best_node
    
    def expand(self):
        possibleMoves = self.state.validMoves()
        if self.state.validMoves() and possibleMoves:
            for move in possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandedState = deepcopy(self.state)
                    expandedState.make_move(move)
                    self.children.append(Node(expandedState, parent=self, move=move,C=self.C))
                  
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

    def calculate_score(self,node,totalVisits):
        return node.score / (1 + node.visits) + 2.801* math.sqrt(math.log(totalVisits) / (1 + node.visits))



class RootParallelMCTS:
    def __init__(self, root_state, player=2, n_simulations=1000, C=2, num_threads=4):
        self.root_state = root_state
        self.player = player
        self.n_simulations = n_simulations
        self.C = C
        self.num_threads = num_threads

    def run_simulation(self,ttime,mode):
        root = Node(self.root_state, C=self.C, expanded=True)

        if mode=="Time":
            start = time.time()
            while time.time()-start<ttime:
                node = root
                while len(node.children) > 0:
                    if node == root and len(node.children) < len(root.state.validMoves()):
                        break
                    node = node.select()
                node = node.expand()
                result = node.rollout(self.player)
                node.backpropagate(result)
        else:
            for i in range(ttime):
                node = root
                while len(node.children) > 0:
                    if node == root and len(node.children) < len(root.state.validMoves()):
                        break
                    node = node.select()
                node = node.expand()
                result = node.rollout(self.player)
                node.backpropagate(result)
        return root

    def run_parallel(self,ttime,mode):
        roots = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [ ]
            for _ in range(self.num_threads):
                f= executor.submit(self.run_simulation,ttime,mode)
                futures.append(f)
                
            concurrent.futures.wait(futures)
            roots = []
            for future in futures:
                roots.append(future.result()) 
        combined_root = Node(self.root_state, C=self.C, expanded=True)
        
        
        for root in roots:
            for child in root.children:
                new=True
                for i in combined_root.children:
                    if i.move==child.move:
                        i.visits+=child.visits
                        i.score+=child.score
                        new=False
                        break
                if new:
                    combined_root.children.append(child)
                        

        return  max(combined_root.children, key=lambda node: node.visits).move


def MCTS(root_state,player,n_simulations,mode="Time",queue=None):
    mcts = RootParallelMCTS(root_state, player=player, n_simulations=n_simulations, C=2, num_threads=8)
    a=mcts.run_parallel(n_simulations,mode)
    if queue:
       queue.put((a,0))
    return  a,0
