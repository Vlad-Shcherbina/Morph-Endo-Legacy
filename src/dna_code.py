# stuff related to contents of DNA


__all__ = [
    'endo',
    'protect',
    'asnat',
    ]


endo_file_name = '../data/endo.dna'
endo = open(endo_file_name).read()


def protect(dna, level):
    assert level >= 0
    m = {'I': 'C', 'C': 'F', 'F': 'P', 'P': 'IC'}
    a = ['I']
    for i in range(level+3):
        a.append(''.join(map(m.get, a[-1])))
        
    m = dict(zip('ICFP', a[-4:]))
    return ''.join(map(m.get, dna))
 
            
def asnat(n):
    r = []
    while n > 0:
        r.append('IC'[n%2])
        n //= 2
    r.append('P')
    return ''.join(r)

    
    
if __name__ == '__main__':

        
    #prefix = open('../data/guide/navigation.dna').read()
    #show_pattern_and_template(prefix+endo)
    pass