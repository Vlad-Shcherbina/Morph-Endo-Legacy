#include <iostream>
#include <sstream>

#include "Executor.h"
#include "kmp.h"

const int DEFRAGMENTATION_FREQUENCY = 2000000;

/* output formatters */

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

std::string limit_string(dna_type pdna, int maxlen=10)
{
	std::stringstream ss;
	if (pdna->length() <= maxlen)
		ss << pdna->as_string();
	else
	{
		ss << pdna->slice(0, maxlen)->as_string() << "...";
	}
	ss << " (" << pdna->length() << " bases)";
	return ss.str();
}

/* end output formatters */


/* DNA coding */

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

dna_type protect(dna_type pdna, int level)
{
	assert(level>=0);
	std::string i="I", c="C", f="F", p="P";
	for (int j = 0; j < level; j++)
	{
		i = c; c = f; f = p; p = quote(p);
	}
	
	std::string result;
	dna_iter iter = Iterator(pdna);
	while (iter.valid)
	{
		switch (iter.current())
		{
		case 'I': result += i; break;
		case 'C': result += c; break;
		case 'F': result += f; break;
		case 'P': result += p;
		}
		iter.advance();
	}
	return new Leaf(result);
}

dna_type asnat(int n)
{
	std::string result;
	while (n > 0)
	{
		result += (n % 2) ? 'C' : 'I';
		n /= 2;
	}
	result += 'P';
	return new Leaf(result);
}

/* end DNA coding */

Executor::Executor(dna_type pdna, bool debug) : parser(DNAParser(pdna)), pdna(pdna), debug(debug)
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
        std::cout << "dna = " << limit_string(pdna) << std::endl;
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
	
	//pdna->erase(0, index);
	pdna = pdna->slice(index, pdna->length());
	if (execution_finished)
	{
		if (p) delete p;
		if (t) delete t;
		throw FinishException();
	}

	matchreplace(p, t);

	if ((iteration+1)%DEFRAGMENTATION_FREQUENCY == 0) {
		std::string dna;
		pdna->accumulate_string(dna);
		pdna = new Leaf(dna);
	}


	parser = DNAParser(pdna);

	iteration += 1;
	delete p;
	delete t;

	if (debug) {
		std::cout << "len(rna) = " << rna.size() << std::endl << std::endl;
	}
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
				result->push_back(new ISkip(parser.nat()));
			else // IF
			{
				parser.read_base();
				result->push_back(new ISearch(parser.consts()));
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
			int level = parser.nat();
			int n = parser.nat();
			result->push_back(new IReference(n, level));
		}
		else if (l == 3)
		{
			if (c == 'P') // IIP
				result->push_back(new ILength(parser.nat()));
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
	dna_iter iter = Iterator(pdna);
	std::vector<int> c;

	int j, n;
	std::string s;
	t_pattern::iterator pp;
	for (pp = p->begin(); pp != p->end(); pp++)
	{
		switch ((*pp)->type())
		{
		case BASE:
			cost += 1;
			if (iter.current() == static_cast<IBase*>(*pp)->b)
			{
				i++;
				iter.advance();
			}
			else
			{
				if (debug)
					//std::cout << "failed match (base)" << std::endl;
					std::cout << "failed match" << std::endl;
				return;
			}
			break;
		case SKIP:
			n = static_cast<ISkip*>(*pp)->n;
			i += n;
			if (i > pdna->length())
			{
				if (debug)
					//std::cout << "failed match (skip)" << std::endl;
					std::cout << "failed match" << std::endl;
				return;
			}
			else
				iter.advance(n);
			break;
		case SEARCH:
			s = static_cast<ISearch*>(*pp)->s;
			j = kmp_search(pdna, s, i);
			if (j != pdna->length())
			{
				int delta = j + s.size() - i;
				cost += delta;
				i += delta;
				iter.advance(delta);
			}
			else
			{
				cost += pdna->length() - i;
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
			dna_type fragment = pdna->slice(begin, end);
			std::cout << "e[" << j << "] = " << limit_string(fragment) << std::endl;
			j++;
		}
	}
	dna_type r = replacement(t, &e);
	//pdna->erase(0, i);
	//pdna->insert(0, *r);
	pdna = pdna->slice(i, pdna->length());
	pdna = r->concat_with(pdna);
}

dna_type  Executor::replacement(t_template* templ, t_environment* e)
{
	dna_type r = new Leaf("");

	int n, l, begin, end;
	char base;

	std::string base_buffer;

	t_template::iterator tt;
	for (tt = templ->begin(); tt != templ->end(); tt++)
	{
		if (((*tt)->type() != BASE) && !base_buffer.empty())
		{
			// flush buffer
			r = r->concat_with(new Leaf(base_buffer));
			base_buffer = "";
		}
		switch ((*tt)->type())
		{
		case BASE:
			base = static_cast<IBase*>(*tt)->b;
			//r = r->concat_with(new Leaf(base));
			base_buffer += base;
			break;
		case REFERENCE:
			n = static_cast<IReference*>(*tt)->n;
			l = static_cast<IReference*>(*tt)->l;
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
			{
				r = r->concat_with(pdna->slice(begin, end));
			}
			else
			{
				dna_type p = protect(pdna->slice(begin, end), l);
				cost += p->length();
				r = r->concat_with(p);
			}
			break;
		case LENGTH:
			n = static_cast<ILength*>(*tt)->n;
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
			r = r->concat_with(asnat(end - begin));
			break;
		}
	}
	// flush buffer
	if (!base_buffer.empty())
		r = r->concat_with(new Leaf(base_buffer));
	return r;
}

void Executor::dump_registers()
{
	DNAParser p(pdna);

	std::stringstream ss;
	
	
	int AAA_geneTablePageNr = p.get_green_int(0x510),
		__array_index = p.get_green_int(0xc4589),
		__array_value = p.get_green_int(0xc45a1),
		__int12 = p.get_green_int(0xc4628),
		__int12_2 = p.get_green_int(0xc4634),
		__int24 = p.get_green_int(0xc45eb),
		__int24_2 = p.get_green_int(0xc4603),
		__int3 = p.get_green_int(0xc4625),
		__int48 = p.get_green_int(0xc4640),
		__int9 = p.get_green_int(0xc461c);
	

	ss << "AAA_geneTablePageNr = " << AAA_geneTablePageNr << ", " << std::endl;
	ss << "__array_index = " << __array_index << ", ";
	ss << "__array_value = " << __array_value << ", " << std::endl;
	ss << "__int12 = " << __int12 << ", ";
	ss << "__int12_2 = " << __int12_2 << ", " << std::endl;
	ss << "__int24 = " << __int24 << ", ";
	ss << "__int24_2 = " << __int24_2 << ", " << std::endl;
	ss << "__int3 = " << __int3 << ", ";
	ss << "__int48 = " << __int48 << ", ";
	ss << "__int9 = " << __int9 << std::endl;

	std::cout << ss.str();
}
