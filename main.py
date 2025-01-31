from PyQt5 import QtWidgets, uic,QtGui,QtCore
import sys
from multiprocessing import Process,Queue
import os
import importlib
from game import Game
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QRectF
import pickle
import time

VISUALIZATION = False
EXPANDED = False
Scale = 1
NODE_WIDTH = 60
NODE_HEIGHT = 120
X_OFFSET = 30
Y_OFFSET = 50
FONT_SIZE = 20
X = 600
Y = 50

class Node:
    def __init__(self, visits, score, state):
        self.visits = visits
        self.score = score
        self.state = state
        self.children = []

# Sample state class, replace it with your actual state class
class State:
    def __init__(self, board):
        self.board = board


class TreeView(QGraphicsView):
    def __init__(self, scene):
        super(TreeView, self).__init__(scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        self.scenes=[QtWidgets.QGraphicsScene(self),QtWidgets.QGraphicsScene(self),QtWidgets.QGraphicsScene(self)]
        self.currentScene=0
        self.setScene(self.scenes[self.currentScene])
        self.setBackgroundBrush(QtGui.QColor("gray"))
        self.setDragMode(QGraphicsView.ScrollHandDrag)
    def resetScene(self):
        self.scene().clear()
        #self.currentScene+=1
        # if self.currentScene>2:
        #     self.currentScene=0
        # self.setScene(self.scenes[self.currentScene])


    def wheelEvent(self, event):
        global NODE_HEIGHT, NODE_WIDTH, X_OFFSET, Y_OFFSET, Scale, FONT_SIZE
        if event.angleDelta().y() > 0:
            if  Scale<2:
                NODE_HEIGHT *= 1.1
                NODE_WIDTH *= 1.1
                X_OFFSET *= 1.1
                Y_OFFSET *= 1.1
                FONT_SIZE *= 1.1
                Scale*=1.1
        elif Scale>0.1:
            NODE_HEIGHT *= 0.9
            NODE_WIDTH *= 0.9
            X_OFFSET *= 0.9
            Y_OFFSET *= 0.9
            FONT_SIZE *= 0.9
            Scale*=0.9
            
        self.scene().update()


    def draw_node(self, node, x, y, clickable=True):
        viewport_rect=QtCore.QRect(0, 0, self.viewport().width(), self.viewport().height())
        visible_scene_rect = self.mapToScene(viewport_rect).boundingRect()
        if visible_scene_rect.contains(x,y) or visible_scene_rect.contains(x,y+NODE_HEIGHT) or visible_scene_rect.contains(x+NODE_WIDTH,y) or visible_scene_rect.contains(x+NODE_WIDTH,y+NODE_HEIGHT):#(x > -NODE_WIDTH) and y > -NODE_HEIGHT:
            rect_item = QGraphicsRectItem(x, y, NODE_WIDTH, NODE_HEIGHT)
            self.scene().addItem(rect_item)

            # if clickable:
            #     CLICKABLE_NODES.append([rect_item, node])

            rect_item.setPen(QtGui.QColor("black"))

            if Scale>0.4:
                font = QtGui.QFont()
                font.setPixelSize(int(FONT_SIZE))

                text_item = QtWidgets.QGraphicsTextItem(f"V: {node.visits}\nS: {node.score}")
                text_item.setFont(font)
                text_item.setPos(x , y + NODE_HEIGHT / 2)
                self.scene().addItem(text_item)

                for j, row in enumerate(node.state.board):
                    for i, v in enumerate(row):
                        rect = QGraphicsRectItem(
                            x + i * NODE_WIDTH / 9, y + j * NODE_WIDTH / 9,
                            NODE_WIDTH / 9, NODE_WIDTH / 9
                        )
                        rect.setPen(QtGui.QColor("black"))
                        self.scene().addItem(rect)

                        if v != 0:
                            color = QtGui.QColor("white") if v == 2 else QtGui.QColor("black")
                            circle = QtWidgets.QGraphicsEllipseItem(
                                x + i * NODE_WIDTH / 9, y + j * NODE_WIDTH / 9,
                                NODE_WIDTH / 9, NODE_WIDTH / 9
                            )
                            circle.setBrush(color)
                            self.scene().addItem(circle)

    def draw_tree(self,node,x,y):
        
        y+=NODE_HEIGHT+Y_OFFSET
        drawables=[]
        for i,child in enumerate(node.children):
            if child.visits!=0:
                drawables.append(i)
        if drawables:
            for i,child in enumerate(node.children):
                w=self.calculate_width(child)
                self.draw_node(child,x+w/2,y)
                
                if i!=drawables[0]:
                    line_item = QtWidgets.QGraphicsLineItem(x+w/2+NODE_WIDTH/2,y-Y_OFFSET/2,x+NODE_WIDTH/2,y-Y_OFFSET/2)
                    line_item.setPen(Qt.black)
                    self.scene().addItem(line_item)
                if i!=drawables[-1]:
                    line_item = QtWidgets.QGraphicsLineItem(x+w/2+NODE_WIDTH/2,y-Y_OFFSET/2,x+w+X_OFFSET,y-Y_OFFSET/2)
                    line_item.setPen(Qt.black)
                    self.scene().addItem(line_item)
                if child.children :#and child.expanded:
                    line_item = QtWidgets.QGraphicsLineItem(x+w/2+NODE_WIDTH/2,y+NODE_HEIGHT,x+w/2+NODE_WIDTH/2,y+NODE_HEIGHT+Y_OFFSET/2)
                    line_item.setPen(Qt.black)
                    self.scene().addItem(line_item)
                line_item = QtWidgets.QGraphicsLineItem(x+w/2+NODE_WIDTH/2,y,x+w/2+NODE_WIDTH/2,y-Y_OFFSET/2)
                line_item.setPen(Qt.black)
                self.scene().addItem(line_item)

                self.draw_tree(child,x,y)
                x+=w

    def calculate_width(self, node):
        w = 0

        if node.children:
            for child in node.children:
                if child.visits != 0:
                    w += self.calculate_width(child)
            if w == 0:
                return NODE_WIDTH + X_OFFSET
            return w
        else:
            return NODE_WIDTH + X_OFFSET


class TreeScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(TreeScene, self).__init__(parent)
      


class Piece(QtWidgets.QGraphicsEllipseItem):

    def __init__(self,*args,**kwrgs):
        super(Piece, self).__init__(*args,**kwrgs)
        self.callback=None

    def mousePressEvent(self, QMouseEvent):
        #super(Piece, self).mousePressEvent(QMouseEvent)
        if self.callback:
            self.callback()
    

class OthelloBoard(QtWidgets.QGraphicsView):
    def __init__(self):
        super(OthelloBoard, self).__init__()
        self.cell_size = 50
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.installEventFilter(self)
        self.board_size = 8
        self.setFixedSize(self.cell_size*9,self.cell_size*9)
        
    
   
    def redraw(self,game,showMoves=False,callback=None,invalidcallback=None):
        board=game.board
        
        possible_moves=game.validMoves()
        self.scene.clear()
        for row in range(self.board_size):
            for col in range(self.board_size):
                x, y = col * self.cell_size, row * self.cell_size
                rect_item = QtWidgets.QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                rect_item.setPen(QtGui.QPen(QtCore.Qt.black))
                rect_item.setBrush(QtGui.QBrush(QtCore.Qt.green))
                self.scene.addItem(rect_item)

        # Add initial pieces to the board
        for j,row in enumerate(board):
            for i,v in enumerate(row):
                if (j,i) in possible_moves:
                    self.add_piece(i, j, "blue" if showMoves else QtCore.Qt.green,callback)
                elif v==0:
                     self.add_piece(i, j, QtCore.Qt.green,invalidcallback)
                    
                if v!=0:
                    self.add_piece(i, j, "black" if v==1 else "white")
                

    def add_piece(self, row, col, color,callback=None):
        self.cell_size = 50
        x, y = col * self.cell_size+5, row * self.cell_size+5
        ellipse_item = Piece(x, y, 40, 40)
        if callback:
            ellipse_item.callback=lambda:callback(((col,row),1))
        pen = QtGui.QPen(Qt.NoPen)
        ellipse_item.setPen(pen)

        ellipse_item.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        self.scene.addItem(ellipse_item)



class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(tuple)

    def __init__(self, ai, game ,mode, time, C):
        super().__init__()

        self.ai = ai
        self.game = game
        self.time = time
        self.mode = mode
        self.C=C
    
    
    def run(self):
        queue = Queue()
        p = Process(target=self.ai,args=(self.game, self.game.currentPlayer,self.C, self.time,self.mode,queue))
        
        p.start()
        #print(type(queue.get().copy()))
        a=queue.get()
        #move = self.ai(self.game, self.game.currentPlayer, self.time,mode=self.mode,UT=self.UT)
        self.finished.emit(a)#move[0])


class TreeWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(tuple)

    def __init__(self,UT):
        super().__init__()
        self.UT=UT
        self.lastupdated=""
     
    
    
    def run(self):
        while 1:
            multi=False
            a=os.path.getmtime('filename.pickle')
            
            b=os.path.getmtime('root0.pickle')
            
            while 1:
                
                if os.path.getmtime('filename.pickle')!=a:
                    break
                elif os.path.getmtime('root0.pickle')!=b:
                    multi=True
                    break
            with open("threadcount.ini", "r") as f:
                threadcount=int(f.read())
            while 1:
                if multi:
                    all=[]
                    for i in range(threadcount):
                        try:
                            with open(f'root{i}.pickle', 'rb') as handle:
                                all.append(pickle.load(handle))
                        except:
                            pass
                    self.UT(all)
                    time.sleep(0.5)
                    if os.path.getmtime('filename.pickle')!=a:
                        break
                    
                    
                else:
                    try:
                        with open('filename.pickle', 'rb') as handle:
                            d = pickle.load(handle)
                            self.UT(d)
                        time.sleep(0.5)
                        
                        if os.path.getmtime('root0.pickle')!=b:
                            
                            break
                    
                    except:
                        pass


class ResultEvent(QtCore.QEvent):
    def __init__(self, result):
        super().__init__(QtCore.QEvent.User)
        self.result = result

class Ui(QtWidgets.QWidget):
    moveselected = QtCore.pyqtSignal(tuple)
    utsignal = QtCore.pyqtSignal()

    def __init__(self,a):
        super(Ui, self).__init__()
        uic.loadUi('main.ui', self)
        self.a=a
        self.player1type.currentIndexChanged.connect(lambda index: self.player1typewindow.setCurrentIndex(index))
        self.player1mode.currentIndexChanged.connect(lambda index: self.player1modewindow.setCurrentIndex(index))
        
        self.player2type.currentIndexChanged.connect(lambda index: self.player2typewindow.setCurrentIndex(index))
        self.player2mode.currentIndexChanged.connect(lambda index: self.player2modewindow.setCurrentIndex(index))
        self.play.clicked.connect(self.onplay)
        
        self.label_13.setFixedSize(40,40)
        self.label_15.setFixedSize(40,40)
        self.blackp.setFixedSize(40,40)
        self.whitep.setFixedSize(40,40)
        self.player1wins=0
        self.player2wins=0
        self.tie=0
        self.root=None
        self.worker1 = TreeWorker(self.updateTree)
        self.mctsthread1 = QtCore.QThread()
        self.worker1.moveToThread(self.mctsthread1)
        #self.worker1.finished.connect(self.handleMove)
        self.mctsthread1.started.connect(self.worker1.run)
        self.mctsthread1.start()

        self.utsignal.connect(self.redraw_tree)


        self.whitep.hide()
        self.loadMCTS()

        self.moveselected.connect(self.handleMove)
        self.nextgame.clicked.connect(self.startGame)

        #self.Tree = TreePlotter(None)
        scene = TreeScene()
        self.Tree = TreeView(scene)
        self.Tree.show()
        self.tree_plot.addWidget(self.Tree)

        self.game = Game([])
        self.othello_board = OthelloBoard()
        self.board.addWidget(self.othello_board)

        self.showmoves.stateChanged.connect(self.refreshBoard)

        self.othello_board.redraw(self.game)
        #self.show()
        self.ishuman=False
        self.showMaximized()

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            print(event.text())
            if event.text()==" ":
                print("Paused")
                try:
                    with open("setting.ini","r") as f:
                        pause=f.read()=="1"
                    with open("setting.ini","w") as f:
                        f.write("0" if pause else "1")
                        print(pause)
                except:
                    pass
                    

    def loadMCTS(self):
        all_variants=[x.replace(".py","") for x in os.listdir("Variants") if x.endswith(".py")]
        #for variant in all_variants:
        self.ai1combo.addItems(all_variants)
        self.ai2combo.addItems(all_variants)
    
    def redraw_tree(self):
        # self.Tree.scene().clear()
        self.Tree.resetScene()
        if type(self.root)==type([]):
            w=0
            for i in  self.root:
                #self.Tree.draw_tree(i,-500+w+20,-500)
                self.Tree.draw_node(i,-500+w+20+(self.Tree.calculate_width(i)/2),-500+NODE_HEIGHT+Y_OFFSET)
                line_item = QtWidgets.QGraphicsLineItem(-500+w+20+(self.Tree.calculate_width(i)/2)+NODE_WIDTH/2,-500+NODE_HEIGHT*2+Y_OFFSET+Y_OFFSET/2,-500+w+20+(self.Tree.calculate_width(i)/2)+NODE_WIDTH/2,-500+NODE_HEIGHT*2+Y_OFFSET)
                line_item.setPen(Qt.black)
                self.Tree.scene().addItem(line_item)
                self.Tree.draw_tree(i,-500+w+20,-500+NODE_HEIGHT+Y_OFFSET)
                w+=self.Tree.calculate_width(i)+NODE_WIDTH
                
            
        else:
            self.Tree.draw_node(self.root,-500+20+(self.Tree.calculate_width(self.root)/2),-500+NODE_HEIGHT+Y_OFFSET)
            line_item = QtWidgets.QGraphicsLineItem(-500+20+(self.Tree.calculate_width(self.root)/2)+NODE_WIDTH/2,-500+NODE_HEIGHT*2+Y_OFFSET+Y_OFFSET/2,-500+20+(self.Tree.calculate_width(self.root)/2)+NODE_WIDTH/2,-500+NODE_HEIGHT*2+Y_OFFSET)
            line_item.setPen(Qt.black)
            self.Tree.scene().addItem(line_item)
            self.Tree.draw_tree(self.root,-500,-500+NODE_HEIGHT+Y_OFFSET)
        

    def startGame(self):
        with open("setting.ini","w") as f:
            f.write("0")
            
        self.iteration1=0
        self.iteration2=0
        self.nextgame.hide()
        self.winnerlabel.hide()

        self.game=Game([]) 
        self.game.reset_board()
        self.refreshBoard()
        if self.player1type.currentIndex()==1:
            self.ai1=self.ai1combo.currentText()
            self.ai1t=self.ai1time.value() if self.player1mode.currentIndex()==0 else self.ai1iterations.value()
            self.ai1mode="Time" if self.player1mode.currentIndex()==0 else "Iteration"
            self.ai1mcts = importlib.import_module(f"Variants.{self.ai1}").MCTS
        if self.player2type.currentIndex()==1:
            self.ai2=self.ai2combo.currentText()
            self.ai2t=self.ai2time.value() if self.player2mode.currentIndex()==0 else self.ai2iterations.value()
            self.ai2mode="Time" if self.player2mode.currentIndex()==0 else "Iteration"
            self.ai2mcts = importlib.import_module(f"Variants.{self.ai2}").MCTS
        if self.mode.currentIndex()==1:
            self.a.append([self.ai1,self.ai1mcts,self.ai1t,self.ai1mode,self.player1constant.value()])
            self.a.append([self.ai2,self.ai2mcts,self.ai2t,self.ai2mode,self.player2constant.value()])
            self.a.append(self.nogames.value())
            self.close()
            return
        
        
        self.getMove()
        
    def getMove(self):
        if self.game.validMoves():
            if hasattr(self, 'mctsthread'):
                if self.mctsthread.isRunning():
                    self.mctsthread.wait()
            if self.game.currentPlayer==1:
                if self.player1type.currentIndex()==1:
                    self.worker = Worker(self.ai1mcts,self.game,self.ai1mode,self.ai1t,self.player1constant.value())
                else:
                    self.ishuman=True             

                    self.refreshBoard(True)       
                    return
            else:
                if self.player2type.currentIndex()==1:
                    self.worker = Worker(self.ai2mcts,self.game,self.ai2mode,self.ai2t,self.player2constant.value())
                else:
                    self.ishuman=True             

                    self.refreshBoard(True)

                    return

            self.mctsthread = QtCore.QThread()
            self.worker.moveToThread(self.mctsthread)
            self.worker.finished.connect(self.handleMove)

            self.mctsthread.started.connect(self.worker.run)
            self.mctsthread.start()
        else:
            self.finishGame()
    def handleMove(self,move):
        self.ishuman=False
        if self.game.currentPlayer==1:
            self.iteration1+=move[1]
        else:
            self.iteration2+=move[1]
        self.game.make_move(move[0])
        
        self.refreshBoard()
        if hasattr(self, 'worker'):
            self.worker.thread().quit()
            self.worker.thread().wait()
        self.getMove()
       

    def finishGame(self):
        print("Game ENded")
        self.winnerlabel.show()
        if self.game.get_result()==1:
            self.winnerlabel.setText("Player 1 Wins")
            self.player1wins+=1
        elif self.game.get_result()==-1:
            self.winnerlabel.setText("Player 2 Wins")
            self.player2wins+=1

        else:
            self.winnerlabel.setText("Tie")
            self.tie+=1

        self.player1winslabel.setText(str(self.player1wins))
        self.player2winslabel.setText(str(self.player2wins))
        self.tielabel.setText(str(self.tie))
        if self.nogames.value()==self.player1wins+self.player2wins+self.tie:
            with open(f"{self.ai1}_{self.ai1t} vs {self.ai2}_{self.ai2t}.txt","w") as f:
                f.write(f"Player 1 ({self.ai1}) Wins : {self.player1wins} Average Iterations : {self.iteration1/self.nogames.value()}\nPlayer 2 ({self.ai2}) Wins : {self.player2wins} Average Iterations : {self.iteration1/self.nogames.value()}\n Tie : {self.tie}")
        else:
            self.nextgame.show()
        

    def onplay(self):
        self.stackedWidget.setCurrentIndex(1)
        self.startGame()

    def updateTree(self,root):
        self.root=root
        self.utsignal.emit()

    def showinvalidMsg(self,a):
        msg = QtWidgets.QMessageBox() 
        msg.setIcon(QtWidgets.QMessageBox.Information) 
    
        # setting message for Message Box 
        msg.setText("You cannot place a piece at there") 
        
        # setting Message box window title 
        msg.setWindowTitle("Wrong Move ") 
        
        # declaring buttons on Message Box 
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok ) 
        
        # start the app 
        retval = msg.exec_()
        self.refreshBoard(True)   
    
    def refreshBoard(self,ishuman=False):
        if self.ishuman:
            self.othello_board.redraw(self.game,self.showmoves.isChecked() ,self.moveselected.emit,self.showinvalidMsg)
        else:
            self.othello_board.redraw(self.game,self.showmoves.isChecked() , None)


        self.blackpieces.setText(str(sum(row.count(1) for row in self.game.board)))
        self.whitepieces.setText(str(sum(row.count(2) for row in self.game.board)))
        if self.game.currentPlayer==1:
            self.whitep.hide()
            self.blackp.show()
        else:
            self.blackp.hide()
            self.whitep.show()


if __name__=="__main__":
    a=[]
    app = QtWidgets.QApplication(sys.argv)
    window = Ui(a)
    app.exec_()
    if a:
        player1=0
        player2=0
        tie=0

        ai1=a[0]
        ai2=a[1]
        total_iterations1=0
        total_iterations2=0
        
        for i in range(a[2]):
            game=Game([])
            game.reset_board()
            while game.validMoves():
                if game.currentPlayer==1:
                    print(ai1[0], "1 thinking")
                    move=ai1[1](game, game.currentPlayer, ai1[4], ai1[2],mode=ai1[3])
                    game.make_move(move[0])
                    total_iterations1+=move[1]
                    
                elif game.currentPlayer==2:
                    print(ai2[0], "2 thinking")
                    move=ai2[1](game, game.currentPlayer ,ai2[4], ai2[2],mode=ai2[3])
                    game.make_move(move[0])
                    total_iterations2+=move[1]
            result = game.get_result()

            if result==1:
                player1+=1
                print(ai1[0],"Wins")
                
            elif result==-1:
                player2+=1
                print(ai2[0],"Wins")
               
            else:
                tie+=1
                print("Tie")    
               

        print(f"Player 1 : {player1}  ,  player 2 : {player2}   ,  Tie : {tie}")
        with open(f"{ai1[0]}_{ai1[2]} vs {ai2[0]}_{ai2[2]}.txt","w") as f:
                f.write(f"Player 1 ({ai1[0]}) Wins : {player1} Average Iterations : {int(total_iterations1/a[2])}\nPlayer 2 ({ai2[0]}) Wins : {player2} Average Iterations : {int(total_iterations2/a[2])}\n Tie : {tie}")
