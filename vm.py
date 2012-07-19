#!/usr/bin/env python
"""
Synacor challenge for OSCON 2012.

Architecture description in file arch-spec.
"""
import struct
import sys
from inspect import getargspec


## Operations
class VM(object):
    OPCODES = [
        'halt', 'set', 'push', 'pop', 'eq', 'gt', 'jmp', 'jt', 'jf', 'add',
        'mult', 'mod', 'and', 'or', 'not', 'rmem', 'wmem', 'call', 'ret',
        'out', 'in', 'noop'
    ]

    ## Storage regions
    # Memory with 15-bit address space storing 16-bit numbers.
    # {address: number}
    mem = []
    # 8 (16-bit) Registers
    regs = [0 for i in xrange(8)]
    # Unbounded stack
    stack = []

    # Current memory offset. Astonishingly, start at the top.
    offset = 0


    ## Individual opcode implementations
    def op_halt(self):
        """0: stop execution and terminate the program"""
        sys.exit()

    def op_jmp(self, a):
        """6: jump to <a>"""
        assert a < len(self.mem)
        self.offset = a

    def op_out(self, a):
        """
        19: write the character represented by ascii code <a> to the terminal
        """
        sys.stdout.write(chr(a))

    def op_noop(self):
        """21: no operation"""
        pass

    def execute(self):
        """Opcode dispatcher."""
        # Map opcode to implementation
        op = self.mem[self.offset]
        try:
            func = getattr(self, 'op_%s' % self.OPCODES[op])
        except (IndexError, AttributeError):
            raise NotImplementedError('Opcode %s not implemented.' % op)
        self.offset += 1

        # Determine how many args we must pass to this op code.
        argcount = len(getargspec(func).args) - 1  # Ignore "self".
        args = []

        # Collect args.
        if argcount:
            arg = self.mem[self.offset]
            args.append(arg)
            self.offset += 1

        # Execute it.
        func(*args)



    def run(self):
        """Run application from memory."""
        self.offset = 0
        while True:
            self.execute()


# Load and execute a vm
def main():
    """Run this as ./vm.py <inputfile>."""
    try:
        infile = sys.argv[1]
    except IndexError:
        sys.exit(main.__doc__)

    vm = VM()

    # Read input file into memory.
    with open(infile, 'rb') as f:
        # Read 16 bits at a time.
        chunk = f.read(2)
        while chunk != '':
            vm.mem.append(struct.unpack('<H', chunk)[0])
            chunk = f.read(2)

    vm.run()


# Run it
if __name__ == '__main__':
    main()