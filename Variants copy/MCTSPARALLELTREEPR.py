import math
from random import choice
import pickle
import multiprocessing
import time
from copy import deepcopy

class Node:
    def __init__(self, state, parent=None, move=None, C=2, expanded=False):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0
        self.C = C
        self.expanded = expanded
        #self.lock = threading.Lock()

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
        return best_node

    def expand(self):
        possibleMoves = self.state.validMoves()
        if self.state.validMoves() and possibleMoves:
            for move in possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandedState = deepcopy(self.state)
                    expandedState.make_move(move)
                    child_node = Node(expandedState, parent=self, move=move, C=self.C)
                    self.children.append(child_node)
                    return child_node
        else:
            return self

    def rollout(self, player):
        currentState = deepcopy(self.state)
        while currentState.validMoves():
            all_moves = currentState.validMoves()
            move = choice(all_moves)
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
        if totalVisits==0:
            return 0
        return node.score / (1 + node.visits) + 2.801 * math.sqrt(math.log(totalVisits) / (1 + node.visits))


class TREEParallelMCTS:
    def __init__(self, shared_data, player=2, n_simulations=1000, C=2, num_processes=2):
        self.shared_data = shared_data
        self.player = player
        self.n_simulations = n_simulations
        self.C = C
        self.num_processes = num_processes

    def worker(self, process_id,ttime,mode):
        root = self.shared_data['root']
        if mode=="Time":
            start = time.time()
            while time.time()-start<ttime:
        
                current_node = root

                while len(current_node.children) > 0:
                    if current_node == root and len(current_node.children) < len(root.state.validMoves()):
                        break
                    new_node = current_node.select()
                    current_node = new_node

                next_node_1 = current_node.expand()
                result = next_node_1.rollout(self.player)
                next_node_1.backpropagate(result)
        else:
            for i in range(ttime):
                current_node = root
                while len(current_node.children) > 0:
                    if current_node == root and len(current_node.children) < len(root.state.validMoves()):
                        break
                    current_node = current_node.select()
                next_node_1 = current_node.expand()
                result = next_node_1.rollout(self.player)
                next_node_1.backpropagate(result)
                with open('filename.pickle', 'wb') as handle:
                    pickle.dump(root, handle, protocol=pickle.HIGHEST_PROTOCOL)
                print("eeeeeeeee")
                time.sleep(10)
        best_move = max(set(root.children), key=lambda child: child.visits).move
        self.shared_data['result_queue'].put(best_move)

def run_parallel(shared_data,ttime,mode):
    processes = []

    for process_id in range(shared_data['num_processes']):
        mcts = TREEParallelMCTS(shared_data, player=shared_data['player'], n_simulations=shared_data['n_simulations'], C=2, num_processes=2)
        process = multiprocessing.Process(target=mcts.worker, args=(process_id,ttime,mode))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    results = [shared_data['result_queue'].get() for _ in range(shared_data['num_processes'])]
    best_move = max(set(results), key=results.count)
    return best_move

def MCTS(root_state, player, n_simulations, mode="Time",queue=None):
    
    manager = multiprocessing.Manager()
    shared_data = manager.dict({'root': Node(root_state, C=2.831, expanded=True), 'result_queue': manager.Queue(),"n_simulations":n_simulations, 'num_processes': 4, 'player': player})

    best_move = run_parallel(shared_data,n_simulations,mode)
    if queue:
       queue.put((best_move,0))

    return best_move,0