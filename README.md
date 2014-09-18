# A solution to Synacor's OSCON 2012 programming challenge.

From the [challenge website](https://challenge.synacor.com/):

> This is a programming challenge, but you can use any language you like.
> As you complete sections, come back here to check your answer codes.

I hope you enjoy reading my code and learn a thing or two :)

## Running it
This solution is written in Python (2.7).

There are two ways to run this.
 
- execute ``vm/vm.py challenge.bin``, which will execute the VM and start running the challenge code from the beginning.
- run ``vm/solution.sh``, which plays through the game at a really rapid pace using the standard UNIX tool ``expect``.

## Contributing
If you find any problems, please file a Github Issue!

## License

This solution is (c) 2012-2014 Fred Wenzel, and licensed under an MIT license.

The challenge itself is -- presumably -- copyrighted by the orginial author
Eric ([@ericwastl](https://twitter.com/ericwastl)) and Synacor.


-----

## Architecture Description (from the original challenge)

In this challenge, your job is to use this architecture spec to create a virtual machine capable of running the included binary.  Along the way, you will find codes; submit these to the challenge website to track your progress.  Good luck!

### architecture

- three storage regions
  - memory with 15-bit address space storing 16-bit values
  - eight registers
  - an unbounded stack which holds individual 16-bit values
- all numbers are unsigned integers 0..32767 (15-bit)
- all math is modulo 32768; 32758 + 15 => 5

### binary format

- each number is stored as a 16-bit little-endian pair (low byte, high byte)
- numbers 0..32767 mean a literal value
- numbers 32768..32775 instead mean registers 0..7
- numbers 32776..65535 are invalid
- programs are loaded into memory starting at address 0
- address 0 is the first 16-bit value, address 1 is the second 16-bit value, etc

### execution

- After an operation is executed, the next instruction to read is immediately after the last argument of the current operation.  If a jump was performed, the next operation is instead the exact destination of the jump.
- Encountering a register as an operation argument should be taken as reading from the register or setting into the register as appropriate.

### hints

- Start with operations 0, 19, and 21.
- Here's a code for the challenge website: zucAbtJMOmNr
- The program "9,32768,32769,4,19,32768" occupies six memory addresses and should:
  - Store into register 0 the sum of 4 and the value contained in register 1.
  - Output to the terminal the character with the ascii code contained in register 0.

### opcode listing

```
halt: 0
  stop execution and terminate the program

set: 1 a b
  set register <a> to the value of <b>

push: 2 a
  push <a> onto the stack

pop: 3 a
  remove the top element from the stack and write it into <a>; empty stack = error

eq: 4 a b c
  set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise

gt: 5 a b c
  set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise

jmp: 6 a
  jump to <a>

jt: 7 a b
  if <a> is nonzero, jump to <b>

jf: 8 a b
  if <a> is zero, jump to <b>

add: 9 a b c
  assign into <a> the sum of <b> and <c> (modulo 32768)

mult: 10 a b c
  store into <a> the product of <b> and <c> (modulo 32768)

mod: 11 a b c
  store into <a> the remainder of <b> divided by <c>

and: 12 a b c
  stores into <a> the bitwise and of <b> and <c>

or: 13 a b c
  stores into <a> the bitwise or of <b> and <c>

not: 14 a b
  stores 15-bit bitwise inverse of <b> in <a>

rmem: 15 a b
  read memory at address <b> and write it to <a>

wmem: 16 a b
  write the value from <b> into memory at address <a>

call: 17 a
  write the address of the next instruction to the stack and jump to <a>

ret: 18
  remove the top element from the stack and jump to it; empty stack = halt

out: 19 a
  write the character represented by ascii code <a> to the terminal

in: 20 a
  read a character from the terminal and write its ascii code to <a>;
  it can be assumed that once input starts, it will continue until a
  newline is encountered; this means that you can safely read whole
  lines from the keyboard and trust that they will be fully read

noop: 21
  no operation
```