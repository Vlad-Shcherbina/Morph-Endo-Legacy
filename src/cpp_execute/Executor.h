#include <string>
#include <vector>
#include <exception>
#include <ostream>

#include "DNAParser.h"
#include "Item.h"

struct item_container : public std::vector<Item*>
{
	~item_container()
	{
		item_container::iterator ii;
		for (ii = begin(); ii != end(); ii++)
			delete *ii;
	}
	std::string str()
	{
		item_container::iterator ii;
		std::string result;
		for (ii = begin(); ii != end(); ii++)
			result += (*ii)->str();
		return result;
	}
};

struct env_pair
{
	int start, end;
	env_pair(int start, int end) : start(start), end(end) {}
};

typedef item_container t_pattern;
typedef item_container t_template;
typedef std::vector<env_pair> t_environment;

typedef std::string t_command;
typedef std::vector<t_command> t_rna;

class FinishException : std::exception {};

class Executor
{
public:
	dna_type pdna;
	DNAParser parser;
	t_rna rna;
	int iteration;
	int cost;
	bool debug;

	t_pattern* pattern();
	int nat();
	std::string consts();
	t_template* templ();
	void matchreplace(t_pattern* p, t_template* t);
	dna_type replacement(t_template* t, t_environment* e);

	public:
	Executor(dna_type pdna, bool debug=false);
	void dump_rna(std::ostream &o) {
		for (t_rna::iterator ii = rna.begin(); ii != rna.end(); ii++)
			o << *ii << std::endl;
	};
	void dump_dna() { std::cout << pdna->as_string() << std::endl; }
	void step();
};
