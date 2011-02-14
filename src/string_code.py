from dna_basics import consts, nat, protect

# codepage, both ways
code = \
{'!': 15, ' ': 0, "'": 61, ')': 29, '(': 13, '*': 28, '-': 32, ',': 43, '/': 33,\
 '.': 11, '1': 177, '0': 176, '3': 179, '2': 178, '5': 181, '4': 180, '7': 183,\
'6': 182, '9': 185, '8': 184, '=': 62, '<': 12, '?': 47, '>': 46, 'A': 129, 'C':\
 131, 'B': 130, 'E': 133, 'D': 132, 'G': 135, 'F': 134, 'I': 137, 'H': 136, 'K':\
 146, 'J': 145, 'M': 148, 'L': 147, 'O': 150, 'N': 149, 'Q': 152, 'P': 151, 'S':\
 162, 'R': 153, 'U': 164, 'T': 163, 'W': 166, 'V': 165, 'Y': 168, 'X': 167, '[':\
 10, 'Z': 169, ']': 26, '_': 45, 'a': 65, 'c': 67, 'b': 66, 'e': 69, 'd': 68, \
'g': 71, 'f': 70, 'i': 73, 'h': 72, 'k': 82, 'j': 81, 'm': 84, 'l': 83, 'o': 86,\
'n': 85, 'q': 88, 'p': 87, 's': 98, 'r': 89, 'u': 100, 't': 99, 'w': 102,\
'v': 101, 'y': 104, 'x': 103, 'z': 105}

character = dict(zip(code.values(), code.keys()))



# this should append the I's before P instead
# but fuck it
#def asnat_fixed_length(n, length=9):
#    s = dna_code.asnat(n)
#    assert(len(s) <= length)
#    return 'I'*(length - len(s)) + s

def asnat_fixed_length(n, length=9):
    r = []
    while (n > 0) or (length > 1):
        r.append('IC'[n%2])
        n //= 2
        length -= 1
    r.append('P')
    return ''.join(r)


def extract_from_offset(dna, offset, level=1):
    result = ""
    gen = (dna[i] for i in xrange(offset, len(dna)))
    for l in xrange(level):
        gen = consts(gen)
    gen = nat(gen)
    for c in gen:
        if c == 255:
            result += "<EoL>"
            break
        if c in character:
            result += character[c]
        else:
            result += "<" + str(c) + ">"
    return result

def search(dna, substring, level=1):
    substring_dna = ''.join(asnat_fixed_length(code[c]) for c in substring)
    substring_dna = protect(substring_dna, level) # inefficient
    return dna.find(substring_dna)

def extract_from_prefix(dna, substring, level=1):
    offset = search(dna, substring, level)
    if offset > 0:
        return extract_from_offset(dna, offset, level)
    else:
        return ""
