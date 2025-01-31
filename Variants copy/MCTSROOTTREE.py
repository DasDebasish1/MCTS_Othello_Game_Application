import math
from random import choice
import threading
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
        self.lock = threading.Lock()

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
            return self.children[-1]
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
        if totalVisits == 0:
            return 0
        return node.score / (1 + node.visits) + 2.801 * math.sqrt(math.log(totalVisits) / (1 + node.visits))


class TreeWorkerThread(threading.Thread):
    def __init__(self, root_node, n_simulations, player,mode):
        threading.Thread.__init__(self)
        self.root_node = root_node
        self.n_simulations = n_simulations
        self.player = player
        self.moves = []
        self.mode=mode

    def run(self):
        if self.mode=="Time":
            start = time.time()
            while time.time()-start<self.n_simulations:
                current_node = self.root_node
                current_node.lock.acquire()

                while len(current_node.children) > 0:
                    if current_node == self.root_node and len(current_node.children) < len(self.root_node.state.validMoves()):
                        break
                    new_node = current_node.select()
                    current_node.lock.release()
                    current_node = new_node
                    current_node.lock.acquire()

                current_node.lock.release()

                current_node.lock.acquire()
                next_node_1 = current_node.expand()
                current_node.lock.release()

                result = next_node_1.rollout(self.player)

                next_node_1.lock.acquire()
                next_node_1.backpropagate(result)
                next_node_1.lock.release()
        else:
            for i in range(self.n_simulations):
                current_node = self.root_node
                current_node.lock.acquire()

                while len(current_node.children) > 0:
                    if current_node == self.root_node and len(current_node.children) < len(self.root_node.state.validMoves()):
                        break
                    new_node = current_node.select()
                    current_node.lock.release()
                    current_node = new_node
                    current_node.lock.acquire()

                current_node.lock.release()

                current_node.lock.acquire()
                next_node_1 = current_node.expand()
                current_node.lock.release()

                result = next_node_1.rollout(self.player)

                next_node_1.lock.acquire()
                next_node_1.backpropagate(result)
                next_node_1.lock.release()


        self.moves.append(max(self.root_node.children, key=lambda child: child.visits).move)


class RootWorkerThread(threading.Thread):
    def __init__(self, root_state, n_simulations, C, num_threads_tree, player,mode):
        threading.Thread.__init__(self)
        self.root_state = root_state
        self.n_simulations = n_simulations
        self.C = C
        self.num_threads_tree = num_threads_tree
        self.player = player
        self.mode=mode

    def run(self):
        root_node = Node(self.root_state, C=self.C, expanded=True)

        tree_threads = []
        for _ in range(self.num_threads_tree):
            thread = TreeWorkerThread(root_node, self.n_simulations // self.num_threads_tree if self.mode!="Time" else self.n_simulations, self.player,mode=self.mode)
            tree_threads.append(thread)

        for thread in tree_threads:
            thread.start()

        for thread in tree_threads:
            thread.join()

        combined_moves = [move for thread in tree_threads for move in thread.moves]
        self.best_move = max(set(combined_moves), key=combined_moves.count)
        
        
        #print(f"Root worker result: {best_move}")


def MCTS_Hybrid(root_state, player, n_simulations, C=2, num_threads_root=2, num_threads_tree=2):
    root_threads = []
    for _ in range(num_threads_root):
        thread = RootWorkerThread(root_state, n_simulations, C, num_threads_tree, player)
        root_threads.append(thread)

    for thread in root_threads:

        thread.start()

    for thread in root_threads:
        thread.join()



def MCTS(root_state, player, n_simulations, C=2, num_threads_root=2, num_threads_tree=2,mode="Time",queue=None):
    root_threads = []
    results = []
    
    for _ in range(num_threads_root):
        thread = RootWorkerThread(root_state, n_simulations, C, num_threads_tree, player,mode=mode)
        root_threads.append(thread)

    for thread in root_threads:
        thread.start()

    for thread in root_threads:
        thread.join()
        results.append(thread.best_move)

    best_move = max(set(results), key=results.count)
    if queue:
       queue.put((best_move,0))

    return best_move,0

# def MCTS(root_state,player,n_simulations):
#     mcts = HybridParallelMCTS(root_state, player=player, n_simulations=n_simulations, C=2)
#     a=mcts.run_parallel()
#     return  a
