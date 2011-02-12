# unsorted shit

def limit_string(s, maxlen=10):
    if len(s) <= maxlen:
        return ''.join(s)
    return '{0}... ({1} bases)'.format(''.join(s[:maxlen]), len(s))

   
