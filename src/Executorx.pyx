from collections import defaultdict
from blist import blist

import kmp
from helpers import protect, asnat, limit_string
from items import Base, OpenParen, open_paren, CloseParen, close_paren, \
    Skip, Search, Reference, Length 


#dna_type is something that supports following operations:
#    empty initialization
#    initialization from string
#    __len__()
#    [index]
#    [begin:end] -- produces dna_type as well
#    append(char)
#    extend(dna_type)
#  
dna_type = blist


class FinishException(Exception):
    pass

        
class Executor(object):
    def __init__(self, dna):
        #assert all(c in 'ICFP' for c in dna)
        self.dna = dna_type(dna)
        self.dna_len = len(self.dna)
        self.rna = []
        self.cost = 0
        self.debug = False
        self.iteration = 0
        self.pattern_freqs = defaultdict(int)
        self.template_freqs = defaultdict(int)
        self.codon_len_freqs = defaultdict(int)
        self.begin_dna_scan()
             
#    def obtain_rna(self):
#        try:
#            while True:
#                self.step()
#                for r in self.rna:
#                    yield r
#                self.rna = []
#        except FinishException:
#            pass
#        for r in self.rna:
#            yield r
#        self.rna = []
        
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
            self.dna = self.dna[self.index:self.dna_len]
            self.dna_len = len(self.dna)
            
        self.matchreplace(p, t)
        self.begin_dna_scan()
        self.iteration += 1
        
        if self.debug:
            print 'len(rna) =', len(self.rna)
            print

    def begin_dna_scan(self):
        self.index = 0
        self.saved_codon = None # because we sometimes unread codon

    def read_base(self):
        '''return base or empty string in case of EOF'''
        assert self.saved_codon is None #because of the structure of the parser
        if self.index == self.dna_len:
            return ''
        self.index += 1
        return self.dna[self.index - 1]
        
    def read_codon(self):
        '''return "", C, F, P, IC, IF, IP, IIC, IIF, IIP or III'''
        # it turned out to be useful for parsing pattern, template and consts
        if self.saved_codon is not None:
            result = self.saved_codon
            self.saved_codon = None
            #self.index += len(result)
            return result
        
        dna = self.dna
        index = self.index
        bases_left = self.dna_len - index
        max_len = bases_left if bases_left < 3 else 3 # faster than min
            
        codon = ''    
        codon_len = 0
        while codon_len < max_len:
            base = dna[index + codon_len]
            codon_len += 1
            codon += base
            if base != 'I':
                break
               
        self.index += codon_len
        
        self.codon_len_freqs[codon_len] += 1
        return codon

    
    def unread_codon(self, codon):
        assert self.saved_codon is None
        #self.index -= len(codon)
        self.saved_codon = codon

    def pattern(self):
        result = []
        lvl = 0
        while True:
            a = self.read_codon()
            
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
                command = ''
                for i in range(7):
                    command += self.read_base()
                self.rna.append(command)
                
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
            a = self.read_codon()
            
            if a == 'C':
                result.append('I')
                
            elif a == 'F':
                result.append('C')
                
            elif a == 'P':
                result.append('F')
                
            elif a == 'IC':
                result.append('P')
                
            else:
                self.unread_codon(a) #it will be later consumed in pattern()
                break
            
        return ''.join(result)
    
    def template(self):
        result = []
        while True:
            a = self.read_codon()
            
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
                command = ''
                for i in range(7):
                    command += self.read_base()
                self.rna.append(command)
                
            else:
                raise FinishException(a)

            
    def matchreplace(self, pattern, template):
        e = []
        i = 0
        c = []
        dna = self.dna
       # dna_len = self.dna_len
        for p in pattern:
            tp = type(p)
            if tp is Base:
                self.cost += 1
                if dna[i] == p:
                    i += 1
                else:
                    if self.debug:
                        print 'failed match (base)'
                    return
                
            elif tp is Skip:
                i += p
                if i > len(dna):
                    if self.debug:
                        print 'failed match (skip)'
                    return
                
            elif tp is Search:
                j = next(kmp.find(dna, p, start=i), None)
                if j is not None:
                    self.cost += j + len(p) - i
                    i = j + len(p)
                else:
                    self.cost += len(dna) - i
                    if self.debug:
                        print 'failed match (search)'
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
        dna = dna[i:len(dna)]
        r.extend(dna)
        self.dna = r
        self.dna_len = len(self.dna)
        
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
                r.extend(asnat(end - begin))
        return r
