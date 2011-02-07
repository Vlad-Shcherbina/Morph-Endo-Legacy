from blist import blist


class Iterator(object):
    def __init__(self, list, start=0):
        self.list = list
        self.len = len(list)
        self.index = start

    def __iter__(self):
        return self

    def current(self):
        return self.list[self.index]

    def next(self, *args):
        self.index += 1
        if self.index <= self.len:
            return self.list[self.index-1]
        
        if len(args) == 0:
            raise StopIteration()
        else:
            default, = args
            return default
        
    def back(self, steps=1):
        assert self.index >= steps
        self.index -= steps
        
        
 
class OpenParen(object):
    def __str__(self):
        return '('

class CloseParen(object):
    def __str__(self):
        return ')'

class Base(str):
    def __str__(self):
        return str.__str__(self)

class Skip(int):
    def __str__(self):
        return '!'+int.__str__(self)

class Search(str):
    def __str__(self):
        return '?"'+self+'"'


class FinishException(Exception):
    pass
        
        
class Executor(object):
    def __init__(self, dna):
        self.dna = dna
        self.dna_iter = Iterator(dna)
        self.rna = []
        self.cost = 0    
        
    
    def pattern(self):
        dna_iter = self.dna_iter
        lvl = 0
        while True:
            a = next(dna_iter, None)
            if a is None:
                raise FinishException()
            if a == 'C':
                yield Base('I')
            elif a == 'F':
                yield Base('C')
            elif a == 'P':
                yield Base('F')
            elif a == 'I':
                b = next(dna_iter, None)
                if b is None:
                    raise FinishException()
                if b == 'C':
                    yield Base('P')
                elif b == 'P':
                    yield Skip(self.nat())
                elif b == 'F':
                    yield Search(self.consts())
                elif b == 'I':
                    c = next(dna_iter, None)
                    if c is None:
                        raise FinishException()
                    if c == 'P':
                        lvl += 1
                        yield OpenParen()
                    elif c in 'CF':
                        if lvl == 0:
                            return
                        lvl -= 1
                        yield CloseParen()
                    elif c == 'I':
                        s = ''
                        for i in range(7):
                            s += next(dna_iter, '')
                        self.rna.append(s)
                    else:
                        assert False
                else:
                    assert False
            else:
                assert False
        
    def nat(self):
        s = []
        while True:
            a = next(self.dna_iter, None)
            if a == 'P' or a is None:
                break
            s.append(a)
        s.reverse()
        s = ''.join(s)
        s = s.replace('I', '0').replace('F', '0').replace('C', '1')
        return int(s, 2)
    
    def consts(self):
        dna_iter = self.dna_iter
        result = []
        while True:
            a = next(dna_iter, None)
            if a == 'C':
                result.append('I')
            elif a == 'F':
                result.append('C')
            elif a == 'P':
                result.append('F')
            elif a == 'I':
                b = next(dna_iter, None)
                if b == 'C':
                    result.append('P')
                else:
                    dna_iter.back(2)
                    break
            else:
                assert a is None
                dna_iter.back()
                break
        return ''.join(result)
    
            
if __name__ == '__main__':
    #print OpenParen(), Base('I'), Skip(10), Search('ABC')
    
    e = Executor('IIPIPICPIICICIIF')
    for p in e.pattern():
        print p,
    print
    