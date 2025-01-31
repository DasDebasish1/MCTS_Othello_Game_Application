import multiprocessing  
import time
from .MCTS import Node
import pickle

class RootParallelMCTS:
    def __init__(self, root_state, player=2, n_processes=4):
        self.root_state = root_state
        self.player = player
        self.n_processes = n_processes

    def run_simulation(self,args):
        ttime=args[0]
        mode=args[1]
        C=args[2]
        queue=args[3]
        id=args[4]
        root = Node(self.root_state,C=C)
        start = time.time()
        n=0
        if mode=="Time":
            start = time.time()
            while time.time()-start<ttime:
                node = root
               
                node = node.select()
                node = node.expand()
                result = node.rollout(self.player)
                node.backpropagate(result)
                n+=1
            
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
                    
                n+=1
        return root,n

    def run_parallel(self,ttime,mode="Time",C=2.801,queue=False):
        roots = []
        #num_processes = multiprocessing.cpu_count()
        if queue:
            with open("threadcount.ini","w") as f:
                f.write(str(self.n_processes))
        args=[]
        for i in range(self.n_processes):
            args.append((ttime,mode,C,queue,i))
        with multiprocessing.Pool(processes=self.n_processes) as pool:
            roots = pool.map(self.run_simulation,args)
            
        combined_root = Node(self.root_state,C=C)
        total_iterations=0
        n=0
        for root,n in roots:
            n+=root.visits
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
        return  max(combined_root.children, key=lambda node: node.visits).move,n,n/len(roots)


def MCTS(root_state,player,C,ttime,mode="Time",queue=None):
    mcts = RootParallelMCTS(root_state, player=player,n_processes=3)
    if queue:
       queue.put(mcts.run_parallel(ttime,mode=mode,queue=True,C=C))
    return  mcts.run_parallel(ttime,mode=mode,C=C)
