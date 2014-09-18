#!/usr/bin/env python
"""Solve coin equation from game."""
import itertools

COINS = (2, 3, 5, 7, 9)


for comb in itertools.permutations(COINS):
    a, b, c, d, e = comb
    if a + b * c ** 2 + d ** 3 - e == 399:
        print "Found! Combination is %s" % ', '.join(map(str, comb))