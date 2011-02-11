
from time import clock
import sys
import argparse
import cProfile

try:
    import psyco
    psyco.full()
except ImportError:
    pass

from Executor import Executor, FinishException
   



endo_file_name = '../data/endo.dna'    
             

def test():
    # tests from task description
    for q, a in [
        ('IIPIPICPIICICIIFICCIFPPIICCFPC', 'PICFC'),
        ('IIPIPICPIICICIIFICCIFCCCPPIICCFPC', 'PIICCFCFFPC'),
        ('IIPIPIICPIICIICCIICFCFC', 'I'),
        ]:
        e = Executor(q)
        e.step()
        result = ''.join(e.dna)
        #print result
        assert result == a
    
    
def generate_trace():
    endo = open(endo_file_name).read()
    e = Executor(endo)
    
    e.debug = True
    for i in range(10):
        e.step()
        
        
def stats_run(n_steps=0):        
    endo = open(endo_file_name).read()
    
#    prefix = 'IIPIFFCPICICIICPIICIPPPICIIC'
    prefix = ''
    
    e = Executor(prefix+endo)
    #e.debug = True
    
    start = clock()
    try:
        for i in xrange(2*10**9):
            if i > 0 and i%1000 == 0:
                print i, int(i/(clock()-start+1e-6)),'steps/s'
            e.step()
            n_steps -= 1
            if n_steps == 0: break
    except FinishException:
        print 'execution finished'
    finally:
        print e.iteration, 'iterations'
        print len(e.rna), 'rna produced'
        print 'it took', clock()-start
        print int(e.iteration/(clock()-start+1e-6)), 'iterations/s'
        print 'pattern freqs', e.pattern_freqs
        print 'template freqs', e.template_freqs
        print 'codon len freqs', e.codon_len_freqs
            
            
def main():
    test()
    
    endo = open(endo_file_name).read()
    
    prefix_file, = sys.argv[1:]
    
    prefix = open(prefix_file+'.dna').read()
    
    rna = open(prefix_file+'.rna', 'w')
    
    e = Executor(prefix+endo)
    
    start = clock()
    
    for r in e.obtain_rna():
        print>>rna, r
    
    print 'it took', clock()-start
    print int(e.iteration/(clock()-start+1e-6)), 'iterations/s'
    
    rna.close()

        
    
if __name__ == '__main__':
    #main()
    test()
    cProfile.run('stats_run(10000)', 'profile')
    #generate_trace()
    