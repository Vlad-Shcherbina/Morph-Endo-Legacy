# low level dna encoding stuff

from collections import namedtuple

__all__ = [
    'protect',
    'asnat',
    'consts',
    'nat',
    'OpenParen',
    'open_paren',
    'CloseParen',
    'close_paren',
    'Base',
    'Skip',
    'Search',
    'Reference',
    'Length',
    'RNA_Item',
    ]


def protect(dna, level):
    assert level >= 0
    m = {'I': 'C', 'C': 'F', 'F': 'P', 'P': 'IC'}
    a = ['I']
    for i in range(level+3):
        a.append(''.join(map(m.get, a[-1])))
        
    m = dict(zip('ICFP', a[-4:]))
    return ''.join(map(m.get, dna))
 
def asnat(n):
    r = []
    while n > 0:
        r.append('IC'[n%2])
        n //= 2
    r.append('P')
    return ''.join(r)

def consts(dna):
    for base in dna:
        if base == 'I':
            try:
                nextbase = dna.next()
            except StopIteration:
                return
            if nextbase == 'C':
                yield 'P'
            else:
                return
        else:
            yield {'C':'I', 'F':'C', 'P':'F'}[base]

def nat(dna):
    result = 0
    power = 1
    for base in dna:
        if base == 'P':
            yield result
            result = 0
            power = 1
            continue
        elif base == 'C':
            result += power
        power *= 2


class OpenParen(object):
    def __str__(self):
        return '('
    def to_dna(self):
        return 'IIP'
    
open_paren = OpenParen()    

class CloseParen(object):
    def __str__(self):
        return ')'
    def to_dna(self):
        return 'IIC'
close_paren = CloseParen()

class Base(str):
    def __str__(self):
        return str.__str__(self)
    def to_dna(self):
        return protect(self, 1)
Base.I = Base('I')
Base.C = Base('C')
Base.F = Base('F')
Base.P = Base('P')
Base.decode = {'C': Base.I, 'F': Base.C, 'P': Base.F, 'IC': Base.P}

class Skip(int):
    def __str__(self):
        return '!'+int.__str__(self)
    def to_dna(self):
        return 'IP'+asnat(self)

class Search(str):
    def __str__(self):
        return '?"'+self+'"'
    def to_dna(self):
        return 'IFF'+protect(self, 1)

Reference = namedtuple('Reference', 'n level')
class Reference(Reference):
    def __str__(self):
        if self.level == 0:
            return '\\{0}'.format(self.n)
        return '\\{0}_{0}'.format(self.n, self.level)
    def to_dna(self):
        # or 'IF'
        return 'IP'+asnat(self.level)+asnat(self.n)
    
class Length(int):
    def __str__(self):
        return '|{0}|'.format(int.__str__(self))
    def to_dna(self):
        return 'IIP'+asnat(self)
    
class RNA_Item(str):
    def __str__(self):
        return '['+self+']'
    def to_dna(self):
        return 'III'+self
