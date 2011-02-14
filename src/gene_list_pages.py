
import os

from helpers import project_path
from dna_basics import *
from dna_code import *



def main():

    for page in range(2, 3):
        print page
        prefix = gene_table_page_nr.patch_prefix(asnat(page, length=24))
        
        # prefix to show genelist page
        prefix += 'IIPIFFCPICFPPICIICCCCCCCIICIPPPCFCFCFIIC'
         
        create_and_run_prefix(prefix, 'data/guide/genelist/{0:02}'.format(page))
        
        
if __name__ == '__main__':
    main()