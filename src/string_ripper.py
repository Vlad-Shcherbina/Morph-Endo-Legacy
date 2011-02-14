import string_code
import dna_code
import sys

if __name__ == "__main__":
    command = sys.argv[1]

    endo = dna_code.endo();

    if command == 'offset':
        offset = int(sys.argv[2])
        print string_code.extract_from_offset(endo, offset)
    elif command == 'prefix':
        prefix = sys.argv[2]
        (offset, substring) = string_code.extract_from_prefix(endo, prefix)
        if offset > 0:
            print "at", str(offset) + ":"
            print substring
        else:
            print "Nothing found."
    else:
        print "Syntax: string_ripper.py ( offset | prefix ) ARGUMENT"
