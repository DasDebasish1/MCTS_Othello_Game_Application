import threading
import time
import pickle
from copy import deepcopy
from random import choice
from .MCTS import Node as MCTSNODE

class Node(MCTSNODE):
    def __init__(self, *args, **kwrgs):
        super().__init__(*args , **kwrgs)
        self.lock= threading.Lock()
    def expand(self):
        if self.possibleMoves:
            expandableMoves=[]
            for move in self.possibleMoves:
                if move not in [child.move for child in self.children]:
                    expandableMoves.append(move)
            if expandableMoves:
                expandedMove=choice(expandableMoves)
                expandedState = deepcopy(self.state)
                expandedState.make_move(expandedMove)
                self.children.append(Node(expandedState, parent=self, move=expandedMove))
                return self.children[-1]
            else:
                return self
        else:
            return self
def copyRoot(root):
    copy_root=MCTSNODE(root.state)
    copy_root.visits=root.visits
    copy_root.score=root.score
    for child in root.children:
        copy_root.children.append(copyRoot(child))
    return copy_root


class TREEParallelMCTS:
    def __init__(self, root_state, player=2, n_simulations=1000, C=2, num_threads=2):
        self.root_state = root_state
        self.player = player
        self.n_simulations = n_simulations
        self.C = C
        self.num_threads = num_threads 
        self.root = Node(self.root_state)
        self.thread_results = []
        self.iterations=0

    def worker(self,ttime,mode,queue):
        n=0
        if mode=="Time":
            start = time.time()
            while time.time()-start<ttime:
            #print(_)
                current_node = self.root
                current_node.lock.acquire()
                

                new_node = current_node.select()
                current_node.lock.release()
                current_node=new_node
              

                current_node.lock.acquire()
                next_node_1 = current_node.expand()
                current_node.lock.release()

                result = next_node_1.rollout(self.player)

                next_node_1.lock.acquire()
                next_node_1.backpropagate(result)
                next_node_1.lock.release()
                n+=1
        else:
            n=ttime
            for i in range(ttime):
                current_node = self.root
                current_node.lock.acquire()
                new_node = current_node.select()
                current_node.lock.release()
                current_node=new_node
                current_node.lock.acquire()
                    
                current_node.lock.release()

                
                current_node.lock.acquire()
                next_node_1 = current_node.expand()
                current_node.lock.release()

                result = next_node_1.rollout(self.player)

                next_node_1.lock.acquire()
                next_node_1.backpropagate(result)
                next_node_1.lock.release()
                self.root.lock.acquire()
                if queue:
                    with open('filename.pickle', 'wb') as handle:
                        pickle.dump(copyRoot(self.root), handle, protocol=pickle.HIGHEST_PROTOCOL)
                    try:
                        PauseStatus=True
                        while PauseStatus:
                            f= open("setting.ini","r")
                            PauseStatus=f.read()=="1"
                            f.close()
                    except:
                        pass
                self.root.lock.release()
                time.sleep(0.5)
                
        self.iterations+=n
        self.thread_results.append(max(self.root.children, key=lambda child: child.visits).move)

    def run_parallel(self,ttime,mode,queue=None):
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker,args=[ttime,mode,queue])
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        best_move = max(set(self.thread_results), key=self.thread_results.count)
        return best_move,self.iterations

def MCTS(root_state, player,C, n_simulations,mode="Time",queue=None):
    mcts = TREEParallelMCTS(root_state, player=player, n_simulations=n_simulations, C=2, num_threads=4)
    if queue:
       queue.put(mcts.run_parallel(n_simulations,mode,True))
    return mcts.run_parallel(n_simulations,mode)