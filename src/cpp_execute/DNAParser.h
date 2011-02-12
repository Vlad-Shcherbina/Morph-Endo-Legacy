#ifndef DNAPARSER_H
#define DNAPARSER_H

#include <string>

typedef std::string dna_type;
typedef char t_base;
typedef std::string t_codon;

//int len(dna_type* dna) { return dna->length(); }

class DNAParser {
	dna_type* pdna;
	int dna_len;
	int index;
	t_codon saved_codon;

	public:
	DNAParser(dna_type* pdna);
	t_base read_base();
	t_codon read_codon();
	void unread_codon(t_codon codon);
	inline int getIndex() { return index; }
};

#endif /* DNAPARSER_H */
