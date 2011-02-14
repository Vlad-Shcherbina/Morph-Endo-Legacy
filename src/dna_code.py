# higher level stuff related to contents of DNA

import os
import re

from helpers import project_dir
from dna_basics import *


endo_file_name = os.path.join(project_dir, 'data/endo.dna')
_endo = None
def endo():
    global _endo
    if _endo is None:
        _endo = open(endo_file_name).read()
    return _endo

     

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
    
    
adapter_signature = 'IFPICFPPCCC'
def adapter():
    m1, m2 = re.finditer(adapter_signature, endo())
    adapter = endo()[m1.end():m2.start()]
    return adapter

def gene_activation_prefix(offset, size):
    # see fieldrepairing
    pattern = [
        open_paren,
        Search(adapter_signature),
        open_paren,
        Search(adapter_signature),
        #Skip(len(adapter())+len(adapter_signature)),
        close_paren,
        close_paren,
        ]
    template = \
        [Reference(0, 0)]+\
        map(Base, asnat(offset))+\
        map(Base, asnat(size))+\
        [Reference(1, 0)]
    
    items = pattern+[close_paren]+template+[close_paren]
    return ' '.join(i.to_dna() for i in items)
    
    
# blue zone starts after it
blue_zone_marker = 'IFPICFPPCFIPP'

    
if __name__ == '__main__':
    
    #print 'precheck:'
    #prefix = open('../data/precheck.dna').read()
    #show_pattern_and_template(prefix+endo())

    #prefix = adapter()+asnat(123)+asnat(456)
    prefix = open(os.path.join(project_dir, 'data/sun.dna')).read()
    show_pattern_and_template(prefix+endo())

    print gene_activation_prefix(1234, 500)
        