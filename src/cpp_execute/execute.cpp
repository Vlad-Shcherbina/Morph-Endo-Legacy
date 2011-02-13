#include <iostream>
#include <fstream>
#include <time.h>

#include "DNAParser.h"
#include "Executor.h"
//#include "treap_rope.h"

using namespace std;

/*void test_parser(string s)
{
	cout << s << endl;
	DNAParser p = DNAParser(&s);
	t_base b = p.read_base();
	while (b)
	{
		cout << b << ' ';
		b = p.read_base();
	}
	cout << endl;
	p = DNAParser(&s);
	t_codon c = p.read_codon();
	while (c != "")
	{
		cout << c << ' ';
		c = p.read_codon();
	}
	cout << endl;
}*/

void test_executor(string s)
{
	try {
		Executor e = Executor(new Leaf(s));
		e.step();
		e.dump_dna();
	}
	catch (FinishException) {}
}


dna_type* endo()
{
	ifstream endo;
	endo.open ("endo.dna", ios::in);
    
	std::string endo_string;

	endo >> endo_string;
	endo.close();
	
	return new Leaf(endo_string);
}

void trace(int steps=10)
{
	Executor e = Executor(endo(), true);
	for(int i = 0; i < steps; i++) {
		e.step();
		//cin>>*new string();
	}
}

void stats_run(int n_steps=2000000000)
{
	std::string prefix;
	//prefix = "IIPIFFCPICICIICPIICIPPPICIIC";
	prefix = "";
    
	dna_type* pdna = (new Leaf(prefix))->concat_with(endo());
	
	Executor e = Executor(pdna);
    e.step();
	clock_t start = clock();
	try
	{
		for (int i = 0; i < n_steps; i++)
		{
			if ((i > 0) && (i%10 == 0))
			{
				clock_t elapsed = clock() - start;
				std::cout <<  i << " " << ((i/(clock()-start+(1e-6)))*CLOCKS_PER_SEC) << " steps/s" << std::endl;
			}
			e.step();
		}
	}
	catch (FinishException& e)
	{
		std::cout << "execution finished" << std::endl;
	}
	/*
        print e.iteration, 'iterations'
        print len(e.rna), 'rna produced'
        print 'it took', clock()-start
        print int(e.iteration/(clock()-start+1e-6)), 'iterations/s'
        print 'pattern freqs', e.pattern_freqs
        print 'template freqs', e.template_freqs
        print 'codon len freqs', e.codon_len_freqs
	*/
}

int main()
{
	//test_executor("IIPIPICPIICICIIFICCIFPPIICCFPC");
	//test_executor("IIPIPICPIICICIIFICCIFCCCPPIICCFPC");
	//test_executor("IIPIPIICPIICIICCIICFCFC");
	trace(100);
	//stats_run();
	//test();
}
