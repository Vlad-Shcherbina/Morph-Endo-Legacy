"""
Usage:
    guide_page_prefix.py <page number>
"""


import sys

def page_prefix(n):
    s = bin(n)[2:]
    s = s[::-1]
    s = s.replace('0', 'C').replace('1', 'F')
    s = 'IIP IFFCPICFPPIC IIC {} IIC IPPP {} IIC'.format('C'*len(s),s)
    return s.replace(' ','')


if len(sys.argv) != 2:
    print __doc__
    exit()
    
sys.stdout.write(page_prefix(int(sys.argv[1])))

