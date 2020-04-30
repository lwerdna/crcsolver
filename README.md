# crcsolver

solve for data, given a target cyclic redundancy check (CRC)

# Use

We'll target python's built-in crc32:

```
>>> import binascii
>>> binascii.crc32(b'penguin')
3854672160
```

Now suppose we lost the 'e', so we have b'p_nguin' and need to solve for it. With bits indexed left-to-right across the input, the missing character is at bits [8,9,10,11,12,13,14,15].

```
>>> from crcsolver import solve
>>> solve(b'p_nguin', [8,9,10,11,12,13,14,15], 3854672160, binascii.crc32)
b'penguin'
```

The solve takes what data is known, a list of bits that are unknown, a target CRC result, and a CRC calculating function which it will call while finding a solution.

Any n-bit CRC is solvable with at least n bits of freedom, but might not have a solution with less. Here's a failed attempt to toggle the first 8 bits of b'XXXXXXXX' to the same CRC has b'penguin'. When there is no solution, solve() returns None:

```
>>> solve(b'XXXXXXXX', range(8), 3854672161, binascii.crc32)
>>>
```

With 32 bits of freedom, a solution exists:

```
>>> solve(b'XXXXXXXX', range(32), 3854672161, binascii.crc32)
b'B\xb0\xfd\x95XXXX'
```

Note the solver doesn't know what data looks nice or not. It will find the first solution, which may not be human readable. Verify:

```
>>> binascii.crc32(b'B\xb0\xfd\x95XXXX')
3854672161
```
