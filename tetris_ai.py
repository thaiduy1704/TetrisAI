#!/usr/bin/python3
from tetris_model import BOARD_DATA, Shape
from datetime import datetime
import numpy as np


def calcNextDropDist(data, d0, xRange):
    res = {}
    for x0 in xRange:
        if x0 not in res:
            res[x0] = BOARD_DATA.height - 1
        for x, y in BOARD_DATA.nextShape.getCoords(d0, x0, 0):
            yy = 0
            while yy + y < BOARD_DATA.height and (yy + y < 0 or data[(y + yy), x] == Shape.shapeNone):
                yy += 1
            yy -= 1
            if yy < res[x0]:
                res[x0] = yy
    return res


def dropDownByDist(data, shape, direction, x0, dist):
    for x, y in shape.getCoords(direction, x0, 0):
        data[y + dist, x] = shape.shape


def calculateScore(step1Board, d1, x1, dropDist):
    t1 = datetime.now()
    width = BOARD_DATA.width
    height = BOARD_DATA.height

    dropDownByDist(step1Board, BOARD_DATA.nextShape, d1, x1, dropDist[x1])

    complete_lines = 0
    block_columns = [0] * width
    holeCandidates = [0] * width
    holeConfirm = [0] * width
    holes, blocks = 0, 0
    for y in range(height - 1, -1, -1):
        is_hole = False
        is_block = False
        for x in range(width):
            if step1Board[y, x] == Shape.shapeNone:
                is_hole = True
                holeCandidates[x] += 1
            else:
                is_block = True
                block_columns[x] = height - y
                if holeCandidates[x] > 0:
                    holeConfirm[x] += holeCandidates[x]
                    holeCandidates[x] = 0
                if holeConfirm[x] > 0:
                    blocks += 1
        if not is_block:
            break
        if not is_hole and is_block:
            complete_lines += 1
    holes = sum([x ** .7 for x in holeConfirm])
    max_height = max(block_columns) - complete_lines

    height_different_between_col = [block_columns[i] - block_columns[i + 1] for i in range(len(block_columns) - 1)]
    aggregate_height = sum([abs(x) for x in height_different_between_col]) / 10
    # aggregate_height = sum([abs(x) for x in block_columns]) / 10
    # print(datetime.now() - t1)
    score = complete_lines * 0.760666 - 0.35663 * holes - 0.510066 * aggregate_height - 0.184483 * max_height
    return score

def dropDown(data, shape, direction, x0):
    dy = BOARD_DATA.height - 1
    for x, y in shape.getCoords(direction, x0, 0):
        yy = 0
        while yy + y < BOARD_DATA.height and (yy + y < 0 or data[(y + yy), x] == Shape.shapeNone):
            yy += 1
        yy -= 1
        if yy < dy:
            dy = yy
    # print("dropDown: shape {0}, direction {1}, x0 {2}, dy {3}".format(shape.shape, direction, x0, dy))
    dropDownByDist(data, shape, direction, x0, dy)


def calcStep1Board(d0, x0):
    board = np.array(BOARD_DATA.getData()).reshape((BOARD_DATA.height, BOARD_DATA.width))
    dropDown(board, BOARD_DATA.currentShape, d0, x0)
    return board


def nextMove(TETRIS_AI):
    if BOARD_DATA.currentShape == Shape.shapeNone or not TETRIS_AI:
        return None

    _, _, min_y, _ = BOARD_DATA.nextShape.getBoundingOffsets(0)

    strategy = None
    if BOARD_DATA.currentShape.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
        current_direction_range = (0, 1)
    elif BOARD_DATA.currentShape.shape == Shape.shapeO:
        current_direction_range = (0,)
    else:
        current_direction_range = (0, 1, 2, 3)

    if BOARD_DATA.nextShape.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
        next_direction_range = (0, 1)
    elif BOARD_DATA.nextShape.shape == Shape.shapeO:
        next_direction_range = (0,)
    else:
        next_direction_range = (0, 1, 2, 3)

    for d0 in current_direction_range:
        min_x, max_x, _, _ = BOARD_DATA.currentShape.getBoundingOffsets(d0)
        for x0 in range(-min_x, BOARD_DATA.width - max_x):
            board = calcStep1Board(d0, x0)
            for d1 in next_direction_range:
                min_x, max_x, _, _ = BOARD_DATA.nextShape.getBoundingOffsets(d1)
                dropDist = calcNextDropDist(board, d1, range(-min_x, BOARD_DATA.width - max_x))
                for x1 in range(-min_x, BOARD_DATA.width - max_x):
                    score = calculateScore(np.copy(board), d1, x1, dropDist)
                    if not strategy or strategy[2] < score:
                        strategy = (d0, x0, score)
    return strategy

# -0.510066 , 0.760666 , -0.35663 , -0.184483

