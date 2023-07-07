#!/usr/bin/python3
import random


class Shape:
    shapeNone = 0
    shapeI = 1
    shapeL = 2
    shapeJ = 3
    shapeT = 4
    shapeO = 5
    shapeS = 6
    shapeZ = 7

    shapeCoord = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),     # None
        ((0, -1), (0, 0), (0, 1), (0, 2)),    # I
        ((0, -1), (0, 0), (0, 1), (1, 1)),    # L
        ((0, -1), (0, 0), (0, 1), (-1, 1)),   # J
        ((0, -1), (0, 0), (0, 1), (1, 0)),    # T
        ((0, 0), (0, -1), (1, 0), (1, -1)),   # O
        ((0, 0), (0, -1), (-1, 0), (1, -1)),  # S
        ((0, 0), (0, -1), (1, 0), (-1, -1))   # Z
    )

    def __init__(self, shape=0):
        self.shape = shape

    def getRotatedOffsets(self, direction):
        tmp_coords = Shape.shapeCoord[self.shape]
        if direction == 0 or self.shape == Shape.shapeO:
            return ((x, y) for x, y in tmp_coords)

        if direction == 1:
            return ((-y, x) for x, y in tmp_coords)

        if direction == 2:
            if self.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
                return ((x, y) for x, y in tmp_coords)
            else:
                return ((-x, -y) for x, y in tmp_coords)

        if direction == 3:
            if self.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
                return ((-y, x) for x, y in tmp_coords)
            else:
                return ((y, -x) for x, y in tmp_coords)

    def getCoords(self, direction, x, y):
        return ((x + xx, y + yy) for xx, yy in self.getRotatedOffsets(direction))

    def getBoundingOffsets(self, direction):
        tmp_coords = self.getRotatedOffsets(direction)
        min_x, max_x, min_y, max_y = 0, 0, 0, 0
        for x, y in tmp_coords:
            if min_x > x:
                min_x = x
            if max_x < x:
                max_x = x
            if min_y > y:
                min_y = y
            if max_y < y:
                max_y = y
        return min_x, max_x, min_y, max_y


class BoardData:
    width = 10
    height = 22

    def __init__(self):
        self.backBoard = [0] * BoardData.width * BoardData.height

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()
        self.nextShape = Shape(random.randint(1, 7))
        self.score = 0
        self.shapeStat = [0] * 8

    def getData(self):
        return self.backBoard[:]

    def getValue(self, x, y):
        return self.backBoard[x + y * BoardData.width]

    def getCurrentShapeCoord(self):
        return self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY)

    def createNewPiece(self):
        min_x, max_x, min_y, max_y = self.nextShape.getBoundingOffsets(0)
        result = False
        if self.tryMoveCurrent(0, 5, -min_y):
            self.currentX = 5
            self.currentY = -min_y
            self.currentDirection = 0
            self.currentShape = self.nextShape
            self.nextShape = Shape(random.randint(1, 7))
            result = True
        else:
            self.currentShape = Shape()
            self.currentX = -1
            self.currentY = -1
            self.currentDirection = 0
        self.shapeStat[self.currentShape.shape] += 1
        return result

    def tryMoveCurrent(self, direction, x, y):
        return self.tryMove(self.currentShape, direction, x, y)

    def tryMove(self, shape, direction, x, y):
        for x, y in shape.getCoords(direction, x, y):
            if x >= BoardData.width or x < 0 or y >= BoardData.height or y < 0:
                return False
            if self.backBoard[x + y * BoardData.width] > 0:
                return False
        return True

    def moveDown(self):
        lines = 0
        if self.tryMoveCurrent(self.currentDirection, self.currentX, self.currentY + 1):
            self.currentY += 1
        else:
            self.mergePiece()
            lines = self.removeFullLines()
            self.createNewPiece()
            self.score += lines  # Update the score
        return lines

    def dropDown(self):
        while self.tryMoveCurrent(self.currentDirection, self.currentX, self.currentY + 1):
            self.currentY += 1
        self.mergePiece()
        lines = self.removeFullLines()
        self.createNewPiece()
        return lines

    def moveLeft(self):
        if self.tryMoveCurrent(self.currentDirection, self.currentX - 1, self.currentY):
            self.currentX -= 1

    def moveRight(self):
        if self.tryMoveCurrent(self.currentDirection, self.currentX + 1, self.currentY):
            self.currentX += 1

    def rotateRight(self):
        if self.tryMoveCurrent((self.currentDirection + 1) % 4, self.currentX, self.currentY):
            self.currentDirection += 1
            self.currentDirection %= 4

    def rotateLeft(self):
        if self.tryMoveCurrent((self.currentDirection - 1) % 4, self.currentX, self.currentY):
            self.currentDirection -= 1
            self.currentDirection %= 4

    def removeFullLines(self):
        new_back_board = [0] * BoardData.width * BoardData.height
        new_y = BoardData.height - 1
        lines = 0
        for y in range(BoardData.height - 1, -1, -1):
            blockCount = sum([1 if self.backBoard[x + y * BoardData.width] > 0 else 0 for x in range(BoardData.width)])
            if blockCount < BoardData.width:
                for x in range(BoardData.width):
                    new_back_board[x + new_y * BoardData.width] = self.backBoard[x + y * BoardData.width]
                new_y -= 1
            else:
                lines += 1
        if lines > 0:
            self.backBoard = new_back_board
            self.score += lines  # Cập nhật điểm số
        return lines

    def mergePiece(self):
        for x, y in self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY):
            self.backBoard[x + y * BoardData.width] = self.currentShape.shape

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()

    def clear(self):
        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()
        self.backBoard = [0] * BoardData.width * BoardData.height


BOARD_DATA = BoardData()
