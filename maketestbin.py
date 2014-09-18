#!/usr/bin/env python
"""Create binary file from input string, for testing."""
import struct


IN = '9,32768,32769,4,19,32768'

with open('test.bin', 'wb') as f:
    codes = map(int, IN.split(','))
    for c in codes:
        f.write(struct.pack('<H', c))  # 16-bit unsigned int