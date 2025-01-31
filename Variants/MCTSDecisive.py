import time
import pickle
from .MCTS import Node

def MCTS(root_state,player=2,C=2.801,ttime=1,mode="Time",queue=None):

    root = Node(root_state,C=C)
    for move in root.possibleMoves:
        if root.state.is_decisive_move(player, move):
            if queue:
                queue.put((move,n))
            return  move,n
    n=0
    if mode=="Time":
        start = time.time()
        while time.time()-start<ttime:
            node = root
            node = node.select()
            node = node.expand()
            result = node.rollout(player)
            node.backpropagate(result)
            n+=1
        
        
    else:
        n=ttime
        
        for i in range(ttime):
            node = root
            
            node = node.select()
            node = node.expand()
            result = node.rollout(player)
            node.backpropagate(result)
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
                
            n+=1
    if queue:
       queue.put((max(root.children, key=lambda node: node.visits).move,n))
    return  max(root.children, key=lambda node: node.visits).move,n,root

