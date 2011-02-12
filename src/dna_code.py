# stuff related to contents of DNA


__all__ = [
    'endo',
    'protect',
    'asnat',
    ]


endo_file_name = '../data/endo.dna'
_endo = None
def endo():
    global _endo
    if _endo is None:
        _endo = open(endo_file_name).read()
    return _endo


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

def show_pattern_and_template(dna):
    #it's buggy and shit
    from Executor import Executor
    from items import TerminationItem
    e = Executor(dna)
    e.explicit_rna_items = True
    
    pattern = e.pattern()
    pattern.append(TerminationItem())
    template = e.template()
    template.append(TerminationItem())
    e.item_starts.append(e.parser.index)
    
    s1 = []
    s2 = []
    for item, begin, end in zip(
                pattern+template, 
                e.item_starts, 
                e.item_starts[1:]):
        e1 = ''.join(e.dna[begin:end])
        e2 = str(item)
        if len(e1) > len(e2):
            e2 += ' '*(len(e1)-len(e2))
        else:
            e1 += ' '*(len(e2)-len(e1))
            
        s1.append(e1)
        s2.append(e2)
        
    print ' '.join(s1)
    print ' '.join(s2)
    
    
if __name__ == '__main__':
        
    prefix = open('../data/guide/navigation.dna').read()
    show_pattern_and_template(prefix+endo())
    pass