#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import re

from termcolor import colored


TEST_FILES = ['A-Star-Craft/config/test%d.json' % i for i in range(1, 30+1)]


def print_c(string='', color=None):
    reset = '\033[0m'
    c = {
        'black': '\033[0;30m',
        'red': '\033[0;31m',
        'green': '\033[0;32m',
        'yellow': '\033[0;33m',
        'blue': '\033[0;34m',
        'purple': '\033[0;35m',
        'cyan': '\033[0;36m',
        'white': '\033[0;37m',
    }.get(color, reset)

    print('%s%s%s' % (c, string, reset))

def print_section(s):
    print_c(s, 'green')

def print_header(s):
    print_c('### %s %s' % (s, '#'*(75-len(s))), 'blue')

def print_data(s):
    print_c(s, 'yellow')


def run_test(ident, title, grid, verbose):

    # print header

    if verbose:
        print_section('#'*80)
        print_section('### Test %2d - %s' % (ident, title))
        print_section('#'*80)
    else:
        print('Running test %2d %s' % (ident, title))

    # find robots and build input data

    robots = []
    for y, line in enumerate(grid):
        for x, cell in enumerate(line):
            if cell in ['R', 'D', 'L', 'U']:  # upper case == robot
                robots.append([x, y, cell])
                grid[y][x] = '.'
            elif cell in ['r', 'd', 'l', 'u']:  # lower case == initial
                grid[y][x] = grid[y][x].upper()

    assert len(robots) != 0

    input_data = '\n'.join((
        '\n'.join([''.join([c for c in line]) for line in grid]),
        '%d' % len(robots),
        '\n'.join([' '.join([str(c) for c in r]) for r in robots]),
    )) + '\n'

    # print debug

    if verbose:
        print_header('Input data')
        print_data(input_data)

    # start test

    p = subprocess.Popen(
        ['python3', 'nodia/go.py'],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    stdout, stderr = p.communicate(input=input_data.encode('utf8'), timeout=2)
    stdout = stdout.decode('utf8')
    stderr = stderr.decode('utf8')

    if verbose:
        print_header('Stderr (rc=%d)' % p.returncode)
        print_data(stderr)
        print_header('Stdout')
        print_data(stdout)

    # extract score prediction

    if p.returncode != 0:
        return -1, -1

    score = int(re.findall(r'points: ([0-9]+)\n', stderr, re.MULTILINE)[0])
    time = int(re.findall(r'Time2: ([0-9]+)', stderr, re.MULTILINE)[0])
    return score, time


def test_load_and_run(test_id, verbose=True):
    filepath = TEST_FILES[test_id-1]
    f = open(filepath, 'r')
    f_json = json.load(f)
    ident = test_id
    title = f_json['title']['2']
    grid = [[c for c in line] for line in f_json['testIn'].split('\n')]

    return run_test(ident, title, grid, verbose)


def main():
    assert len(sys.argv) == 2
    if sys.argv[1] != 'all':
        test_id = int(sys.argv[1])
        test_load_and_run(test_id)
    else:
        scores = []
        for i in range(1, 30+1):
            tup = test_load_and_run(i, verbose=False)
            scores.append(tup)

        out = ''

        for i, (s, t) in enumerate(scores):
            out += 'Test %2d:\n\t%3d\n\t\t%4d\n' % (i+1, s, t)
        out += 'Total: %4d\n' % sum([tup[0] for tup in scores])

        print(out)
        with open('out.txt', 'w') as f:
            f.write(out)

        print('Wrote output to out.txt')

main()
