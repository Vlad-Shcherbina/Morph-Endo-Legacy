#include <assert.h>

#include "DNAParser.h"

DNAParser::DNAParser(dna_type* pdna) : pdna(pdna), index(0), iter(Iterator(pdna))
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
