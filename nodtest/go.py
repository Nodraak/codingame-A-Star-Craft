#!/usr/bin/env python3

import json
import subprocess
import sys
import time

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


def run_test(ident, title, grid):

    # print header

    print_section('#'*80)
    print_section('### Test %2d - %s' % (ident, title))
    print_section('#'*80)

    # find robots and build input data

    robots = []
    for y, line in enumerate(grid):
        for x, cell in enumerate(line):
            if cell in ['R', 'D', 'L', 'U']:  # upper case == robot
                robots.append([x, y, cell])

    assert len(robots) != 0

    input_data = '\n'.join((
        '\n'.join(grid),
        '%d' % len(robots),
        '\n'.join([' '.join([str(c) for c in r]) for r in robots]),
    )) + '\n'

    # print debug

    print_header('Input data')
    print_data(input_data)

    # start test

    p = subprocess.Popen(
        ['python3', 'nodia/go.py'],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    stdout, stderr = p.communicate(input=input_data.encode('utf8'))
    stdout = stdout.decode('utf8')
    stderr = stderr.decode('utf8')

    print_header('Stdout')
    print_data(stdout)
    print_header('Stderr (rc=%d)' % p.returncode)
    print_data(stderr)


def main():
    assert len(sys.argv) == 2
    test_id = int(sys.argv[1])

    filepath = TEST_FILES[test_id-1]

    f = open(filepath, 'r')
    f_json = json.load(f)
    ident = test_id
    title = f_json['title']['2']
    grid = f_json['testIn'].split('\n')

    run_test(ident, title, grid)


main()
