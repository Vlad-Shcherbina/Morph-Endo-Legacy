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
    

def overwrite_green_prefix(offset, new_data):
    """ Prefix to overwrite data in the green zone. """
    length = len(new_data) # the green zone is unchanging in size
    pattern = [
        open_paren,
        Search(green_zone_marker),
        Skip(offset - len(green_zone_marker)),
        close_paren,
        Skip(length)
        ]
    template = \
        [Reference(0, 0)]+\
        map(Base, new_data)
    items = pattern+[close_paren]+template+[close_paren]
    return ''.join(i.to_dna() for i in items)

def green_set_bool_prefix(offset, value=True):
    new_gene = 'P' if value else 'F'
    return overwrite_green_prefix(offset, new_gene)     

def nop(length):
    if length == 0: return ""
    if length % 2 == 0:
        m = (length - 6) / 2
    else:
        m = (length - 6 - 3) / 2
    assert (m >= 0)
    pattern = [ Base('C') ] * m
    if length % 2 != 0:
        pattern += [ Skip(0) ]
    template = [Base('C')] * m
    items = pattern+[close_paren]+template+[close_paren]
    return ''.join(i.to_dna() for i in items)

def replace_procedure_prefix(target, source, prefix=''):
    """ Overwrite the body of procedure target with source
        padding with nop + prefix. """
    assert(source.size + len(prefix) <= target.size)
    #replacement = nop(target.size - source.size) + source.content()
    replacement = nop(target.size - source.size - len(prefix)) + prefix \
                                + source.content()
    return target.patch_prefix(replacement)

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
    
    import genes
    
    purchase_code = genes.vmu_code_purchase_code.content()
    print purchase_code
    exit()
    prefix = ''
    #prefix += genes.crack_test_value.patch_prefix(purchase_code)
    prefix += push_to_blue_prefix(purchase_code)
    prefix += gene_activation_prefix(genes.crack_key_and_print)
    create_and_run_prefix(prefix, 'data/crack')
    
    pass
            