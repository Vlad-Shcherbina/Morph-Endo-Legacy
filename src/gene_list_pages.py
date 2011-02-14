
import os

from helpers import project_path
from dna_basics import *
from dna_code import *



def main():

    for page in range(15):
        print page
        pattern = [
            open_paren,
            Search(green_zone_marker),
            Skip(0x510-len(green_zone_marker)),
            close_paren,
            Skip(24),
            ]
        template = \
            [Reference(0, 0)]+\
            map(Base, asnat(page, length=24))
            
        items = pattern+[close_paren]+template+[close_paren]
        prefix = ''.join(i.to_dna() for i in items)
        
        # prefix to show genelist page
        prefix += 'IIPIFFCPICFPPICIICCCCCCCIICIPPPCFCFCFIIC'
         
        file_name = project_path('data/guide/genelist/{0:02}'.format(page))
        with open(file_name+'.dna', 'w') as fout:
            fout.write(prefix)
        
        os.system(project_path('scripts\\exec_build.bat')+' '+file_name)
        
        
if __name__ == '__main__':
    main()