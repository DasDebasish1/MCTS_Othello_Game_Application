import pickle
import multiprocessing
import time
from .MCTS import Node
from multiprocessing.managers import BaseManager

# class Node(MCTSNODE):
#     def __init__(self,*args,**kwrgs):
#         super().__init__(*args,**kwrgs)
#         #self.Lock=multiprocessing.Lock()

class TREEParallelMCTS:
    def __init__(self, shared_d ata, player=2, n_simulations=1000, C=2, num_processes=2):
        self.shared_data = shared_data
        self.player = player
        self.n_simulations = n_simulations
        self.C = C
        self.num_processes = num_processes

    def worker(self, process_id,ttime,mode,root):
        #root = self.shared_data['root']
        if mode=="Time":
            start = time.time()
            while time.time()-start<ttime:
                current_node = root
                new_node = current_node.select()
                current_node = new_node
                next_node_1 = current_node.expand()
                result = next_node_1.rollout(self.player)
                next_node_1.backpropagate(result)
        else:
            for i in range(ttime):
                current_node = root
                print(id(current_node))
              
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
    root1 = shared_data['root']
    BaseManager.register('Node', Node)
    manager = BaseManager()
    manager.start()
    root = manager.Node(root1.state)
    for process_id in range(shared_data['num_processes']):
        mcts = TREEParallelMCTS(shared_data, player=shared_data['player'], n_simulations=shared_data['n_simulations'], C=2, num_processes=2)
        process = multiprocessing.Process(target=mcts.worker, args=(process_id,ttime,mode,root))
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
    shared_data = manager.dict({'root': Node(root_state), 'result_queue': manager.Queue(),"n_simulations":n_simulations, 'num_processes': 4, 'player': player})

    best_move = run_parallel(shared_data,n_simulations,mode)
    if queue:
       queue.put((best_move,0))

    return best_move,0