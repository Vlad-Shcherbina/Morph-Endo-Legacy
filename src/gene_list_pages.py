
import os

from helpers import project_path
from dna_basics import *
from dna_code import *
from genes import *



def main():
    for page in range(15):
        print page
        prefix = gene_table_page_nr.patch_prefix(asnat(page, length=24))
        
        # gene list page
        prefix += guide_page_prefix(42)
         
        create_and_run_prefix(prefix, 'data/guide/genelist/{0:02}'.format(page))
        
        
if __name__ == '__main__':
    main()