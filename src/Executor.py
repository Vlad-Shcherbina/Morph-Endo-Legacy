from collections import defaultdict

import kmp
from helpers import limit_string
from dna_code import protect, asnat
from items import Base, OpenParen, open_paren, CloseParen, close_paren, \
    Skip, Search, Reference, Length, RNA_Item 

from DNA_parser import DNA_parser, dna_type
  
class FinishException(Exception):
    pass

class Executor(object):
    def __init__(self, dna):
        #assert all(c in 'ICFP' for c in dna)
        self.pattern_freqs = defaultdict(int)
        self.template_freqs = defaultdict(int)
        self.codon_len_freqs = defaultdict(int)
        self.freqs = [self.pattern_freqs, self.template_freqs, self.codon_len_freqs]
        self.explicit_rna_items = False

        self.dna = dna_type(dna)
        self.parser = DNA_parser(self.dna, self.freqs)
        self.item_starts = []
        self.rna = []
        self.cost = 0
        self.debug = False
        self.iteration = 0
             
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
            index = self.parser.index
            self.cost += index
            self.parser = None
            self.item_starts = []
            del self.dna[:index]
            
        self.matchreplace(p, t)
        self.parser = DNA_parser(self.dna, self.freqs)
        self.iteration += 1
        
        if self.debug:
            print 'len(rna) =', len(self.rna)
            print

    def pattern(self):
        result = []
        lvl = 0
        parser = self.parser
        while True:
            self.item_starts.append(parser.index)
            a = parser.read_codon()
            
            base = Base.decode.get(a)
            if base is not None:
                result.append(base)
                
            elif a == 'IP':
                result.append(Skip(self.nat()))
                
            elif a == 'IF':
                parser.read_base() # that's right
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
                    command += parser.read_base()
                if self.explicit_rna_items:
                    result.append(RNA_Item(command))
                else:
                    self.rna.append(command)
                
            else:
                raise FinishException()
            
    def nat(self):
        result = 0
        power = 1
        while True:
            a = self.parser.read_base()
            if a == '' or a == 'P':
                break
            if a == 'C':
                result += power
            power *= 2
        
        return result    
    
    def consts(self):
        result = []
        while True:
            a = self.parser.read_codon()
            
            if a == 'C':
                result.append('I')
                
            elif a == 'F':
                result.append('C')
                
            elif a == 'P':
                result.append('F')
                
            elif a == 'IC':
                result.append('P')
                
            else:
                self.parser.unread_codon(a) #it will be later consumed in pattern()
                break
            
        return ''.join(result)
    
    def template(self):
        result = []
        parser = self.parser
        while True:
            self.item_starts.append(parser.index)
            a = parser.read_codon()
            
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
                    command += parser.read_base()
                if self.explicit_rna_items:
                    result.append(RNA_Item(command))
                else:
                    self.rna.append(command)
                
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
                print 'e[{0}] = {1}'.format(j, limit_string(dna[ee[0]: ee[1]]))
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
                r.extend(asnat(end - begin))
        return r


def test():
    for q, a in [
        ('IIPIPICPIICICIIFICCIFPPIICCFPC', 'PICFC'),
        ('IIPIPICPIICICIIFICCIFCCCPPIICCFPC', 'PIICCFCFFPC'),
        ('IIPIPIICPIICIICCIICFCFC', 'I'),
        ]:
        e = Executor(q)
        e.step()
        result = ''.join(e.dna)
        assert result == a
    print 'tests from task description passed'


if __name__ == '__main__':
    test()
    
