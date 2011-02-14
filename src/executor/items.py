from collections import namedtuple

from dna_code import protect, asnat


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
        return 'IFC'+protect(self, 1)

Reference = namedtuple('Reference', 'n level')
class Reference(Reference):
    def __str__(self):
        if self.level == 0:
            return '\\{0}'.format(self.n)
        return '\\{0}_{0}'.format(self.n, self.level)
    def to_dna(self):
        return 'IF'+asnat(self.level)+asnat(self.n)
    
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
