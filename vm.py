#!/usr/bin/env python
"""
Synacor challenge for OSCON 2012.

Architecture description in file arch-spec.
"""
import struct
import sys
from inspect import getargspec


MAX_LITERAL = 32768


class VM(object):
    OPCODES = [
        'halt', 'set', 'push', 'pop', 'eq', 'gt', 'jmp', 'jt', 'jf', 'add',
        'mult', 'mod', 'and', 'or', 'not', 'rmem', 'wmem', 'call', 'ret',
        'out', 'in', 'noop'
    ]

    ## Storage regions
    # Memory with 15-bit address space storing 16-bit numbers.
    mem = []
    # 8 (16-bit) Registers
    regs = [0 for i in xrange(8)]
    # Unbounded stack
    stack = []

    # Current memory offset. Astonishingly, start at the top.
    offset = 0

    # Because we read keyboard input by the line, we need to hold on to it
    # until we've read it all.
    input_buffer = None


    ## Helpers
    def reg_lit(self, a):
        """Return register content or literal."""
        assert a <= 32775
        if a < MAX_LITERAL:
            return a
        else:
            return self.regs[a % MAX_LITERAL]

    def write_reg(self, a, b):
        """Write b to register at address a."""
        assert 32768 <= a <= 32775
        self.regs[a % MAX_LITERAL] = b


    ## Individual opcode implementations
    def op_halt(self):
        """0: stop execution and terminate the program"""
        sys.exit()

    def op_set(self, a, b):
        """1: set register <a> to the value of <b>"""
        self.write_reg(a, self.reg_lit(b))

    def op_push(self, a):
        """2: push <a> onto the stack"""
        self.stack.append(self.reg_lit(a))

    def op_pop(self, a):
        """
        3: remove the top element from the stack and write it into <a>;
        empty stack = error
        """
        self.write_reg(a, self.stack.pop())

    def op_eq(self, a, b, c):
        """4: set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise"""
        if self.reg_lit(b) == self.reg_lit(c):
            self.write_reg(a, 1)
        else:
            self.write_reg(a, 0)

    def op_gt(self, a, b, c):
        """
        5: set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
        """
        if self.reg_lit(b) > self.reg_lit(c):
            self.write_reg(a, 1)
        else:
            self.write_reg(a, 0)

    def op_jmp(self, a):
        """6: jump to <a>"""
        assert a < len(self.mem)
        self.offset = a

    def op_jt(self, a, b):
        """7: if <a> is nonzero, jump to <b>"""
        if self.reg_lit(a) != 0:
            self.op_jmp(b)

    def op_jf(self, a, b):
        """8: if <a> is zero, jump to <b>"""
        if self.reg_lit(a) == 0:
            self.op_jmp(b)

    def op_add(self, a, b, c):
        """9: assign into <a> the sum of <b> and <c> (modulo 32768)"""
        self.write_reg(a, (self.reg_lit(b) + self.reg_lit(c)) % MAX_LITERAL)

    def op_mult(self, a, b, c):
        """10: store into <a> the product of <b> and <c> (modulo 32768)"""
        self.write_reg(a, (self.reg_lit(b) * self.reg_lit(c)) % MAX_LITERAL)

    def op_mod(self, a, b, c):
        """11: store into <a> the remainder of <b> divided by <c>"""
        self.write_reg(a, self.reg_lit(b) % self.reg_lit(c))

    def op_and(self, a, b, c):
        """12: stores into <a> the bitwise and of <b> and <c>"""
        self.write_reg(a, self.reg_lit(b) & self.reg_lit(c))

    def op_or(self, a, b, c):
        """13: stores into <a> the bitwise or of <b> and <c>"""
        self.write_reg(a, self.reg_lit(b) | self.reg_lit(c))

    def op_not(self, a, b):
        """14: stores 15-bit bitwise inverse of <b> in <a>"""
        self.write_reg(a, (~self.reg_lit(b) & ((1 << 15) - 1)))

    def op_rmem(self, a, b):
        """15: read memory at address <b> and write it to <a>"""
        self.write_reg(a, self.mem[self.reg_lit(b)])

    def op_wmem(self, a, b):
        """16: write the value from <b> into memory at address <a>"""
        self.mem[self.reg_lit(a)] = self.reg_lit(b)

    def op_call(self, a):
        """
        17: write the address of the next instruction to the stack and jump
        to <a>
        """
        self.op_push(self.offset)
        self.op_jmp(self.reg_lit(a))

    def op_ret(self):
        """
        18: remove the top element from the stack and jump to it;
        empty stack = halt
        """
        try:
            a = self.stack.pop()
        except IndexError:
            # Empty stack
            self.op_halt()
        self.op_jmp(a)

    def op_out(self, a):
        """
        19: write the character represented by ascii code <a> to the terminal
        """
        sys.stdout.write(chr(self.reg_lit(a)))

    def op_in(self, a):
        """
        20: read a character from the terminal and write its ascii code to
        <a>; it can be assumed that once input starts, it will continue until
        a newline is encountered; this means that you can safely read whole
        lines from the keyboard and trust that they will be fully read
        """
        if self.input_buffer is None:
            # Collect user input.
            input = raw_input()

            # Drop me into a debugger.
            if input == 'debug':
                import ipdb; ipdb.set_trace()
                return

            self.input_buffer = (c for c in input)

        # Return char by char, finish with newline.
        try:
            char = self.input_buffer.next()
        except StopIteration:
            self.input_buffer = None  # Reset.
            char = '\n'

        self.write_reg(a, ord(char))

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
        for i in xrange(argcount):
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
            if self.offset == len(self.mem):  # End of file
                break


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
