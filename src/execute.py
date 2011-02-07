from collections import namedtuple

from blist import blist

        
        
 
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

Reference = namedtuple('Reference', 'n level')
class Reference(Reference):
    def __str__(self):
        if self.level == 0:
            return '\\{}'.format(self.n)
        return '\\{}_{}'.format(self.n, self.level)
    
class Length(int):
    def __str__(self):
        return '|{}|'.format(int.__str__(self))    


class FinishException(Exception):
    pass
        
        
dna_type = blist
        
class Executor(object):
    def __init__(self, dna):
        self.dna = dna_type(dna)
        self.rna = []
        self.cost = 0
        self.debug = False
         
        
    def step(self):
        #assert all(c in 'ICFP' for c in self.dna)
        try:
            self.index = 0
            p = list(self.pattern())
            if self.debug:
                print 'pattern ', ''.join(map(str, p))
            t = list(self.template())
            if self.debug:
                print 'template', ''.join(map(str, t))
        finally:
            self.cost += self.index
            del self.dna[:self.index]
            
        self.matchreplace(p, t)
        
    def ahead(self, length):
        return ''.join(self.dna[self.index:self.index+length])
    
    def move(self, delta=1):
        self.index += delta
        if self.index > len(self.dna):
            self.index = len(self.dna)
    
    def pattern(self):
        lvl = 0
        while True:
            a = self.ahead(3)
            
            if a.startswith('C'):
                self.move()
                yield Base('I')
                
            elif a.startswith('F'):
                self.move()
                yield Base('C')
                
            elif a.startswith('P'):
                self.move()
                yield Base('F')
                
            elif a.startswith('IC'):
                self.move(2)
                yield Base('P')
                
            elif a.startswith('IP'):
                self.move(2)
                yield Skip(self.nat())
                
            elif a.startswith('IF'):
                self.move(3) # that's right, 3
                yield Search(self.consts())
                
            elif a.startswith('IIP'):
                self.move(3)
                lvl += 1
                yield OpenParen()
                
            elif a.startswith('IIC') or a.startswith('IIF'):
                self.move(3)
                if lvl == 0:
                    return
                lvl -= 1
                yield CloseParen()
                
            elif a.startswith('III'):
                self.move(3)
                self.rna.append(self.ahead(7))
                self.move(7)
                
            else:
                raise FinishException()
            
    def nat(self):
        s = []
        while True:
            a = self.ahead(1)
            self.move(len(a))
            if a == 'P' or a == '':
                break
            s.append(a)
        s.reverse()
        s = ''.join(s)
        s = s.replace('I', '0').replace('F', '0').replace('C', '1')
        return int('0'+s, 2)
    
    def consts(self):
        result = []
        while True:
            a = self.ahead(2)
            
            if a.startswith('C'):
                self.move()
                result.append('I')
                
            elif a.startswith('F'):
                self.move()
                result.append('C')
                
            elif a.startswith('P'):
                self.move()
                result.append('F')
                
            elif a.startswith('IC'):
                self.move(2)
                result.append('P')
                
            else:
                break
        return ''.join(result)
    
    def template(self):
        while True:
            a = self.ahead(3)
            if a.startswith('C'):
                self.move()
                yield Base('I')
                
            elif a.startswith('F'):
                self.move()
                yield Base('C')
                
            elif a.startswith('P'):
                self.move()
                yield Base('F')
                
            elif a.startswith('IC'):
                self.move(2)
                yield Base('P')
                
            elif a.startswith('IF') or a.startswith('IP'):
                self.move(2)
                level = self.nat()
                n = self.nat()
                yield Reference(n, level)
                
            elif a.startswith('IIC') or a.startswith('IIF'):
                self.move(3)
                break
            
            elif a.startswith('III'):
                self.move(3)
                self.rna.append(self.ahead(7))
                self.move(7)
                
            else:
                raise FinishException()
    
    def matchreplace(self, pattern, template):
        e = []
        i = 0
        c = []
        dna = self.dna
        for p in pattern:
            tp = type(p)
            if tp is Base:
                self.cost += 1
                if dna[i] == p:
                    i += 1
                else:
                    if self.debug:
                        print 'failed match'
                    return
            elif tp is Skip:
                i += p
                if i > len(dna):
                    if self.debug:
                        print 'failed match'
                    return
            elif tp is Search:
                # TODO: kmp
                for j in xrange(i, len(dna)-len(p)+1):
                    if ''.join(dna[j:j+len(p)]) == p:
                        self.cost += j+len(p)-i
                        i = j+len(p)
                        break
                else:
                    self.cost += len(dna)-i
                    if self.debug:
                        print 'failed match'
                    return
            elif tp is OpenParen:
                c.append(i)
            elif tp is CloseParen:
                e.append((c.pop(), i))
            else:
                assert False, 'unknown pattern element'
        
        if self.debug:
            print 'succesful match of length', i
            for j, ee in enumerate(e):
                print 'e[{}] = {}'.format(j, limit_string(dna[ee[0]: ee[1]]))
        r = self.replacement(template, e)
        dna[:i] = r
        
    def replacement(self, template, e):
        r = dna_type()
        for t in template:
            tt = type(t)
            if tt is Base:
                r.append(str.__str__(t))
            elif tt is Reference:
                begin, end = e[t.n]
                if t.level == 0:
                    r.extend(self.dna[begin:end])
                else:
                    p = protect(self.dna[begin:end], t.level)
                    self.cost += len(p)
                    r.extend(p)
            elif tt is Length:
                begin, end = e[t]
                r.extend(asnat(end-begin))
        return r            


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
    return ''.join(r)            


def limit_string(s, maxlen=10):
     if len(s) <= maxlen:
         return ''.join(s)
     return '{}... ({} bases)'.format(''.join(s[:maxlen]), len(s))
            
            
def main():
    # tests from task description
    for q, a in [
        ('IIPIPICPIICICIIFICCIFPPIICCFPC', 'PICFC'),
        ('IIPIPICPIICICIIFICCIFCCCPPIICCFPC', 'PIICCFCFFPC'),
        ('IIPIPIICPIICIICCIICFCFC', 'I'),
        ]:
        e = Executor(q)
        e.step()
        result = ''.join(e.dna)
        #print result
        assert result == a
    
    
    import sys
    
    #sys.stdout = open('../data/mytrace.txt', 'w')
    
    endo = open('../data/endo.dna').read()
    e = Executor(endo)
    e.debug = True
    for i in xrange(10):
        print 'iteration', i
        print 'dna =', limit_string(e.dna)
        e.step()
        print 'len(rna) =', len(e.rna)
        print
        
    #sys.stdout.close()
    
if __name__ == '__main__':
    main()    
    