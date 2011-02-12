#include <iostream>
#include <fstream>
#include <time.h>

#include "DNAParser.h"
#include "Executor.h"

using namespace std;

void test_parser(string s)
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
}

void test_executor(string s)
{
	try {
	Executor e = Executor(&s);
	e.step();
	}
	catch (FinishException) {}
}

void trace()
{
	ifstream endo;
	endo.open ("endo.dna", ios::in);
	string dna;
	endo >> dna;
	endo.close();
	Executor e = Executor(&dna, true);
	for(int i = 0; i < 10; i++)
		e.step();
}

void stats_run(int n_steps=2000000000)
{
	ifstream endo;
	endo.open ("endo.dna", ios::in);
    
	dna_type prefix, dna;

	endo >> dna;
	endo.close();

	//prefix = "IIPIFFCPICICIICPIICIPPPICIIC";
	prefix = "";
    
	dna_type complete_dna = prefix + dna;

	Executor e = Executor(&complete_dna);
    
	clock_t start = clock();
	try
	{
		for (int i = 0; i < n_steps; i++)
		{
			if ((i > 0) && (i%10 == 0))
				std::cout <<  i << " " << int((i/(clock()-start+1e-6))*CLOCKS_PER_SEC) << "steps/s" << std::endl;
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
	//trace();
	stats_run();
}
