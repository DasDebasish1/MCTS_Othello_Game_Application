import concurrent.futures
import time
from .MCTS import Node
import pickle

class RootParallelMCTS:
    def __init__(self, root_state, player=2, n_simulations=1000, C=2, num_threads=4):
        self.root_state = root_state
        self.player = player
        self.n_simulations = n_simulations
        self.C = C
        self.num_threads = num_threads

    def run_simulation(self,id,ttime,mode,C,queue):
        root = Node(self.root_state,C=C)

        if mode=="Time":
            start = time.time()
            while time.time()-start<ttime:
                node = root
                node = node.select()
                node = node.expand()
                result = node.rollout(self.player)
                node.backpropagate(result)
        else:
            for i in range(ttime):
                node = root
               
                node = node.select()
                node = node.expand()
                result = node.rollout(self.player)
                node.backpropagate(result)
                if queue:
                    with open(f'root{id}.pickle', 'wb') as handle:
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
                    
        return root

    def run_parallel(self,ttime,mode,C,queue):
        roots = []
        if queue:
            with open("threadcount.ini","w") as f:
                f.write(str(self.num_threads))
                
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [ ]
            for _ in range(self.num_threads):
                f= executor.submit(self.run_simulation,_,ttime,mode,C,queue)
                futures.append(f)
                
            concurrent.futures.wait(futures)
            roots = []
            for future in futures:
                roots.append(future.result()) 
        combined_root = Node(self.root_state, C=self.C)
        
        n=0
        for root in roots:
            n+=root.visits
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
                        
        print(n/len(roots))
        return  max(combined_root.children, key=lambda node: node.visits).move,n/len(roots)


def MCTS(root_state,player,C,n_simulations,mode="Time",queue=None):
    mcts = RootParallelMCTS(root_state, player=player, n_simulations=n_simulations, C=2, num_threads=16)
    a=mcts.run_parallel(n_simulations,mode,C,queue!=None)
    if queue:
       queue.put(a)
    return  a
