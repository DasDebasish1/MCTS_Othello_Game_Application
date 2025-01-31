import math
import multiprocessing  
import time
from random import choice
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

    def calculate_score(self,node,totalVisits):
        return node.score / (1 + node.visits) + 2.831* math.sqrt(math.log(totalVisits) / (1 + node.visits))





class RootParallelMCTS:
    def __init__(self, root_state, player=2, num_threads=4):
        self.root_state = root_state
        self.player = player

        
        self.num_threads = num_threads

    def run_simulation(self,args):
        ttime=args[0]
        mode=args[1]
        root = Node(self.root_state, expanded=True)
        start = time.time()
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
                result = node.rollout(self.player)
                node.backpropagate(result)
                n+=1
            print(n)
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
                n+=1
        return root,n

    def run_parallel(self,ttime,mode="Time"):
        roots = []
        #num_processes = multiprocessing.cpu_count()
        num_processes=8
        with multiprocessing.Pool(processes=num_processes) as pool:
            roots = pool.map(self.run_simulation,[(ttime,mode)]*num_processes)
            
        combined_root = Node(self.root_state, expanded=True)
        total_iterations=0
        for root,n in roots:
            total_iterations+=n
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


def MCTS(root_state,player,ttime,mode="Time",queue=None):
    mcts = RootParallelMCTS(root_state, player=player,num_threads=8)
    if queue:
       queue.put(( mcts.run_parallel(ttime,mode=mode),0))
    return  mcts.run_parallel(ttime,mode=mode)
