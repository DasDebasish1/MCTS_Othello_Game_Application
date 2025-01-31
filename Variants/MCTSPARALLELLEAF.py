import concurrent.futures
import time
import pickle
from .MCTS import Node


class LeafParallelMCTS:
    def __init__(self, root_state, player=2, n_simulations=1000, num_threads=4):
        self.root_state = root_state
        self.player = player
        self.n_simulations = n_simulations
        self.num_threads = num_threads

    def run_parallel(self,C,ttime,mode,queue=None):
        root = Node(self.root_state,C=C)
        n=0
        if mode=="Time":
            start = time.time()
            while time.time()-start<ttime:
                node = root
                node = node.select()
                node = node.expand()
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                    futures = [ ]
                    for _ in range(self.num_threads):
                        f= executor.submit(node.rollout,self.player)
                        futures.append(f)
                        
                    concurrent.futures.wait(futures)
                    results = []
                    for future in futures:

                        results.append(future.result())
                node.backpropagate(sum(results))
                n+=1
        else:
            n=ttime
            for _ in range(ttime):
                node = root
                
                node = node.select()
                node = node.expand()
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                    futures = [ ]
                    for _ in range(self.num_threads):
                        f= executor.submit(node.rollout,self.player)
                        futures.append(f)
                        
                    concurrent.futures.wait(futures)
                    results = []
                    for future in futures:

                        results.append(future.result())
                node.backpropagate(sum(results))

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
        
        return  max(root.children, key=lambda node: node.visits).move,n


def MCTS(root_state,player,C,n_simulations,mode="Time",queue=None):
    mcts = LeafParallelMCTS(root_state, player=player, n_simulations=n_simulations, num_threads=4)
    if queue:
       queue.put(mcts.run_parallel(C,n_simulations,mode,queue!=None))
    return  mcts.run_parallel(C,n_simulations,mode)
