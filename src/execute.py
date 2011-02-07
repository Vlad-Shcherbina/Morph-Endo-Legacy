from collections import namedtuple, defaultdict

from blist import blist
from utils import kmp

        
        
 
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
            return '\\{}'.format(self.n)
        return '\\{}_{}'.format(self.n, self.level)
    
class Length(int):
    def __str__(self):
        return '|{}|'.format(int.__str__(self))    


class FinishException(Exception):
    pass
        
        
pattern_freqs = defaultdict(int)
template_freqs = defaultdict(int)
        
dna_type = blist
        
class Executor(object):
    def __init__(self, dna):
        self.dna = dna_type(dna)
        self.rna = []
        self.cost = 0
        self.debug = False
        self.iteration = 0
         
        
    def step(self):
        if self.debug:
            print 'iteration', self.iteration
            print 'dna =', limit_string(self.dna)
            
        
        try:
            self.index = 0
            
            p = list(self.pattern())
            if self.debug:
                print 'pattern ', ''.join(map(str, p))
            t = list(self.template())
            if self.debug:
                print 'template', ''.join(map(str, t))
                
            for pp in p:
                pattern_freqs[type(pp)] += 1
            for tt in t:
                template_freqs[type(tt)] += 1
                
        finally:
            self.cost += self.index
            del self.dna[:self.index]
            
        self.matchreplace(p, t)
        self.iteration += 1
        
        if self.debug:
            print 'len(rna) =', len(self.rna)
            print
    
    def read_prefix(self):
        '''return "", C, F, P, IC, IF, IP, IIC, IIF, IIP or III'''
        dna = self.dna
        prefix = ''
        while True:
            if self.index == len(dna):
                return prefix
            prefix += dna[self.index]
            self.index += 1
            if prefix[-1] != 'I' or len(prefix) == 3:
                return prefix

    def read_base(self):
        if self.index == len(self.dna):
            return ''
        self.index += 1
        return self.dna[self.index-1]
        
    def pattern(self):
        lvl = 0
        while True:
            a = self.read_prefix()
            
            base = Base.decode.get(a)
            if base is not None:
                yield base
                
            elif a == 'IP':
                yield Skip(self.nat())
                
            elif a == 'IF':
                self.read_base() # that's right
                yield Search(self.consts())
                
            elif a == 'IIP':
                lvl += 1
                yield open_paren
                
            elif a == 'IIC' or a == 'IIF':
                if lvl == 0:
                    return
                lvl -= 1
                yield close_paren
                
            elif a == 'III':
                self.rna.append(''.join(self.read_base() for i in range(7)))
                
            else:
                raise FinishException()
            
    def nat(self):
        s = []
        while True:
            a = self.read_base()
            if a == '' or a == 'P':
                break
            s.append(a)
            
        s.reverse()
        s = ''.join(s)
        s = s.replace('I', '0').replace('F', '0').replace('C', '1')
        if s == '':
            return 0
        return int(s, 2)
    
    def consts(self):
        result = []
        while True:
            a = self.read_prefix()
            
            if a == 'C':
                result.append('I')
                
            elif a == 'F':
                result.append('C')
                
            elif a == 'P':
                result.append('F')
                
            elif a == 'IC':
                result.append('P')
                
            else:
                # undo read_prefix
                self.index -= len(a)
                break
        return ''.join(result)
    
    def template(self):
        while True:
            a = self.read_prefix()
            
            base = Base.decode.get(a)
            if base is not None:
                yield base
                
            elif a == 'IF' or a == 'IP':
                level = self.nat()
                n = self.nat()
                yield Reference(n, level)
                
            elif a == 'IIC' or a == 'IIF':
                return
            
            elif a == 'IIP':
                yield Length(self.nat())
            
            elif a == 'III':
                self.rna.append(''.join(self.read_base() for i in range(7)))
                
            else:
                raise FinishException(a)
    
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
                j = next(kmp.find(dna, p, start=i), None)
                if j is not None:
                    self.cost += j+len(p)-i
                    i = j+len(p)
                else:
                    self.cost += len(dna)-i
                    if self.debug:
                        print 'failed match'
                    return
#                for j in xrange(i, len(dna)-len(p)+1):
#                    if ''.join(dna[j:j+len(p)]) == p:
#                        self.cost += j+len(p)-i
#                        i = j+len(p)
#                        break
#                else:
#                    self.cost += len(dna)-i
#                    if self.debug:
#                        print 'failed match'
#                    return
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
    r.append('P')
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
    e.debug = False
    
    from time import clock
    start = clock()
    try:
        for i in xrange(5000):
            if i > 0 and i%1000 == 0:
                print i
                print int(i/(clock()-start+1e-6)),'steps/s'
            e.step()
    finally:
        print e.iteration, 'iterations'
        print 'it took', clock()-start
        print 'pattern freqs', pattern_freqs
        print 'template freqs', template_freqs

        
    #sys.stdout.close()
    
if __name__ == '__main__':
    main()    
    