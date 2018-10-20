#!/usr/bin/env python3


"""
TODO:

IA
    remplacer les classes Cell par Dir, et remplacer les Pos([-1; 1]) par Dir
        state : default, locked, temp

    faire en plusieurs passes:
        lire la grid et fixer les directions
        pour chaque robot
            backtrack + ajouter direction inverse sur la derniere case
            fixer les directions

    checker le backtracking

TEST
    script pour tester toutes les grids ?


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
# Game
#

class Cell(str):
    pass

class Pos(object):
    def __init__(self, **kwargs):
        self.x = kwargs.get('x', None)
        self.y = kwargs.get('y', None)

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

    def is_valid(self):
        return self.x >= 0 and self.x < GRID_SIZE_X and self.y >= 0 and self.y < GRID_SIZE_Y

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
# Grid backtrack
#

class Grid(object):
    def __init__(self, grid):
        self.grid = grid

    def backtrack(self, cur_pos, coming_from=None, cur_points=1):
        deltas = (
            Pos(x=-1, y=0),
            Pos(x=1, y=0),
            Pos(x=0, y=-1),
            Pos(x=0, y=1),
        )

        best_score = cur_points
        best_delta = None

        for delta in deltas:
            new_pos = cur_pos + delta
            if self.is_free_cell_platform(new_pos):
                self.set_arrow(cur_pos, delta)
                out_debug('backtrack try %s -> %s (d=%s)' % (cur_pos, new_pos, self.get_arrow(cur_pos)))
                new_score = self.backtrack(new_pos, delta, cur_points+1)
                if new_score > best_score:
                    best_score = new_score
                    best_delta = delta

        if best_delta is not None:
            self.set_arrow(cur_pos, best_delta)
        return best_score

    def is_free_cell_platform(self, pos):
        return pos.is_valid() and self.grid[pos.y][pos.x] == CELL_PLATFORM

    def set_arrow(self, pos, delta):
        self.grid[pos.y][pos.x] = delta

    def get_arrow(self, pos):
        cell = self.grid[pos.y][pos.x]
        if cell in ['#', '.', 'R', 'D', 'L', 'U', 'r', 'd', 'l', 'u']:
            return cell
        d = {  # x, y
            (-1, 0): 'L',
            (1, 0): 'R',
            (0, -1): 'U',
            (0, 1): 'D',
        }[(cell.x, cell.y)]

        return d

    def __str__(self):
        ret = ''
        for y, line in enumerate(self.grid):
            ret += '\n'
            for x, _cell in enumerate(line):
                ret += self.get_arrow(Pos(x=x, y=y))

        return ret[1:]

    def print_arrows(self, pos):
        ret = ''
        last_arrow = None
        while self.get_arrow(pos) != CELL_PLATFORM:  # in ['R', 'D', 'L', 'U'] ?
            arrow = self.get_arrow(pos)
            if arrow != last_arrow:
                ret += ' %d %d %c' % (pos.x, pos.y, arrow)

            pos += self.grid[pos.y][pos.x]
            last_arrow = arrow

        return ret[1:]

#
# Main
#

def main():
    start = datetime.datetime.now()
    out_debug('Hello, world!')

    grid, _, robots = game_parse()
    g = Grid(grid)
    robots_pos = [Pos(x=robot[0], y=robot[1]) for robot in robots]

    out_debug('Time1: %.3f sec' % (datetime.datetime.now()-start).total_seconds())
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
        total_points += g.backtrack(pos)

    out_debug()
    out_debug('== Grid ==')
    out_debug(g)
    out_debug('points: %d' % total_points)

    arrows = [g.print_arrows(pos) for pos in robots_pos]
    out_print(' '.join(arrows))

    out_debug('Time2: %.3f sec' % (datetime.datetime.now()-start).total_seconds())


main()
