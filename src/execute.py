
from time import clock
import sys
import argparse
import cProfile


try:
    import psyco
    psyco.full()
except ImportError:
    pass

from executor import Executor, FinishException
from dna_code import endo
  


def generate_trace(n_steps=10):
    e = Executor(endo())
    
    e.debug = True
    for i in range(n_steps):
        e.step()
        
        
def stats_run(n_steps=0):        
    e = Executor(endo())
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
    parser = argparse.ArgumentParser(description='Produce RNA from DNA')
    parser.add_argument('--trace', action='store_true')
    parser.add_argument('--pause', action='store_true')
    parser.add_argument('prefix_filename')
    
    args = parser.parse_args()
    prefix_filename = args.prefix_filename
    
    prefix = open(prefix_filename+'.dna').read().strip()
    
    assert all(c in 'ICFP' for c in prefix)
        
    e = Executor(prefix+endo())
    e.debug = args.trace or args.pause
    
    start = clock()
    
    #for r in e.obtain_rna():
    #    print>>rna, r
    try:
        while True:
            e.step()
            if args.pause:
                print 'press enter',
                raw_input()
    except FinishException:
        pass

    rna_file = open(prefix_filename+'.rna', 'w')
    for r in e.rna:
        print>>rna_file, r
    
    print 'it took', clock()-start
    print int(e.iteration/(clock()-start+1e-6)), 'iterations/s'
    
    rna_file.close()

    
if __name__ == '__main__':
	#generate_trace(25)
	#main()
    #test()
    #stats_run()
    main()
    #cProfile.run('stats_run(10000)', 'profile')
    #generate_trace()
    
