import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem, QVBoxLayout, QWidget, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, QRectF
from PyQt5 import QtGui

class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(GraphicsView, self).__init__(scene, parent)
        
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor

        self.scale(factor, factor)


class CustomScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(CustomScene, self).__init__(parent)
        self.setSceneRect(QRectF(-1000, -1000, 2000, 2000))  # Adjust as needed

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super(CustomScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            super(CustomScene, self).mouseReleaseEvent(event)


def main():
    app = QApplication(sys.argv)

    scene = CustomScene()
    view = GraphicsView(scene)

    # Add some items to the scene for demonstration
    ellipse_item = QGraphicsEllipseItem(-50, -50, 100, 100)
    rect_item = QGraphicsRectItem(-75, -75, 150, 150)

    scene.addItem(ellipse_item)
    scene.addItem(rect_item)

    # Set up the main window
    main_window = QWidget()
    layout = QVBoxLayout(main_window)
    layout.addWidget(view)

    main_window.setLayout(layout)
    main_window.setGeometry(100, 100, 800, 600)
    main_window.setWindowTitle('PyQt5 GraphicsView with Infinite Pan and Zoom')
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
