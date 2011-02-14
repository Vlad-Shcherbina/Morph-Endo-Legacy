#include <assert.h>

#include "DNAParser.h"

DNAParser::DNAParser(dna_type pdna) : pdna(pdna), index(0), iter(Iterator(pdna))
{
	dna_len = pdna->length();
	saved_codon = "";
}

t_base DNAParser::read_base()
{
	assert(saved_codon == "");
	if (!iter.valid)
		return 0;
	t_base result = iter.current();
	iter.advance();
	index++;
	return result;
}

t_codon DNAParser::read_codon()
{
	if (saved_codon != "")
	{
		t_codon result = saved_codon;
		saved_codon = "";
		return result;
	}

	int bases_left = dna_len - index;
	int max_len = bases_left < 3 ? bases_left : 3;

	t_codon codon = "";
	int codon_len = 0;
	while (codon_len < max_len)
	{
		t_base base = iter.current();
		iter.advance();
		codon_len += 1;
		codon += base;
		if (base != 'I')
			break;
	}
	index += codon_len;
	return codon;
}

void DNAParser::unread_codon(t_codon codon)
{
	assert(saved_codon == "");
	saved_codon = codon;
}

void DNAParser::jump(int offset)
{
	assert(offset >= 0);
	assert(offset < dna_len);
	saved_codon = "";
	index = offset;
	iter = Iterator(pdna);
	iter.advance(offset);
}

int DNAParser::nat()
{
	int result = 0;
	int power = 1;
	while (true)
	{
		t_base a = read_base();
		if ((a == 0) || (a == 'P'))
			break;
		if (a == 'C')
			result += power;
		power *= 2;
	}
	return result;
}

std::string DNAParser::consts()
{
	std::string result;
	while (true)
	{
		t_codon a = read_codon();
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
			unread_codon(a);
			break;				
		}
	}
	return result;
}
