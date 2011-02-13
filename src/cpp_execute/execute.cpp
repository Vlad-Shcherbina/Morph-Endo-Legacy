#include <iostream>
#include <fstream>
#include <time.h>

#include "DNAParser.h"
#include "Executor.h"
#include "treap_rope.h"

using namespace std;

const std::string endo_file_name = "..\\data\\endo";

dna_type read_dna(std::string fname)
{
	ifstream f;
	f.exceptions(ifstream::badbit | fstream::failbit);
	std::string result_string;
	try {
		f.open (fname + ".dna", ios::in);
		f.exceptions(ifstream::badbit);
		f >> result_string;
	}
	catch (ifstream::failure e)
	{
		std::cout << "Can't open " << fname << ".dna" << std::endl;
		throw e;
	}
	f.close();
	std::cout << "Read " << fname  << ".dna" << std::endl;
	return new Leaf(result_string);
}

/*
dna_type endo()
{
	return read_dna(endo_file_name);
}

void trace(int steps=10)
{
	Executor e = Executor(endo(), true);
	for(int i = 0; i < steps; i++)
		e.step();
}

void stats_run(int n_steps=2000000000)
{
	std::string prefix;
	//prefix = "IIPIFFCPICICIICPIICIPPPICIIC";
	prefix = "";
    
	dna_type pdna = (new Leaf(prefix))->concat_with(endo());
	
	Executor e = Executor(pdna);
    
	clock_t start = clock();
	try
	{
		for (int i = 0; i < n_steps; i++)
		{
			if ((i > 0) && (i%10000 == 0))
			{
				clock_t elapsed = clock() - start;
				//std::cout<<"rope depth "<<e.pdna->depth()<<std::endl;
				std::cout <<  i << " " << ((i/(clock()-start+(1e-6)))*CLOCKS_PER_SEC) << " steps/s" << std::endl;
				std::cout << node_count << " nodes total"<<std::endl;
			}
			e.step();
		}
	}
	catch (FinishException& e)
	{
		std::cout << "execution finished" << std::endl;
	}
}
*/
void run(std::string prefix_file_name)
{
	dna_type endo, prefix;
	try {
		endo = read_dna(endo_file_name);
		prefix = read_dna(prefix_file_name);
	}
	catch (ifstream::failure e)	{
		return;
	}

	ofstream rna_file;
	rna_file.exceptions(ifstream::badbit | fstream::failbit);
	try {
		rna_file.open(prefix_file_name + ".rna", ios::out);
	}
	catch (ifstream::failure e)
	{
		std::cout << "Can't open " <<  prefix_file_name << ".rna for writing" << std::endl;
		return;
	}
	

	dna_type dna = prefix->concat_with(endo);
	Executor e(dna);

	clock_t start = clock();
	try
	{
		for (int i = 0; true; i++)
		{
			if ((i > 0) && (i%10000 == 0))
			{
				std::cout <<  i << " " << int((i/(clock()-start+(1e-6)))*CLOCKS_PER_SEC) << " steps/s" << std::endl;
			}
			e.step();
		}
	}
	catch (FinishException& e)
	{
		std::cout << "Execution finished" << std::endl;
	}
	std::cout << "Total time: " << double(clock()-start)/CLOCKS_PER_SEC << " seconds" << std::endl;

	
	try {
		e.dump_rna(rna_file);
	}
	catch (ifstream::failure e)
	{
		std::cout << "Error writing to " <<  prefix_file_name << ".rna" << std::endl;
		return;
	}
	rna_file.close();
}

int main(int argc, char** argv)
{
	if (argc != 2)
	{
		std::cout << "Syntax: execute PREFIX_NAME" << std::endl;
		return 1;
	}

	run(argv[1]);
	return 0;

	//trace(100);
	//stats_run(1000000);
}
