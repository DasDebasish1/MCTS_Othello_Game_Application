from PyQt5 import QtWidgets, uic,QtGui,QtCore
import sys
import os
import importlib
from game import Game

class TreePlotter(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.root = None
        self.NODE_WIDTH=100
        self.NODE_HEIGHT=300
        self.Y_OFFSET=20
        self.X_OFFSET=20
    def draw_tree(self, node, x, y):
        #node.draw_node()
        y += self.NODE_HEIGHT + self.Y_OFFSET
        for child in node.children:
            if child.visits != 0:
                #child.draw_node()
                w = self.calculate_width(child)
                edge = QtWidgets.QGraphicsLineItem(x + w / 2 + self.NODE_WIDTH / 2, y - self.Y_OFFSET / 2, x + self.NODE_WIDTH / 2, y - self.Y_OFFSET / 2)
                self.scene.addItem(edge)
                if child.children and child.expanded:
                    edge = QtWidgets.QGraphicsLineItem(x + w / 2 + self.NODE_WIDTH / 2, y + self.NODE_HEIGHT, x + w / 2 + self.NODE_WIDTH / 2, y + self.NODE_HEIGHT + self.Y_OFFSET / 2)
                    self.scene.addItem(edge)
                edge = QtWidgets.QGraphicsLineItem(x + w / 2 + self.NODE_WIDTH / 2, y, x + w / 2 + self.NODE_WIDTH / 2, y - self.Y_OFFSET / 2)
                self.scene.addItem(edge)
                if child.expanded:
                    self.draw_tree(child, x, y)
                x += w
    
    def calculate_width(self, node):
        w = 0
        if node.children:
            for child in node.children:
                if child.visits != 0:
                    w += self.calculate_width(child)
            if w == 0:
                return self.NODE_WIDTH + self.X_OFFSET
            return w
        else:
            return self.NODE_WIDTH + self.X_OFFSET

    def show_tree(self,root):
        self.scene.clear()
        x = 0
        y = 0
        self.draw_tree(root, x, y)

class Piece(QtWidgets.QGraphicsEllipseItem):

    def __init__(self,*args,**kwrgs):
        super(Piece, self).__init__(*args,**kwrgs)
        self.callback=None

    def mousePressEvent(self, QMouseEvent):
        super(Piece, self).mousePressEvent(QMouseEvent)

        if self.callback:
            self.callback()
    

class OthelloBoard(QtWidgets.QGraphicsView):
    def __init__(self):
        super(OthelloBoard, self).__init__()
        self.cell_size = 50
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.installEventFilter(self)
        self.setScene(self.scene)
        self.board_size = 8
        self.setFixedSize(self.cell_size*9,self.cell_size*9)
        
 
   
    def redraw(self,game,showMoves=False,callback=None):
        board=game.board
        possible_moves=[]
        if showMoves:
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
                if showMoves:
                    if (j,i) in possible_moves:

                        self.add_piece(i, j, "blue",callback)

                if v!=0:
                    self.add_piece(i, j, "black" if v==1 else "white")
                

    def add_piece(self, row, col, color,callback=None):
        self.cell_size = 50
        x, y = col * self.cell_size+5, row * self.cell_size+5
        ellipse_item = Piece(x, y, 40, 40)
        if callback:
            ellipse_item.callback=lambda:callback((col,row))


        ellipse_item.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        self.scene.addItem(ellipse_item)


# class Worker(QtCore.QObject):
#     finished = QtCore.pyqtSignal()
#     update_signal = QtCore.pyqtSignal(list)

#     def __init__(self, ai1, ai2, times):
#         super().__init__()
#         self.ai1 = ai1
#         self.ai2 = ai2
#         self.times = times
    
    
#     def run(self):
#         game = Game([])
#         for tt in range(self.times):
#             game.reset_board()
#             #self.redraw(game.board)
#             self.update_signal.emit(game.board)
#             print("redrawn")
#             while game.validMoves():
#                 if game.currentPlayer == 1:
#                     move = self.ai1[0](game, game.currentPlayer, self.ai1[2])
#                     game.make_move(move[0])
#                     #self.redraw(game.board)
#                     self.update_signal.emit(game.board)
#                     print("redrawn")
                    
                    
#                 elif game.validMoves():
#                     move = self.ai2[0](game, game.currentPlayer, self.ai2[2])
#                     game.make_move(move[0])
#                     #self.redraw(game.board)
#                     self.update_signal.emit(game.board)
#                     print("redrawn")

#             result = game.get_result()
#             QtWidgets.QApplication.postEvent(window, ResultEvent(result))


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(tuple)

    def __init__(self, ai, game ,mode, time,UT):
        super().__init__()

        self.ai = ai
        self.game = game
        self.time = time
        self.mode = mode
        self.UT=UT
    
    
    def run(self):
        move = self.ai(self.game, self.game.currentPlayer, self.time,mode=self.mode,UT=self.UT)
        self.finished.emit(move[0])


class ResultEvent(QtCore.QEvent):
    def __init__(self, result):
        super().__init__(QtCore.QEvent.User)
        self.result = result

class Ui(QtWidgets.QWidget):
    moveselected = QtCore.pyqtSignal(tuple)
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




        self.whitep.hide()
        self.loadMCTS()

        self.moveselected.connect(self.handleMove)
        self.nextgame.clicked.connect(self.startGame)

        self.Tree = TreePlotter(None)
        self.tree_plot.addWidget(self.Tree)

        self.game = Game([])
        self.othello_board = OthelloBoard()
        self.board.addWidget(self.othello_board)

        self.showmoves.stateChanged.connect(self.refreshBoard)

        self.othello_board.redraw(self.game)
        #self.show()
        self.showMaximized()



    def loadMCTS(self):
        all_variants=[x.replace(".py","") for x in os.listdir("Variants") if x.endswith(".py")]
        #for variant in all_variants:
        self.ai1combo.addItems(all_variants)
        self.ai2combo.addItems(all_variants)
    
   
    def startGame(self):
        
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
            self.a.append([self.ai1,self.ai1mcts,self.ai1t,self.ai1mode])
            self.a.append([self.ai2,self.ai2mcts,self.ai2t,self.ai2mode])
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
                    self.worker = Worker(self.ai1mcts,self.game,self.ai1mode,self.ai1t,lambda root:self.updateTree(root))
                else:
                    self.refreshBoard(True)                    
                    return
            else:
                if self.player2type.currentIndex()==1:
                    self.worker = Worker(self.ai2mcts,self.game,self.ai2mode,self.ai2t,lambda root:self.updateTree(root))
                else:
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
        self.game.make_move(move)
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
        elif self.game.get_result()==2:
            self.winnerlabel.setText("Player 2 Wins")
            self.player2wins+=1

        else:
            self.winnerlabel.setText("Tie")
            self.tie+=1

        self.player1winslabel.setText(str(self.player1wins))
        self.player2winslabel.setText(str(self.player2wins))
        self.tielabel.setText(str(self.tie))
        
        self.nextgame.show()
        

    def onplay(self):
        self.stackedWidget.setCurrentIndex(1)
        
        self.startGame()

        #self.tree_plot.addWidget(self.treeplotter)
        # ai1=self.ai1combo.currentText()
        # ai1time=self.ai1time.value()
        # ai1mcts = importlib.import_module(f"Variants.{ai1}").MCTS

        # ai2=self.ai2combo.currentText()
        # ai2time=self.ai2time.value()
        # ai2mcts = importlib.import_module(f"Variants.{ai2}").MCTS
        
        # self.worker = Worker([ai1mcts, ai1, ai1time], [ai2mcts, ai2, ai2time], self.nogames.value())
        # #self.worker.finished.connect(self.on_worker_finished)
        
        # self.thread = QtCore.QThread()
        # self.worker.moveToThread(self.thread)
        # self.worker.update_signal.connect(self.othello_board.redraw)
        # self.thread.started.connect(self.worker.run)
        # self.thread.start()
        #self.Run([ai1mcts,ai1,ai1time],[ai2mcts,ai2,ai2time],self.nogames.value())

    def updateTree(self,root):
        print(len(root.children))
        self.Tree.show_tree(root)
    def refreshBoard(self,ishuman=False):
        if ishuman:
            self.othello_board.redraw(self.game,True ,self.moveselected.emit)

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


    def Run(self,ai1,ai2,times):
        
        for tt in range(times):
            self.game.reset_board()
            self.refreshBoard()

            
            
            while self.game.validMoves():
                if self.game.currentPlayer==1:
                    print(f"{ai1[1]}{self.game.currentPlayer} is thinking")
                    move = ai1[0](self.game,self.game.currentPlayer,ai1[2])
                    self.game.make_move(move[0])
                    #draw_board(game)
                    self.refreshBoard()

                    
                elif self.game.validMoves():
                    print(f"{ai2[1]}{self.game.currentPlayer} is thinking")
                    move = ai2[0](self.game,self.game.currentPlayer,ai2[2])
                    self.game.make_move(move[0])
                    #draw_board(game)
                    self.refreshBoard()
                    
            
            result = self.game.get_result()
            if not os.path.isfile(f"{ai1[1]}_{ai1[2]} vs {ai2[1]}_{ai2[2]}.txt"):
                with open(f"{ai1[1]}_{ai1[2]} vs {ai2[1]}_{ai2[2]}.txt" , "w") as f:
                    f.write("") 
            if result == 0:
                
                print("Draw")
                with open(f"{ai1[1]}_{ai1[2]} vs {ai2[1]}_{ai2[2]}.txt" , "a") as f:
                    f.write("0\n")
                tie +=1
            elif result == 1:
                print("AI 1 wins")
                win1 +=1
                with open(f"{ai1[1]}_{ai1[2]} vs {ai2[1]}_{ai2[2]}.txt" , "a") as f:
                    f.write("-1\n")
            else:
                win2 +=1
                with open(f"{ai1[1]}_{ai1[2]} vs {ai2[1]}_{ai2[2]}.txt" , "a") as f:
                    f.write("1\n")
        #screen.fill("gray")   
        
        #draw_board(game)
        self.refreshBoard()
                    
        
        print(f"AI 1 : {win1} , AI 2 : {win2} , DRAW : {tie}")



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

        for i in range(a[2]):
            game=Game([])
            game.reset_board()
            while game.validMoves():
                if game.currentPlayer==1:
                    print(ai1[0], "thinking")
                    move=ai1[1](game, game.currentPlayer, ai1[2],mode=ai1[3])
                    game.make_move(move[0])
                elif game.currentPlayer==2:
                    print(ai2[0], "thinking")
                    move=ai2[1](game, game.currentPlayer, ai2[2],mode=ai2[3])
                    game.make_move(move[0])
            result = game.get_result()
            if not os.path.isfile(f"{ai1[0]}_{ai1[2]} vs {ai2[0]}_{ai2[2]}.txt"):
                with open(f"{ai1[0]}_{ai1[2]} vs {ai2[0]}_{ai2[2]}.txt" , "w") as f:
                    f.write("") 
            if result==1:
                player1+=1
                print(ai1[0],"Wins")
                with open(f"{ai1[0]}_{ai1[2]} vs {ai2[0]}_{ai2[2]}.txt" , "a") as f:
                    f.write("1\n")
            elif result==-1:
                player2+=1
                print(ai2[0],"Wins")
                with open(f"{ai1[0]}_{ai1[2]} vs {ai2[0]}_{ai2[2]}.txt" , "a") as f:
                    f.write("2\n")

            else:
                tie+=1
                print("Tie")
                with open(f"{ai1[0]}_{ai1[2]} vs {ai2[0]}_{ai2[2]}.txt" , "a") as f:
                    f.write("0\n")

        print(f"Player 1 : {player1}  ,  player 2 : {player2}   ,  Tie : {tie}")