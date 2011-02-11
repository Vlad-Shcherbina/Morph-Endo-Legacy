
def limit_string(s, maxlen=10):
    if len(s) <= maxlen:
        return ''.join(s)
    return '{}... ({} bases)'.format(''.join(s[:maxlen]), len(s))


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