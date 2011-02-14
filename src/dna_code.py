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
    return ' '.join(i.to_dna() for i in items)
    
    
def put_to_blue_prefix(data):
    pattern = [
        open_paren,
        Search(blue_zone_marker),
        close_paren,
        ]
    template = \
        [Reference(0, 0)]+\
        map(Base, data)
    items = pattern+[close_paren]+template+[close_paren]
    return ' '.join(i.to_dna() for i in items)
    
    
Gene = namedtuple('Gene', 'offset size')
class Gene(Gene):
    def content(self):
        green_start = endo().find(green_zone_marker)
        return endo()[green_start+self.offset:green_start+self.offset+self.size]
    
    def patch_prefix(self, new_content):
        assert len(new_content) == self.size
        pattern = [
            open_paren,
            Search(green_zone_marker),
            Skip(self.offset-len(green_zone_marker)),
            close_paren,
            Skip(self.size),
            ]
        template = \
            [Reference(0, 0)]+\
            map(Base, new_content)
            
        items = pattern+[close_paren]+template+[close_paren]
        return ''.join(i.to_dna() for i in items)        


apple = Gene(0x65F785, 0x0003FB)
mlephant = Gene(0x5B427d, 0x002811)
do_self_check = Gene(0x000058, 1) # that self check from the beginning
gene_table_page_nr = Gene(0x00510, 0x00018)
font_table_dots = Gene(0x0A1AC3, 0x002400)
font_table_cyperus = Gene(0x033965, 0x002400)


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

    
if __name__ == '__main__':
    
    #print 'precheck:'
    #prefix = open('../data/precheck.dna').read()
    #show_pattern_and_template(prefix+endo())

    #prefix = adapter()+asnat(123)+asnat(456)
    prefix = open(project_path('data/sun.dna')).read()
    show_pattern_and_template(prefix+endo())

    #print put_to_blue_prefix('ICICIIIIIIIIIIP')
    #print put_to_blue_prefix('F')
    #p = ''
    #p += put_to_blue_prefix(asnat(250, length=24)*3)
    #p += gene_activation_prefix(apple)
    #print p.replace(' ', '')
    
    #print do_self_check.content()
    #create_and_run_prefix(do_self_check.patch_prefix('P')+'')
    create_and_run_prefix(
        font_table_dots.patch_prefix(font_table_cyperus.content())+
        guide_page_prefix(10646),
        'data/guide/true_charset'
        )
            