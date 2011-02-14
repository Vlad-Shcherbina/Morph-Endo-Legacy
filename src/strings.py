import re

from dna_code import endo
from string_code import character


def forgiving_unprotect(dna):
    i = iter(dna)
    result = ''
    c = next(i, '')
    while True:
        if c == '':
            break
        if c == 'C':
            result += 'I'
        elif c == 'F':
            result += 'C'
        elif c == 'P':
            result += 'F'
        elif c == 'I':
            c = next(i, '')
            if c == 'P':
                result += 'P'
            else:
                continue
        c = next(i, '') 
    return result


def decode_chars(dna):
    result = ''
    for i in range(0, len(dna), 9):
        bits = dna[i:i+9]
        if 'F' in bits or 'P' in bits:
            if not result.endswith('~'):
                result += '~'
            continue
        bits = bits.replace('I', '0').replace('C', '1')
        bits = bits[::-1]
        x = int(bits, 2)
        if x in character:
            result += character[x]
        else:
            result += '?'
    return result


def strings(s):
    result = []
    for m in re.finditer(r'[^\~^\?]{6,}', s):
        result.append((m.start(), m.end(), m.group()))
    return result

if __name__ == '__main__':
    s = endo()
    for i in range(100):
        print '************** PROTECTION LEVEL', i
        results = []
        for i in range(9):
            data = decode_chars(s[i:])
            results += strings(data)
        results.sort(key=lambda (start, end, text): start)
        for start, end, text in results:
            print text
        s = forgiving_unprotect(s)