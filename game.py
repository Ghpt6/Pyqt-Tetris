import typing
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QBasicTimer


class Piece:
    color = [
        QColor(0, 0, 0, 0),  # transparent
        QColor(255, 0, 0),  # red
    ]
    No_Shape = 0
    T_Shape = 1

    def __init__(self, x, y, board):
        self.x = x
        self.y = y
        self.board = board
 
    def new_piece(self):
        self.board.cur = TPiece(2, -2, self.board)

    def change_piece(self, newX, newY):
        pass

    # direction: true->clockwise, false->counterclockwise
    def rotate(self, direction: bool):
        for pos in self.coord:
            x = self.x + pos[0]
            y = self.y + pos[1]
            self.board.set_Shape_At(x, y, Piece.No_Shape)

        if direction:
            for pos in self.coord:
                x = pos[0]
                pos[0] = pos[1]
                pos[1] = -x
        else:
            for pos in self.coord:
                y = pos[1]
                pos[1] = pos[0]
                pos[0] = -y

        for pos in self.coord:
            x = self.x + pos[0]
            y = self.y + pos[1]
            self.board.set_Shape_At(x, y, self.shape)
            
        self.board.flush_board()

    def move(self, relative):
        for pos in self.coord:
            x = self.x + pos[0]
            y = self.y + pos[1]
            self.board.set_Shape_At(x, y, Piece.No_Shape)

        self.x = self.x + relative[0]
        self.y = self.y + relative[1]

        for pos in self.coord:
            x = self.x + pos[0]
            y = self.y + pos[1]
            self.board.set_Shape_At(x, y, self.shape)

        self.board.flush_board()

    def drop_one_line(self):
        self.move([0, 1])
        if self.hit_the_bottom():
            self.new_piece()

    def move_right_one_line(self):
        self.move([1, 0])

    def move_left_one_line(self):
        self.move([-1, 0])

    def rotate_right(self):
        self.rotate(True)

    def rotate_left(self):
        self.rotate(False)

    def get_color(shape):
        return Piece.color[shape]


class NoPiece(Piece):
    def __init__(self):
        self.coord = []


class TPiece(Piece):
    def __init__(self, x, y, board):
        super().__init__(x, y, board)

        self.shape = Piece.T_Shape
        self.coord = [[-1, 0], [0, 0], [1, 0], [0, 1]]

    def hit_the_bottom(self) -> bool:
        return self.y >= (self.board.height - 1)


class Board:
    def __init__(self, width, height, squareLen, squareWid, painter):
        self._board = []

        self.width = width
        self.height = height
        self.squareLen = squareLen
        self.squareWid = squareWid

        self.painter = painter
        self.cur = TPiece(2, -2, self)
        self.init_board()

    def init_board(self):
        self.clear_board()

    # triggered by timeEvent per interval msec
    # def one_line_down(self):
    #     self.cur.drop_one_line()

    def clear_board(self):
        for i in range(self.width * self.height):
            self._board.append(Piece.No_Shape)
        self.flush_board()

    def flush_board(self):
        self.painter()

    def set_Shape_At(self, x, y, shape):
        if self.out_of_bounds(x, y):
            return
        self._board[self.xy2i(x, y)] = shape

    def out_of_bounds(self, x, y) -> bool:
        return (x < 0) or (y < 0) or (x >= self.width) or (y >= self.height)

    def xy2i(self, x, y):
        return y * self.width + x


class Game(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tetris")
        self.setGeometry(0, 0, 700, 1000)

        self.board = Board(10, 19, 50, 50, self.update)
        self.timer = QBasicTimer()

        self.show()

    def start(self):
        interval = 250
        self.timer.start(interval, self)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Right:
            self.board.cur.move_right_one_line()
        elif event.key() == Qt.Key_Left:
            self.board.cur.move_left_one_line()
        elif event.key() == Qt.Key_Up:
            self.board.cur.rotate_left()
        elif event.key() == Qt.Key_Down:
            self.board.cur.rotate_right()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.board.cur.drop_one_line()

    def paintEvent(self, e) -> None:
        qp = QPainter()
        qp.begin(self)

        for i in range(self.board.width * self.board.height):
            x = i % self.board.width
            y = int(i / self.board.width)

            color = Piece.get_color(self.board._board[i])

            qp.setBrush(QBrush(color, Qt.SolidPattern))
            qp.drawRect(
                x * self.board.squareWid,
                y * self.board.squareLen,
                self.board.squareWid,
                self.board.squareLen,
            )

        qp.end()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    game = Game()
    game.start()
    sys.exit(app.exec_())
