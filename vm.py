#!/usr/bin/env python
"""
Synacor challenge for OSCON 2012.

Architecture description in file arch-spec.
"""
import struct
import sys


# Memory with 15-bit address space storing 16-bit numbers.
# {address: number}
MEM = []
# 8 (16-bit) Registers
REGS = [i for i in xrange(8)]
# Unbounded stack
STACK = []


def run():
    """Run application from memory."""
    offset = 0
    while True:
        op = MEM[offset]


def main():
    """Run this as ./vm.py <inputfile>."""
    try:
        infile = sys.argv[1]
    except IndexError:
        sys.exit(main.__doc__)

    # Read input file into memory.
    with open(infile, 'rb') as f:
        # Read 16 bits at a time.
        chunk = f.read(2)
        while chunk != '':
            MEM.append(struct.unpack('<H', chunk)[0])
            chunk = f.read(2)


# Run it
if __name__ == '__main__':
    main()