#!/usr/bin/env python3


"""
TODO:

IA
    visited:
        take into account the direction
    arrow:
        can_change: use the cell's attribute locked/tmp

"""

import datetime
import sys

#
# Constants
#

GRID_SIZE_X = 19
GRID_SIZE_Y = 10

CELL_PLATFORM = '.'
CELL_VOID = '#'

#
# Output
#

_real_print = print
def print(*args):
    out_debug('Please dont use print().')
    raise Exception('Please dont use print().')

def out_print(*args):
    _real_print(*args)

def out_debug(*args):
    _real_print(*args, file=sys.stderr)

#
# Cell
#

CELL_INITIAL = 'CELL_INITIAL'
CELL_LOCKED = 'CELL_LOCKED'
CELL_TMP = 'CELL_TMP'

def cell_c2p(c):
    return {
        'L': Pos(x=-1, y=0),
        'R': Pos(x=1, y=0),
        'U': Pos(x=0, y=-1),
        'D': Pos(x=0, y=1),
    }[c.upper()]

def cell_p2c(p):
    return {  # x, y
        (-1, 0): 'L',
        (1, 0): 'R',
        (0, -1): 'U',
        (0, 1): 'D',
    }[(p.x, p.y)]

class Cell(object):
    def __init__(self, c):
        self.c = c
        self.state = CELL_INITIAL
        self.visited = False

    def can_change(self):
        return self.c == CELL_PLATFORM or self.state != CELL_INITIAL

    def set(self, delta):
        if not self.can_change():
            raise Exception('Error, cant change this cell')

        self.c = cell_p2c(delta)
        self.state = CELL_TMP

    def reverse(self):
        return {
            'R': 'L',
            'L': 'R',
            'U': 'D',
            'D': 'U',
        }[self.c]

class Pos(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Pos(
            x = self.x + other.x,
            y = self.y + other.y,
        )

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __str__(self):
        return 'Pos(x=%2d, y=%2d)' % (self.x, self.y)

    def is_in_grid(self):
        return self.x >= 0 and self.x < GRID_SIZE_X and self.y >= 0 and self.y < GRID_SIZE_Y

#
# Game
#

def game_parse():
    grid = [[Cell(c) for c in input()] for _ in range(10)]

    robot_count = int(input())
    robots = []
    for _ in range(robot_count):
        x, y, d = input().split()
        x = int(x)
        y = int(y)
        robots.append((x, y, d))

    return grid, robot_count, robots

#
# Grid
#

class Grid(object):
    def __init__(self, grid):
        self.grid = grid

    def reset_visited(self):
        for line in self.grid:
            for c in line:
                c.visited = False

    def backtrack(self, cur_pos, cur_points=1):
        self.get_cell(cur_pos.x, cur_pos.y).visited = True

        # if not playable, follow direction
        if not self.can_set_cell(cur_pos):
            new_pos = cur_pos + cell_c2p(self.get_cell(cur_pos.x, cur_pos.y).c)
            if self.should_bactrack(new_pos):
                return self.backtrack(new_pos, cur_points+1)
            else:
                return cur_points

        # now we can actually bactrack

        deltas = (
            Pos(x=-1, y=0),
            Pos(x=1, y=0),
            Pos(x=0, y=-1),
            Pos(x=0, y=1),
        )

        best_score = cur_points
        best_delta = None

        # try all options, saving the best one
        for delta in deltas:
            new_pos = cur_pos + delta
            if self.should_bactrack(new_pos):
                # try backtrack
                self.set_cell(cur_pos, delta)
                out_debug('backtrack try %s -> %s (d=%s)' % (cur_pos, new_pos, cell_p2c(delta)))
                new_score = self.backtrack(new_pos, cur_points+1)
                if new_score > best_score:
                    best_score = new_score
                    best_delta = delta
                # reset
                self.grid[cur_pos.y][cur_pos.x].c = CELL_PLATFORM

        # set the direction to the best option found
        if best_score > cur_points:
            self.set_cell(cur_pos, best_delta)

        return best_score

    def should_bactrack(self, pos):
        if not pos.is_in_grid():
            return False

        cur_cell = self.get_cell(pos.x, pos.y)

        if cur_cell.c == CELL_VOID or cur_cell.visited:
            return False

        return True

    def can_set_cell(self, pos):
        return self.grid[pos.y][pos.x].can_change()

    def set_cell(self, pos, delta):
        self.grid[pos.y][pos.x].set(delta)

    def get_cell(self, x, y):
        return self.grid[y][x]

    def __str__(self):
        ret = ''
        for y, line in enumerate(self.grid):
            ret += '\n'
            for x, _cell in enumerate(line):
                ret += self.get_cell(x, y).c

        return ret[1:]

    def print_arrows(self, pos):
        self.reset_visited()

        last_cell = self.get_cell(pos.x, pos.y)
        ret = '%d %d %c' % (pos.x, pos.y, last_cell.c)

        while True:
            if not pos.is_in_grid():
                break

            cell = self.get_cell(pos.x, pos.y)
            if cell.c == CELL_PLATFORM or cell.c == CELL_VOID or cell.visited:  # not a direction, did we reached the end of the path?
                break

            cell.visited = True

            if cell.c != last_cell.c:
                ret += ' %d %d %c' % (pos.x, pos.y, cell.c)

            pos += cell_c2p(cell.c)
            last_cell = cell

        ret += ' %d %d %c' % (pos.x, pos.y, last_cell.reverse())

        return ret

#
# Main
#

def main():
    out_debug('Hello, world!')

    grid, _, robots = game_parse()
    g = Grid(grid)
    robots_pos = [Pos(x=robot[0], y=robot[1]) for robot in robots]

    start = datetime.datetime.now()

    out_debug('== Grid ==')
    out_debug(g)
    out_debug('== Robots ==')
    for r in robots:
        out_debug(r)
    out_debug('')

    total_points = 0
    for pos in robots_pos:
        out_debug('== Backtracking robot %s' % str(pos))
        g.reset_visited()
        total_points += g.backtrack(pos)
        out_debug(g)

    out_debug()
    out_debug('== Grid ==')
    out_debug(g)
    out_debug('points: %d' % total_points)

    arrows = [g.print_arrows(pos) for pos in robots_pos]
    out_print(' '.join(arrows))

    out_debug('Time2: %d ms' % ((datetime.datetime.now()-start).total_seconds()*1000))
    out_debug()


main()
