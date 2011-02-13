import sys
import argparse

draw_commands = {
    'PIPIIIC': 'black',
    'PIPIIIP': 'red',
    'PIPIICC': 'green',
    'PIPIICF': 'yellow',
    'PIPIICP': 'blue',
    'PIPIIFC': 'magenta',
    'PIPIIFF': 'cyan',
    'PIPIIPC': 'white',
    'PIPIIPF': 'transparent',
    'PIPIIPP': 'opaque',
    'PIIPICP': 'clear',
    'PIIIIIP': 'move',
    'PCCCCCP': 'counter clockwise',
    'PFFFFFP': 'clockwise',
    'PCCIFFP': 'mark',
    'PFFICCP': 'line',
    'PIIPIIP': 'fill',
    'PCCPFFP': 'add bitmap',
    'PFFPCCP': 'compose',
    'PFFICCF': 'clip',
    }


return_rna = 'CFPICFP'
weird_rna = {
    return_rna: 'return',
    'CCICIPC': 'hz',
    'CPICCCI': 'put_string',
    'CIIIPPC': 'put_char',
    'CIIPIIC': 'background gradient?',
    'CIIIICC': 'draw_line',
    'CPIPIIC': 'background_lambda',         
    }


all_rna_codes = {}
all_rna_codes.update(draw_commands)
all_rna_codes.update(weird_rna)


def main():
    parser = argparse.ArgumentParser(description='Decode rna commands')
    parser.add_argument('--draw', action='store_true')
    parser.add_argument('--weird', action='store_true')
    parser.add_argument('--unknown', action='store_true')
    parser.add_argument('rna_file')
    
    args = parser.parse_args()
    filename = args.rna_file+'.rna'
    
    unknown_index = {}
    
    indent = 0
    
    with open(filename) as fin:
        for rna in fin:
            rna = rna.strip()
            if rna in draw_commands:
                if args.draw:
                    print ' '*indent, draw_commands[rna]
            elif rna in weird_rna:
                if rna == return_rna:
                    indent -= 4
                if args.weird:
                    print ' '*indent, weird_rna[rna]
            else:
                if args.unknown:
                    if rna not in unknown_index:
                        unknown_index[rna] = len(unknown_index)
                    print ' '*indent, rna, '(', unknown_index[rna], ')'
            
            if rna not in draw_commands and rna != return_rna:
                indent += 4


if __name__ == '__main__':
    main()