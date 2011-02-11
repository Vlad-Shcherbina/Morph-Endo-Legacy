from collections import defaultdict
from blist import blist
import kmp

from helpers import protect, asnat
from items import Base, OpenParen, open_paren, CloseParen, close_paren,\
    Skip, Search, Reference, Length 

dna_type = blist

class FinishException(Exception):
    pass
        
class Executor(object):
    def __init__(self, dna):
        assert all(c in 'ICFP' for c in dna)
        self.dna = dna_type(dna)
        self.rna = []
        self.cost = 0
        self.debug = False
        self.iteration = 0
        self.init_dna_scan()
        self.pattern_freqs = defaultdict(int)
        self.template_freqs = defaultdict(int)
        self.prefix_len_freqs = defaultdict(int)
         
    def init_dna_scan(self):
        self.index = 0
        self.dna_iter = iter(self.dna)
        self.saved_prefix = None
    
    def obtain_rna(self):
        try:
            while True:
                self.step()
                for r in self.rna:
                    yield r
                self.rna = []
        except FinishException:
            pass
        for r in self.rna:
            yield r
        self.rna = []
        
    def step(self):
        if self.debug:
            print 'iteration', self.iteration
            print 'dna =', limit_string(self.dna)
            
        
        try:
            p = self.pattern()
            if self.debug:
                print 'pattern ', ''.join(map(str, p))
            t = self.template()
            if self.debug:
                print 'template', ''.join(map(str, t))
                
            for pp in p:
                self.pattern_freqs[type(pp)] += 1
            for tt in t:
                self.template_freqs[type(tt)] += 1
                
        finally:
            self.cost += self.index
            del self.dna[:self.index]
            
        self.matchreplace(p, t)
        self.init_dna_scan()
        self.iteration += 1
        
        if self.debug:
            print 'len(rna) =', len(self.rna)
            print
    
#    def read_prefix_old(self):
#        '''return "", C, F, P, IC, IF, IP, IIC, IIF, IIP or III'''
#        dna = self.dna
#        prefix = ''
#        while True:
#            if self.index == len(dna):
#                prefix_len_freqs[len(prefix)] += 1
#                return prefix
#            prefix += dna[self.index]
#            self.index += 1
#            if prefix[-1] != 'I' or len(prefix) == 3:
#                prefix_len_freqs[len(prefix)] += 1
#                return prefix
            
    def read_prefix(self):
        if self.saved_prefix:
            result = self.saved_prefix
            self.saved_prefix = None
            self.index += len(result)
            return result
        dna = self.dna
        len_dna = len(dna)
        dna_iter = self.dna_iter
        local_next = next
        i = self.index
        if i < len_dna:
            #a = dna[i]
            a = local_next(dna_iter)
            i += 1
            if a != 'I':
                self.index = i
                return a
            if i < len_dna:
                #b = dna[i]
                b = local_next(dna_iter)
                i += 1
                if b != 'I':
                    self.index = i
                    return a+b
                if i < len_dna:
                    #c = dna[i]
                    c = local_next(dna_iter)
                    i += 1
                    self.index = i
                    return a+b+c
                self.index = i
                return a+b
            self.index = i
            return a
        return ''
    
    def unread_prefix(self, prefix):
        assert self.saved_prefix is None
        self.index -= len(prefix)
        self.saved_prefix = prefix

    def read_base(self):
        assert self.saved_prefix is None
        if self.index == len(self.dna):
            return ''
        self.index += 1
        #return self.dna[self.index-1]
        return next(self.dna_iter)
        
    def pattern(self):
        result = []
        lvl = 0
        while True:
            a = self.read_prefix()
            
            base = Base.decode.get(a)
            if base is not None:
                result.append(base)
                
            elif a == 'IP':
                result.append(Skip(self.nat()))
                
            elif a == 'IF':
                self.read_base() # that's right
                result.append(Search(self.consts()))
                
            elif a == 'IIP':
                lvl += 1
                result.append(open_paren)
                
            elif a == 'IIC' or a == 'IIF':
                if lvl == 0:
                    return result
                lvl -= 1
                result.append(close_paren)
                
            elif a == 'III':
                self.rna.append(''.join(self.read_base() for i in range(7)))
                
            else:
                raise FinishException()
            
    def nat(self):
        result = 0
        power = 1
        while True:
            a = self.read_base()
            if a == '' or a == 'P':
                break
            if a == 'C':
                result += power
            power *= 2
        
        return result    
    
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
                self.unread_prefix(a)
                break
            
        return ''.join(result)
    
    def template(self):
        result = []
        while True:
            a = self.read_prefix()
            
            base = Base.decode.get(a)
            if base is not None:
                result.append(base)
                
            elif a == 'IF' or a == 'IP':
                level = self.nat()
                n = self.nat()
                result.append(Reference(n, level))
                
            elif a == 'IIC' or a == 'IIF':
                return result
            
            elif a == 'IIP':
                result.append(Length(self.nat()))
            
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
            #print p
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
        base_to_string = str.__str__
        for t in template:
            tt = type(t)
            if tt is Base:
                r.append(base_to_string(t))
            elif tt is Reference:
                if t.n < len(e):
                    begin, end = e[t.n]
                else:
                    begin, end = 0, 0
                if t.level == 0:
                    r.extend(self.dna[begin:end])
                else:
                    p = protect(self.dna[begin:end], t.level)
                    self.cost += len(p)
                    r.extend(p)
            elif tt is Length:
                if t < len(e):
                    begin, end = e[t]
                else:
                    begin, end = 0, 0
                r.extend(asnat(end-begin))
        return r