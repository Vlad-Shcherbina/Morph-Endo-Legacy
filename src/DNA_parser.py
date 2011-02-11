from blist import blist

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

class DNA_parser(object):
    def __init__(self, dna, freqs):
        assert isinstance(dna, dna_type)
        self.dna = dna
        self.dna_len = len(self.dna)
        self.index = 0  # needed outside the parser
        self.iter = iter(self.dna)
        self.saved_codon = None
        self.pattern_freqs, self.template_freqs, self.codon_len_freqs = freqs
     
    def read_base(self):
        '''return base or empty string in case of EOF'''
        assert self.saved_codon is None #because of the structure of the parser
        if self.index == self.dna_len:
            return ''
        self.index += 1
        return self.iter.next()
    
    def read_codon(self):
        '''return "", C, F, P, IC, IF, IP, IIC, IIF, IIP or III'''
        # it turned out to be useful for parsing pattern, template and consts
        if self.saved_codon is not None:
            result = self.saved_codon
            self.saved_codon = None
            return result
        
        dna = self.dna
        bases_left = self.dna_len - self.index
        max_len = bases_left if bases_left < 3 else 3 # faster than min
            
        codon = ''    
        codon_len = 0
        while codon_len < max_len:
            base = self.iter.next()
            codon_len += 1
            codon += base
            if base != 'I':
                break
               
        self.index += codon_len
        
        self.codon_len_freqs[codon_len] += 1
        return codon
    
    def unread_codon(self, codon):
        assert self.saved_codon is None
        self.saved_codon = codon