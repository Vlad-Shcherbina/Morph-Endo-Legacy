# higher level stuff related to contents of DNA

import os
import re
from collections import namedtuple

from helpers import project_path
from dna_basics import *


endo_file_name = project_path('data/endo.dna')
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
    
    
    
# blue zone starts after it
blue_zone_marker = 'IFPICFPPCFIPP'

green_zone_marker = 'IFPICFPPCFFPP'
    
    
adapter_signature = 'IFPICFPPCCC'
def adapter():
    m1, m2 = re.finditer(adapter_signature, endo())
    adapter = endo()[m1.end():m2.start()]
    return adapter

def gene_activation_prefix(gene):
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
        map(Base, asnat(gene.offset))+\
        map(Base, asnat(gene.size))+\
        [Reference(1, 0)]
    
    items = pattern+[close_paren]+template+[close_paren]
    return ''.join(i.to_dna() for i in items)
    
    
def push_to_blue_prefix(data):
    pattern = [
        open_paren,
        Search(blue_zone_marker),
        close_paren,
        ]
    template = \
        [Reference(0, 0)]+\
        map(Base, data)
    items = pattern+[close_paren]+template+[close_paren]
    return ''.join(i.to_dna() for i in items)
    

def create_and_run_prefix(prefix, path):
    file_name = project_path(path)
    with open(file_name+'.dna', 'w') as fout:
        fout.write(prefix)
    
    os.system(project_path('scripts\\exec_build.bat')+' '+file_name)

    
def guide_page_prefix(n):
    s = bin(n)[2:]
    s = s[::-1]
    s = s.replace('0', 'C').replace('1', 'F')
    s = 'IIP IFFCPICFPPIC IIC {0} IIC IPPP {1} IIC'.format('C'*len(s),s)
    return s.replace(' ','')

    
def test():
    # examples from fieldrepairing
    import genes
    assert gene_activation_prefix(genes.Gene(1234, 500)) == \
        'IIPIFFCPICCFPICICFFFIIPIFFCPICCFPICICFFFIICIICIICIPPPCFCCFCFFCCFI'+\
        'CCCFCFFFFFICIPPCPIIC'
    assert push_to_blue_prefix(asnat(42, length=24)) == \
        'IIPIFFCPICCFPICICFPCICICIICIICIPPPCFCFCFCCCCCCCCCCCCCCCCCICIIC'
    assert push_to_blue_prefix('F') == \
        'IIPIFFCPICCFPICICFPCICICIICIICIPPPPIIC'
        
    
if __name__ == '__main__':
    test()
    #create_and_run_prefix(guide_page_prefix(23), 'data/guide/activating_genes_encrypted')
    
    import genes
    prefix = ''
    #prefix += push_to_blue_prefix(genes.vmu_code_purchase_code.content())
    #prefix += gene_activation_prefix(genes.help_beautiful_numbers)
    #create_and_run_prefix(prefix, 'data/hbn')
    prefix += gene_activation_prefix(genes.contest1998)
    create_and_run_prefix(prefix, 'data/contest1998')
    pass
            