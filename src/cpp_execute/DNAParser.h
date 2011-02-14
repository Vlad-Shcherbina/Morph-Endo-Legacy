#ifndef DNAPARSER_H
#define DNAPARSER_H
#include "treap_rope.h"

#include <string>

typedef NodePtr dna_type;
typedef Iterator dna_iter;
typedef char t_base;
typedef std::string t_codon;

class DNAParser {
	dna_type pdna;
	dna_iter iter;
	int dna_len;		// TODO GET RID OF THIS
	int index;
	t_codon saved_codon;

	public:
	DNAParser(dna_type pdna);
	t_base read_base();
	t_codon read_codon();
	void unread_codon(t_codon codon);
	inline int getIndex()
	{
		assert(saved_codon == "");	// otherwise index is wrong. probably.
		return index;
	}
	int nat();
	std::string consts();
};

#endif /* DNAPARSER_H */
