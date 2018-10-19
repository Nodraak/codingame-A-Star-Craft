#!/usr/bin/env python3

import json


TEST_FILES = ['A-Star-Craft/config/test%d.json' % i for i in range(1, 30+1)]


for filepath in TEST_FILES:
    f = open(filepath, 'r')
    f_json = json.load(f)

    print(filepath)
    print(f_json['testIn'])
    print()
