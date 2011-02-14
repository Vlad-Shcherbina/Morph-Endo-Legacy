import string_code
import dna_code
import sys

if __name__ == "__main__":
#    offset = int(sys.argv[1])
#    endo = dna_code.endo();
#    print string_code.get_string(endo, offset)
    prefix = sys.argv[1]
    endo = dna_code.endo();
    found = string_code.extract_from_prefix(endo, prefix)
    if found != "":
        print found
    else:
        print "Nothing found."