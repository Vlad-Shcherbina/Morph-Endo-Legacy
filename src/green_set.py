from dna_code import endo, green_zone_marker
from dna_basics import asnat_fixed_length, nat

import sys

sizeof = {"int24" : 0x18, "int48" : 0x30, "int12" : 0x0c, "int1" : 0x01}
types = sizeof.keys()

def modify(dna, offset, type, value):
    green_begin = dna.find(green_zone_marker)
    assert(green_begin > 0)
    start = green_begin + offset
    end = start + sizeof[type]
    return dna[:start] + asnat_fixed_length(value, sizeof[type]) + dna[end:]

def get_value(dna, offset, type):
    green_begin = dna.find(green_zone_marker)
    assert(green_begin > 0)
    start = green_begin + offset
    end = start + sizeof[type]
    
    print dna[start:end]
    
    # ugly abuse of iterator-based nat()
    iter = (b for b in dna[start:end])
    nat_list = list(nat(b for b in iter))
    assert(len(nat_list) == 1)
    result = nat_list[0]
    #assert(asnat_fixed_length(result, sizeof[type]) == dna[start:end])
    return result

def print_syntax():
    print "Syntax: green_set.py OFFSET TYPE [VALUE]"
    print "Supported types: " + ", ".join(types)
    exit()

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc not in [3, 4]: print_syntax()
    
    offset, type = sys.argv[1:3]
    if type not in types: print_syntax()

    offset = int(offset, 16) if offset.lower().startswith('0x') else int(offset)

    if argc == 4:
        value = int(sys.argv[-1])
        print modify(endo(), offset, type, value)
    else:
        print get_value(endo(), offset, type)

