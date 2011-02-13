import sys

A = ord('A')
a = ord('a')

table = ''.join(map(chr,
    range(A)+
    range(A+13, A+26)+range(A, A+13)+
    range(A+26, a)+
    range(a+13, a+26)+range(a, a+13)+
    range(a+26, 256)))

for line in sys.stdin:
    sys.stdout.write(line.translate(table))