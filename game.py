from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QBasicTimer
from copy import deepcopy
from random import randint


class Piece:
    color = [
        None,
        QColor(0, 0, 0, 50),
        QColor(0, 0, 0, 0),  # transparent
        QColor(255, 0, 0),  # red
        QColor(0, 255, 0),
        QColor(0, 0, 255),
        QColor(255, 255, 0),
        QColor(255, 0, 255),
        QColor(0, 255, 255),
    ]
    Error_Shape = 0
    Shadow_Shape = 1
    No_Shape = 2
    T_Shape = 3
    S1_Shape = 4
    S2_Shape = 5
    I_Shape = 6

    def __init__(self, board):
        # self.x = x
        # self.y = y
        self.board = board

    def reset(self):
        self.x = int(self.board.width / 2)
        self.y = -2

        # random direction...
        for i in range(randint(0, 3)):
            for pos in self.coord:
                x = pos[0]
                pos[0] = pos[1]
                pos[1] = -x

        self.shadow.x = self.x
        self.shadow.y = self.y
        self.shadow.coord = self.coord

    def new_piece(self):
        self.board.next_piece()

    def reach_the_top(self) -> bool:
        for pos in self.coord:
            y = self.y + pos[1]
            if y < 0:
                return True
        return False

    def collision(self, newX, newY, newCoord=None) -> bool:
        if newCoord is None:
            newCoord = self.coord
        for pos in newCoord:
            x = newX + pos[0]
            y = newY + pos[1]
            cur_shape = self.board.get_Shape_At(x, y)
            if cur_shape != Piece.No_Shape and cur_shape != Piece.Shadow_Shape:
                return True
        return False

    # return success(true) or fail(false)
    def change_piece(self, newX, newY, newCoord=None) -> bool:
        for pos in self.coord:
            x = self.x + pos[0]
            y = self.y + pos[1]
            self.board.set_Shape_At(x, y, Piece.No_Shape)

        if self.collision(newX, newY, newCoord):
            for pos in self.coord:
                x = self.x + pos[0]
                y = self.y + pos[1]
                self.board.set_Shape_At(x, y, self.shape)
            return False

        self.x = newX
        self.y = newY

        if newCoord is None:
            newCoord = self.coord
        else:
            self.coord = newCoord

        self.draw_shadow()

        for pos in newCoord:
            x = self.x + pos[0]
            y = self.y + pos[1]
            self.board.set_Shape_At(x, y, self.shape)

        self.board.flush_board()
        return True

    # direction: true->clockwise, false->counterclockwise
    def rotate(self, direction: bool):
        coord = deepcopy(self.coord)

        if direction:
            for pos in coord:
                x = pos[0]
                pos[0] = pos[1]
                pos[1] = -x
        else:
            for pos in coord:
                y = pos[1]
                pos[1] = pos[0]
                pos[0] = -y

        self.change_piece(self.x, self.y, coord)

    def move(self, relative) -> bool:
        return self.change_piece(self.x + relative[0], self.y + relative[1])

    # if false, then piece has reached the top, game over!
    def drop_one_line(self) -> bool:
        if not self.move([0, 1]):
            if self.reach_the_top():
                return False
            self.board.try_clear_line()
            self.new_piece()
        return True

    def move_right_one_line(self):
        self.move([1, 0])

    def move_left_one_line(self):
        self.move([-1, 0])

    def rotate_right(self):
        self.rotate(True)

    def rotate_left(self):
        self.rotate(False)

    def move_to_shadow(self):
        self.change_piece(self.shadow.x, self.shadow.y)
        self.board.try_clear_line()

    def draw_shadow(self):
        # clear it first
        self.shadow.shape = Piece.No_Shape
        self.draw_piece(self.shadow)

        # then draw again
        self.update_shadow()
        y = self.y
        while not self.collision(self.x, y + 1):
            y = y + 1

        self.shadow.shape = Piece.Shadow_Shape
        self.shadow.y = y
        self.draw_piece(self.shadow)

    def draw_piece(self, piece):
        self.__draw_piece(piece.x, piece.y, piece.coord, piece.shape)

    def __draw_piece(self, x, y, coord, shape):
        for pos in coord:
            _x = x + pos[0]
            _y = y + pos[1]
            self.board.set_Shape_At(_x, _y, shape)

    def update_shadow(self):
        self.shadow.x = self.x
        self.shadow.y = self.y
        self.shadow.coord = self.coord

    def get_color(shape):
        return Piece.color[shape]


class NoPiece(Piece):
    def __init__(self):
        self.coord = []


class TPiece(Piece):
    def __init__(self, board):
        super().__init__(board)

        self.shape = Piece.T_Shape
        self.coord = [[-1, 0], [0, 0], [1, 0], [0, 1]]

        self.shadow = deepcopy(self)
        self.shadow.shape = Piece.Shadow_Shape


class S1Piece(Piece):
    def __init__(self, board):
        super().__init__(board)

        self.shape = Piece.S1_Shape
        self.coord = [[-1, -1], [-1, 0], [0, 0], [0, 1]]

        self.shadow = deepcopy(self)
        self.shadow.shape = Piece.Shadow_Shape


class S2Piece(Piece):
    def __init__(self, board):
        super().__init__(board)

        self.shape = Piece.S2_Shape
        self.coord = [[1, -1], [1, 0], [0, 0], [0, 1]]

        self.shadow = deepcopy(self)
        self.shadow.shape = Piece.Shadow_Shape


class IPiece(Piece):
    def __init__(self, board):
        super().__init__(board)

        self.shape = Piece.I_Shape
        self.coord = [[0, -1], [0, 0], [0, 1], [0, 2]]

        self.shadow = deepcopy(self)
        self.shadow.shape = Piece.Shadow_Shape


class Board:
    def __init__(self, width, height, squareLen, squareWid, painter):
        self._board = []
        self.lib = [
            TPiece(self),
            S1Piece(self),
            S2Piece(self),
            IPiece(self),
        ]

        self.width = width
        self.height = height
        self.squareLen = squareLen
        self.squareWid = squareWid

        self.painter = painter
        self.init_board()

    def init_board(self):
        self.clear_board()
        self.next_piece()

    def next_piece(self):
        idx = randint(0, len(self.lib) - 1)
        self.cur = self.lib[idx]
        self.cur.reset()

    def try_clear_line(self):
        for y in range(self.height):
            flag = False
            for x in range(self.width):
                if self.get_Shape_At(x, y, True) == Piece.No_Shape:
                    break
                if x == self.width - 1:
                    flag = True
            if flag:
                self.clear_one_line(y)

    def clear_one_line(self, line):
        for y in range(line, 0, -1):
            for x in range(self.width):
                shapeAbove = self.get_Shape_At(x, y - 1, True)
                self.set_Shape_At(x, y, shapeAbove, True)
        self.flush_board()

    def clear_board(self):
        for i in range(self.width * self.height):
            self._board.append(Piece.No_Shape)
        self.flush_board()

    def flush_board(self):
        self.painter()

    def set_Shape_At(self, x, y, shape, isSafe: bool = False):
        if isSafe:
            self._board[self.xy2i(x, y)] = shape
            return
        if self.out_of_bounds(x, y):
            return
        self._board[self.xy2i(x, y)] = shape

    def get_Shape_At(self, x, y, isSafe: bool = False):
        if isSafe:
            return self._board[self.xy2i(x, y)]
        if (x < 0) or (x >= self.width) or (y >= self.height):
            return Piece.Error_Shape  # out of border
        elif y < 0:  # it's ok that out of top
            return Piece.No_Shape
        return self._board[self.xy2i(x, y)]

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
        interval = 600
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
        elif event.key() == Qt.Key_Space:
            self.board.cur.move_to_shadow()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if not self.board.cur.drop_one_line():
                self.timer.stop()
                QMessageBox.information(self, "Game Over", "You lose.", QMessageBox.Yes)

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
