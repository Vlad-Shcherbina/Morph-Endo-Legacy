from collections import namedtuple

import dna_code

__all__ = [
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
        return dna_code.protect(self, 1)
Base.I = Base('I')
Base.C = Base('C')
Base.F = Base('F')
Base.P = Base('P')
Base.decode = {'C': Base.I, 'F': Base.C, 'P': Base.F, 'IC': Base.P}

class Skip(int):
    def __str__(self):
        return '!'+int.__str__(self)
    def to_dna(self):
        return 'IP'+dna_code.asnat(self)

class Search(str):
    def __str__(self):
        return '?"'+self+'"'
    def to_dna(self):
        return 'IFF'+dna_code.protect(self, 1)

Reference = namedtuple('Reference', 'n level')
class Reference(Reference):
    def __str__(self):
        if self.level == 0:
            return '\\{0}'.format(self.n)
        return '\\{0}_{0}'.format(self.n, self.level)
    def to_dna(self):
        # or 'IF'
        return 'IP'+dna_code.asnat(self.level)+dna_code.asnat(self.n)
    
class Length(int):
    def __str__(self):
        return '|{0}|'.format(int.__str__(self))
    def to_dna(self):
        return 'IIP'+dna_code.asnat(self)
    
class RNA_Item(str):
    def __str__(self):
        return '['+self+']'
    def to_dna(self):
        return 'III'+self
