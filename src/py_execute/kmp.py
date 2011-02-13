## {{{ http://code.activestate.com/recipes/117214/ (r1)
# Knuth-Morris-Pratt string matching
# David Eppstein, UC Irvine, 1 Mar 2002

# modified a little

from __future__ import generators

def find(text, pattern, start=0, end=None):

    '''Yields all starting positions of copies of the pattern in the text.
Calling conventions are similar to string.find, but its arguments can be
lists or iterators, not just strings, it returns all matches, not just
the first one, and it does not need the whole text in memory at once.
Whenever it yields, it will have read the text exactly up to and including
the match that caused the yield.

    # TODO: describe my modification (how it requires random access with nonzero start)
    '''

    # allow indexing into pattern and protect against change during yield
    pattern = list(pattern)
    len_pattern = len(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift

    # do the actual search
    startPos = start
    matchLen = 0

    iterable = text
    if start != 0:
        iterable = (text[i] for i in xrange(start, len(text)))

    cnt = 0
    for c in iterable:
        if end is not None and start+cnt >= end:
            break
        #print startPos
        while matchLen == len_pattern or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len_pattern:
            yield startPos
        cnt += 1
## end of http://code.activestate.com/recipes/117214/ }}}


if __name__ == '__main__':
    print list(find('abracadabra', 'ab'))