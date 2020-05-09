#!/usr/bin/env python3

from crcsolver import compute

# from https://golang.org/src/hash/crc64/crc64_test.go
assert compute(b'', 'CRC-64/GO-ISO') == 0x0
assert compute(b'a', 'CRC-64/GO-ISO') == 0x3420000000000000
assert compute(b'ab', 'CRC-64/GO-ISO') == 0x36c4200000000000
assert compute(b'abc', 'CRC-64/GO-ISO') == 0x3776c42000000000
assert compute(b'abcd', 'CRC-64/GO-ISO') == 0x336776c420000000
assert compute(b'abcde', 'CRC-64/GO-ISO') == 0x32d36776c4200000
assert compute(b'abcdef', 'CRC-64/GO-ISO') == 0x3002d36776c42000
assert compute(b'abcdefg', 'CRC-64/GO-ISO') == 0x31b002d36776c420
assert compute(b'abcdefgh', 'CRC-64/GO-ISO') == 0xe21b002d36776c4
assert compute(b'abcdefghi', 'CRC-64/GO-ISO') == 0x8b6e21b002d36776
assert compute(b'abcdefghij', 'CRC-64/GO-ISO') == 0x7f5b6e21b002d367
assert compute(b'Discard medicine more than two years old.', 'CRC-64/GO-ISO') == 0x8ec0e7c835bf9cdf
assert compute(b'He who has a shady past knows that nice guys finish last.', 'CRC-64/GO-ISO') == 0xc7db1759e2be5ab4
assert compute(b'I wouldn\'t marry him with a ten foot pole.', 'CRC-64/GO-ISO') == 0xfbf9d9603a6fa020
assert compute(b'Free! Free!/A trip/to Mars/for 900/empty jars/Burma Shave', 'CRC-64/GO-ISO') == 0xeafc4211a6daa0ef
assert compute(b'The days of the digital watch are numbered.  -Tom Stoppard', 'CRC-64/GO-ISO') == 0x3e05b21c7a4dc4da
assert compute(b'Nepal premier won\'t resign.', 'CRC-64/GO-ISO') == 0x5255866ad6ef28a6
assert compute(b'For every action there is an equal and opposite government program.', 'CRC-64/GO-ISO') == 0x8a79895be1e9c361
assert compute(b'His money is twice tainted: \'taint yours and \'taint mine.', 'CRC-64/GO-ISO') == 0x8878963a649d4916
assert compute(b'There is no reason for any individual to have a computer in their home. -Ken Olsen, 1977', 'CRC-64/GO-ISO') == 0xa7b9d53ea87eb82f
assert compute(b'It\'s a tiny change to the code and not completely disgusting. - Bob Manchek', 'CRC-64/GO-ISO') == 0xdb6805c0966a2f9c
assert compute(b'size:  a.out:  bad magic', 'CRC-64/GO-ISO') == 0xf3553c65dacdadd2
assert compute(b'The major problem is with sendmail.  -Mark Horton', 'CRC-64/GO-ISO') == 0x9d5e034087a676b9
assert compute(b'Give me a rock, paper and scissors and I will move the world.  CCFestoon', 'CRC-64/GO-ISO') == 0xa6db2d7f8da96417, 0x7eca10d2f8136eb4
assert compute(b'If the enemy is within range, then so are you.', 'CRC-64/GO-ISO') == 0x325e00cd2fe819f9, 0xd7dd118c98e98727
assert compute(b'It\'s well we cannot hear the screams/That we create in others\' dreams.', 'CRC-64/GO-ISO') == 0x88c6600ce58ae4c6
assert compute(b'You remind me of a TV show, but that\'s all right: I watch it anyway.', 'CRC-64/GO-ISO') == 0x28c4a3f3b769e078, 0x57c891e39a97d9b7
assert compute(b'C is as portable as Stonehedge!!', 'CRC-64/GO-ISO') == 0xa698a34c9d9f1dca
assert compute(b'Even if I could be Shakespeare, I think I should still choose to be Faraday. - A. Huxley', 'CRC-64/GO-ISO') == 0xf6c1e2a8c26c5cfc, 0x7ad25fafa1710407
assert compute(b'The fugacity of a constituent in a mixture of gases at a given temperature is proportional to its mole fraction.  Lewis-Randall Rule', 'CRC-64/GO-ISO') == 0xd402559dfe9b70c
assert compute(b'How can you write a big system without C++?  -Paul Glick', 'CRC-64/GO-ISO') == 0xdb6efff26aa94946
assert compute(b'This is a test of the emergency broadcast system.', 'CRC-64/GO-ISO') == 0xe7fcf1006b503b61

print('PASS')
