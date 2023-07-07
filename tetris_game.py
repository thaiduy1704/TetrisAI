
#!/usr/bin/python3
import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

from tetris_model import BOARD_DATA, Shape
from tetris_ai import nextMove

TETRIS_AI = False
class Tetris(QMainWindow):
    TETRIS_AI = True
    SPEED_NORMAL = 300
    SPEED_AI = 300
    def __init__(self):
        super().__init__()
        self.isStarted = False
        self.isPaused = False
        self.nextMove = None
        self.lastShape = Shape.shapeNone
        self.TETRIS_AI = False
        self.speed = Tetris.SPEED_NORMAL
        self.initUI()

    def initUI(self):
        self.gridSize = 30


        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

        hLayout = QHBoxLayout()
        self.tboard = Board(self, self.gridSize)
        hLayout.addWidget(self.tboard)

        self.sidePanel = SidePanel(self, self.gridSize)
        hLayout.addWidget(self.sidePanel)

        vLayout = QVBoxLayout()
        vLayout.addLayout(hLayout)

        hLayout = QHBoxLayout()
        hLayout.addStretch()  # Add a stretchable space to push the label to the right
        self.scoreLabel = QLabel("Score: 0", self)
        self.scoreLabel.setStyleSheet("font-weight: bold; font-size: 18px;")
        hLayout.addWidget(self.scoreLabel)
        vLayout.addLayout(hLayout)
        self.setLayout(vLayout)

        self.modeButton = QPushButton("Chế độ chơi: Người dùng", self)
        self.modeButton.setStyleSheet("font-weight: bold; font-size: 16px")
        vLayout.addWidget(self.modeButton)

        widget = QWidget(self)
        widget.setLayout(vLayout)
        self.setCentralWidget(widget)

        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.start()

        self.center()
        self.setWindowTitle('Tetris')
        self.show()

        self.setFixedSize(self.tboard.width() + self.sidePanel.width(),
                          self.sidePanel.height() + self.statusbar.height())

        self.updateScoreLabel()

        self.modeButton.clicked.connect(self.toggleMode)

    def updateScoreLabel(self):
        self.scoreLabel.setText("Score: " + str(self.tboard.score))



    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def start(self):
        if self.isPaused:
            return

        self.isStarted = True
        self.tboard.score = 0
        BOARD_DATA.clear()

        self.tboard.msg2Statusbar.emit(str(self.tboard.score + 79))

        BOARD_DATA.createNewPiece()
        self.timer.start(self.speed, self)

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.tboard.msg2Statusbar.emit("paused")
        else:
            self.timer.start(self.speed, self)

    def restartGame(self):
        self.isStarted = False
        self.isPaused = False
        self.nextMove = None
        self.lastShape = Shape.shapeNone
        self.initUI()
        self.start()
    def updateWindow(self):
        self.tboard.updateData()
        self.sidePanel.updateData()
        self.tboard.nextMove()
        self.update()

    def updateModeInfoLabel(self):
        if self.TETRIS_AI:
            self.statusbar.showMessage("Chế độ chơi: AI")
        else:
            self.statusbar.showMessage("Chế độ chơi: Người dùng")
    def toggleMode(self):
        Board.TETRIS_AI = not Board.TETRIS_AI
        if Board.TETRIS_AI:
            self.modeButton.setText("Chế độ chơi: Máy tự động")
        else:
            self.modeButton.setText("Chế độ chơi: Người dùng")


    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.TETRIS_AI and not self.nextMove:
                self.nextMove = nextMove(self.TETRIS_AI)

            if self.nextMove:
                k = 0
                while BOARD_DATA.currentDirection != self.nextMove[0] and k < 4:
                    BOARD_DATA.rotateRight()
                    k += 1
                k = 0
                while BOARD_DATA.currentX != self.nextMove[1] and k < 5:
                    if BOARD_DATA.currentX > self.nextMove[1]:
                        BOARD_DATA.moveLeft()
                    elif BOARD_DATA.currentX < self.nextMove[1]:
                        BOARD_DATA.moveRight()
                    k += 1

            lines = BOARD_DATA.moveDown()
            self.tboard.score += lines

            if self.lastShape != BOARD_DATA.currentShape:
                self.nextMove = None
                self.lastShape = BOARD_DATA.currentShape

            self.updateWindow()
            self.updateScoreLabel()
        else:
            super(Tetris, self).timerEvent(event)

    def keyPressEvent(self, event):
        if not self.isStarted or BOARD_DATA.currentShape == Shape.shapeNone:
            super(Tetris, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return
        elif key == Qt.Key_Left:
            BOARD_DATA.moveLeft()
        elif key == Qt.Key_Right:
            BOARD_DATA.moveRight()
        elif key == Qt.Key_Up:
            BOARD_DATA.rotateLeft()
        else:
            super(Tetris, self).keyPressEvent(event)

        self.updateWindow()


def drawSquare(painter, x, y, val, s):
    colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                  0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00, 0xECECEC]

    if val == 0:
        return

    color = QColor(colorTable[val])
    painter.fillRect(x + 1, y + 1, s - 2, s - 2, color)

    # painter.setPen(color.lighter())
    painter.setPen(color.darker())
    painter.drawLine(x, y + s - 1, x, y)
    painter.drawLine(x, y, x + s - 1, y)

    painter.setPen(color.darker())
    painter.drawLine(x + 1, y + s - 1, x + s - 1, y + s - 1)
    painter.drawLine(x + s - 1, y + s - 1, x + s - 1, y + 1)

class SidePanel(QFrame):
    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * 5, gridSize * BOARD_DATA.height)
        self.move(gridSize * BOARD_DATA.width, 0)
        self.gridSize = gridSize

    def updateData(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        min_x, max_x, min_y, max_y = BOARD_DATA.nextShape.getBoundingOffsets(0)

        dy = 3 * self.gridSize
        dx = (self.width() - (max_x - min_x) * self.gridSize) / 2

        val = BOARD_DATA.nextShape.shape
        for x, y in BOARD_DATA.nextShape.getCoords(0, 0, -min_y):
            drawSquare(painter, x * self.gridSize + dx, y * self.gridSize + dy, val, self.gridSize)


class Board(QFrame):
    msg2Statusbar = pyqtSignal(str)
    nextMoveSignal = pyqtSignal()
    TETRIS_AI = False

    @staticmethod
    def toggleMode():
        Board.TETRIS_AI = not Board.TETRIS_AI
    def __init__(self, parent, gridSize):
        super().__init__(parent)
        self.setFixedSize(gridSize * BOARD_DATA.width, gridSize * BOARD_DATA.height)
        self.gridSize = gridSize
        self.initBoard()

    def initBoard(self):
        self.score = 0
        self.toggleMode()
        BOARD_DATA.clear()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Init backboard
        for x in range(BOARD_DATA.width):
            for y in range(BOARD_DATA.height):
                drawSquare(painter, x * self.gridSize, y * self.gridSize, -1, self.gridSize)
        # Draw backboard
        for x in range(BOARD_DATA.width):
            for y in range(BOARD_DATA.height):
                val = BOARD_DATA.getValue(x, y)
                drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        # Draw current shape
            for x, y in BOARD_DATA.getCurrentShapeCoord():
                val = BOARD_DATA.currentShape.shape
                drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        # Draw a border
            painter.setPen(QColor(0x777777))
            painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
            painter.setPen(QColor(0xCCCCCC))
            painter.drawLine(self.width(), 0, self.width(), self.height())
        # Draw current shape
            if Board.TETRIS_AI:
                for x, y in BOARD_DATA.getCurrentShapeCoord():
                    val = BOARD_DATA.currentShape.shape
                    drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)


        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.end()

    def nextMove(self):
        if self.TETRIS_AI:
            return nextMove()
        return None

    def updateData(self):
        self.msg2Statusbar.emit(str(self.score))
        self.update()


if __name__ == '__main__':
    app = QApplication([])
    run = Tetris()
    sys.exit(app.exec_())
