from PyQt5 import QtWidgets, uic,QtGui,QtCore
import sys
import os
import importlib
from game import Game

class TreePlotter(QtWidgets.QGraphicsView):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.root = root

    def draw_tree(self, node, x, y):
        node.draw_node()
        y += self.NODE_HEIGHT + self.Y_OFFSET
        for child in node.children:
            if child.visits != 0:
                child.draw_node()
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

    def show_tree(self):
        self.scene.clear()
        x = self.X
        y = self.Y
        self.draw_tree(self.root, x, y)


class OthelloBoard(QtWidgets.QGraphicsView):
    def __init__(self):
        super(OthelloBoard, self).__init__()
        self.cell_size = 50
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.board_size = 8
        self.setFixedSize(self.cell_size*9,self.cell_size*9)
        self.showMoves=False

      
    def redraw(self,board):
        if self.showMoves:
            possible_moves=Game(board).validMoves()
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
                if self.showMoves:
                    if (j,i) in possible_moves:
                        self.add_piece(i, j, "green")

                if v!=0:
                    self.add_piece(i, j, "black" if v==1 else "white")
                

    def add_piece(self, row, col, color):
        self.cell_size = 50
        x, y = col * self.cell_size+5, row * self.cell_size+5
        ellipse_item = QtWidgets.QGraphicsEllipseItem(x, y, 40, 40)
        ellipse_item.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        self.scene.addItem(ellipse_item)


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    update_signal = QtCore.pyqtSignal(list)

    def __init__(self, ai1, ai2, times):
        super().__init__()
        self.ai1 = ai1
        self.ai2 = ai2
        self.times = times
    
    
    def run(self):
        game = Game([])
        for tt in range(self.times):
            game.reset_board()
            #self.redraw(game.board)
            self.update_signal.emit(game.board)
            print("redrawn")
            while game.validMoves():
                if game.currentPlayer == 1:
                    move = self.ai1[0](game, game.currentPlayer, self.ai1[2])
                    game.make_move(move[0])
                    #self.redraw(game.board)
                    self.update_signal.emit(game.board)
                    print("redrawn")
                    
                    
                elif game.validMoves():
                    move = self.ai2[0](game, game.currentPlayer, self.ai2[2])
                    game.make_move(move[0])
                    #self.redraw(game.board)
                    self.update_signal.emit(game.board)
                    print("redrawn")

            result = game.get_result()
            QtWidgets.QApplication.postEvent(window, ResultEvent(result))

class ResultEvent(QtCore.QEvent):
    def __init__(self, result):
        super().__init__(QtCore.QEvent.User)
        self.result = result

class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main.ui', self)
        self.player1type.currentIndexChanged.connect(lambda index: self.player1typewindow.setCurrentIndex(index))
        self.player1mode.currentIndexChanged.connect(lambda index: self.player1modewindow.setCurrentIndex(index))
        
        self.player2type.currentIndexChanged.connect(lambda index: self.player2typewindow.setCurrentIndex(index))
        self.player2mode.currentIndexChanged.connect(lambda index: self.player2modewindow.setCurrentIndex(index))
        self.play.clicked.connect(self.onplay)
        
        self.label_13.setFixedSize(60,60)
        self.label_15.setFixedSize(60,60)
        self.blackp.setFixedSize(60,60)
        self.whitep.setFixedSize(60,60)
        self.whitep.hide()
        self.loadMCTS()

        self.showmoves.stateChanged.connect()
        QtWidgets.QCheckBox().stateChanged

        self.game = Game([])
        self.othello_board = OthelloBoard()

        self.othello_board.redraw(self.game.board)
        #self.show()
        self.showMaximized()

    def loadMCTS(self):
        all_variants=[x.replace(".py","") for x in os.listdir("Variants") if x.endswith(".py")]
        #for variant in all_variants:
        self.ai1combo.addItems(all_variants)
        self.ai2combo.addItems(all_variants)
    
   
   
    def onplay(self):
        self.stackedWidget.setCurrentIndex(1)
 
        self.board.addWidget(self.othello_board)
        #self.tree_plot.addWidget(self.treeplotter)
        ai1=self.ai1combo.currentText()
        ai1time=self.ai1time.value()
        ai1mcts = importlib.import_module(f"Variants.{ai1}").MCTS

        ai2=self.ai2combo.currentText()
        ai2time=self.ai2time.value()
        ai2mcts = importlib.import_module(f"Variants.{ai2}").MCTS
        
        self.worker = Worker([ai1mcts, ai1, ai1time], [ai2mcts, ai2, ai2time], self.nogames.value())
        #self.worker.finished.connect(self.on_worker_finished)
        
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.worker.update_signal.connect(self.othello_board.redraw)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        #self.Run([ai1mcts,ai1,ai1time],[ai2mcts,ai2,ai2time],self.nogames.value())
        
    def refreshBoard(self):
        self.othello_board.redraw(self.game.board)

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
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()