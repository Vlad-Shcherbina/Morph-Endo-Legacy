from collections import namedtuple

class OpenParen(object):
    def __str__(self):
        return '('
    
open_paren = OpenParen()    

class CloseParen(object):
    def __str__(self):
        return ')'
close_paren = CloseParen()

class Base(str):
    def __str__(self):
        return str.__str__(self)
Base.I = Base('I')
Base.C = Base('C')
Base.F = Base('F')
Base.P = Base('P')
Base.decode = {'C': Base.I, 'F': Base.C, 'P': Base.F, 'IC': Base.P}

class Skip(int):
    def __str__(self):
        return '!'+int.__str__(self)

class Search(str):
    def __str__(self):
        return '?"'+self+'"'

Reference = namedtuple('Reference', 'n level')
class Reference(Reference):
    def __str__(self):
        if self.level == 0:
            return '\\{0}'.format(self.n)
        return '\\{0}_{0}'.format(self.n, self.level)
    
class Length(int):
    def __str__(self):
        return '|{0}|'.format(int.__str__(self)) 
    
class RNA_Item(str):
    def __str__(self):
        return '['+self+']'
    
