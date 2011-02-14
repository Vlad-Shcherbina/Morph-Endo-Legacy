# stuff related to contents of DNA

import os
import re

from helpers import project_dir

__all__ = [
    'endo',
    'protect',
    'asnat',
    ]


endo_file_name = os.path.join(project_dir, 'data/endo.dna')
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

def consts(dna):
    for base in dna:
        if base == 'I':
            try:
                nextbase = dna.next()
            except StopIteration:
                return
            if nextbase == 'C':
                yield 'P'
            else:
                return
        else:
            yield {'C':'I', 'F':'C', 'P':'F'}[base]

def nat(dna):
    result = 0
    power = 1
    for base in dna:
        if base == 'P':
            yield result
            result = 0
            power = 1
        elif base == 'C':
            result += power
        power *= 2
        

def show_pattern_and_template(dna):
    from executor import Executor

    e = Executor(dna)
    e.explicit_rna_items = True
    
    pattern = e.pattern()
    pattern.append('EoP')
    template = e.template()
    template.append('EoT')
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
    
    
def adapter():
    # see fieldrepairing
    adapter_signature = 'IFPICFPPCCC'
    m1, m2 = re.finditer(adapter_signature, endo())
    adapter = endo()[m1.end():m2.start()]
    return adapter


# blue zone starts after it
blue_zone_marker = 'IFPICFPPCFIPP'

    
if __name__ == '__main__':
    
    #print 'precheck:'
    #prefix = open('../data/precheck.dna').read()
    #show_pattern_and_template(prefix+endo())

    prefix = adapter()+asnat(123)+asnat(456)
    show_pattern_and_template(prefix+endo())
        
