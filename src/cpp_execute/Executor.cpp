#include <iostream>

#include "Executor.h"


std::string limit_string(std::string &s, int maxlen=10)
{
	std::stringstream ss;
	if (s.size() <= maxlen)
		ss << std::string(s);
	else
	{
		ss << s.substr(0, maxlen) << "...";
	}
	ss << " (" << s.size() << " bases)";
	return ss.str();
}

std::string quote(std::string &s)
{
	std::string result;
	std::string::iterator c;
	for (c = s.begin(); c != s.end(); c++)
		switch (*c)
		{
		case 'I': result += 'C'; break;
		case 'C': result += 'F'; break;
		case 'F': result += 'P'; break;
		case 'P': result += "IC";
		}
	return result;
}

dna_type protect(dna_type* pdna, int begin, int end, int level)
{
	assert(level>=0);
	std::string i="I", c="C", f="F", p="P";
	for (int j = 0; j < level; j++)
	{
		i = c; c = f; f = p; p = quote(p);
	}

	dna_type result;
	for (int j = begin; j < end; j++)
		switch ((*pdna)[j])
		{
		case 'I': result += i; break;
		case 'C': result += c; break;
		case 'F': result += f; break;
		case 'P': result += p;
		}
	return result;
}

dna_type asnat(int n)
{
	dna_type result;
	while (n > 0)
	{
		result += (n % 2) ? 'C' : 'I';
		n /= 2;
	}
	return result;
}

Executor::Executor(dna_type* pdna, bool debug) : parser(DNAParser(pdna)), pdna(pdna), debug(debug)
{
	rna = t_rna();
	iteration = 0;
	cost = 0;
}

void Executor::step()
{
	if (debug)
	{
		std::cout << "iteration " << iteration << std::endl;
        std::cout << "dna = " << limit_string(*pdna) << std::endl;
	}

	t_pattern* p = 0;
	t_template* t = 0;
	bool execution_finished = false;
	try
	{
		p = pattern();
		if (debug)
			std::cout << "pattern  " << p->str() << std::endl;
		t = templ();
		if (debug)
			std::cout << "template " << t->str() << std::endl;
	}
	catch (FinishException& e)
	{
		execution_finished = true;
	}
	
	// finally
	int index = parser.getIndex();
	cost += index;
	//std::cout << "old dna " << (*pdna) << std::endl; // DEBUG
	pdna->erase(0, index);
	if (execution_finished)
	{
		if (p) delete p;
		if (t) delete t;
		throw FinishException();
	}

	matchreplace(p, t);
	//std::cout << "new dna " << *pdna << std::endl; // DEBUG
	parser = DNAParser(pdna);
	iteration += 1;
	delete p;
	delete t;

	if (debug)
		std::cout << "len(rna) = " << rna.size() << std::endl << std::endl;
}

t_pattern* Executor::pattern()
{
	t_pattern* result = new t_pattern;
	int lvl = 0;
	while (true)
	{
		t_codon a = parser.read_codon();
		int l = a.length();
		char c = a[l - 1];

		if ((l == 1) || ((l == 2) && (c =='C'))) // base: C, P, F or IC
			result->push_back(new IBase(a));
		else if (l == 2)
		{
			if (c == 'P') // IP
				result->push_back(new ISkip(nat()));
			else // IF
			{
				parser.read_base();
				result->push_back(new ISearch(consts()));
			}
		}
		else if (l == 3)
		{
			if (c == 'P') // IIP
			{
				lvl++;
				result->push_back(new ILParen());
			}
			else if (c == 'I') // III 
			{
				t_command command;
				for (int i = 0; i < 7; i++)
					command += parser.read_base();
				rna.push_back(command);
			}
			else // IIC or IIF
			{
				if (lvl == 0)
					return result;
				lvl--;
				result->push_back(new IRParen());
			}
		}
		else // empty codone
		{
			delete result;
			throw FinishException();
		}
	}
}

int Executor::nat()
{
	int result = 0;
	int power = 1;
	while (true)
	{
		t_base a = parser.read_base();
		if ((a == 0) || (a == 'P'))
			break;
		if (a == 'C')
			result += power;
		power *= 2;
	}
	return result;
}

std::string Executor::consts()
{
	std::string result;
	while (true)
	{
		t_codon a = parser.read_codon();
		if (a == "C")
			result += "I";
		else if (a == "F")
			result += "C";
		else if (a == "P")
			result += "F";
		else if (a == "IC")
			result += "P";
		else
		{
			parser.unread_codon(a);
			break;				
		}
	}
	return result;
}

t_template* Executor::templ()
{
	t_template* result = new t_template;
	while (true)
	{
		t_codon a = parser.read_codon();

		int l = a.length();
		char c = a[l - 1];

		if ((l == 1) || ((l == 2) && (c =='C'))) // base: C, P, F or IC
			result->push_back(new IBase(a));
		else if (l == 2) // IF or IP
		{
			int level = nat();
			int n = nat();
			result->push_back(new IReference(n, level));
		}
		else if (l == 3)
		{
			if (c == 'P') // IIP
				result->push_back(new ILength(nat()));
			else if (c == 'I') // III
			{
				t_command command;
				for (int i = 0; i < 7; i++)
					command += parser.read_base();
				rna.push_back(command);
			}
			else // IIF or IIC
				return result;
		}
		else // empty codone
		{
			delete result;
			throw FinishException();
		}
	}
}

void  Executor::matchreplace(t_pattern* p, t_template* t)
{
	t_environment e;
	int i = 0;
	std::vector<int> c;

	int j;
	std::string s;
	t_pattern::iterator pp;
	for (pp = p->begin(); pp != p->end(); pp++)
	{
		switch ((*pp)->type())
		{
		case BASE:
			cost += 1;
			if ((*pdna)[i] == dynamic_cast<IBase*>(*pp)->b)
				i++;
			else
			{
				if (debug)
					//std::cout << "failed match (base)" << std::endl;
					std::cout << "failed match" << std::endl;
				return;
			}
			break;
		case SKIP:
			i += dynamic_cast<ISkip*>(*pp)->n;
			if (i > pdna->size())
			{
				if (debug)
					//std::cout << "failed match (skip)" << std::endl;
					std::cout << "failed match" << std::endl;
				return;
			}
			break;
		case SEARCH:
			s = dynamic_cast<ISearch*>(*pp)->s;
			j = pdna->find(s, i);
			if (j != pdna->npos)
			{
				cost += j + s.size() - i;
				i = j + s.size();
			}
			else
			{
				cost += pdna->size() - i;
				if (debug)
					//std::cout << "failed match (search)" << std::endl;
					std::cout << "failed match" << std::endl;
				return;
			}
			break;
		case LPAREN:
			c.push_back(i);
			break;
		case RPAREN:
			e.push_back(env_pair(c.back(), i));
			c.pop_back();
			break;
		}
	}
	
	if (debug)
	{
		std::cout << "succesful match of length " << i << std::endl;
		t_environment::iterator ee;
		int j = 0;
		for (ee = e.begin(); ee != e.end(); ee++)
		{
			int begin, end;
			begin = ee->start;
			end = ee->end;
			std::string fragment = pdna->substr(begin, end-begin);
			std::cout << "e[" << j << "] = " << limit_string(fragment) << std::endl;
			j++;
		}
	}
	dna_type* r = replacement(t, &e);
	pdna->erase(0, i);
	pdna->insert(0, *r);
	delete r;
}

dna_type*  Executor::replacement(t_template* templ, t_environment* e)
{
	dna_type* r = new dna_type;
	int n, l, begin, end;
	t_template::iterator tt;
	for (tt = templ->begin(); tt != templ->end(); tt++)
	{
		switch ((*tt)->type())
		{
		case BASE:
			r->push_back(dynamic_cast<IBase*>(*tt)->b);
			break;
		case REFERENCE:
			n = dynamic_cast<IReference*>(*tt)->n;
			l = dynamic_cast<IReference*>(*tt)->l;
			if (n < e->size())
			{
				begin = (*e)[n].start;
				end = (*e)[n].end;
			}
			else
			{
				begin = 0;
				end = 0;
			}
			if (l == 0)
				r->append(*pdna, begin, end - begin);
			else
			{
				dna_type p = protect(pdna, begin, end, l);
				cost += p.size();
				r->append(p);
			}
			break;
		case LENGTH:
			n = dynamic_cast<ILength*>(*tt)->n;
			if (n < e->size())
			{
				begin = (*e)[n].start;
				end = (*e)[n].end;
			}
			else
			{
				begin = 0;
				end = 0;
			}
			dna_type p = asnat(end - begin);
			r->append(p);
			break;
		}
	}
	return r;
}
