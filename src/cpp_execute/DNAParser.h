#ifndef DNAPARSER_H
#define DNAPARSER_H
#include "treap_rope.h"

#include <string>

typedef NodePtr dna_type;
typedef Iterator dna_iter;
typedef char t_base;
typedef std::string t_codon;

const std::string green_zone_marker = "IFPICFPPCFFPP";

class DNAParser {
	dna_type pdna;
	dna_iter iter;
	int dna_len;
	int index;
	t_codon saved_codon;

	int green_zone_offset;

	public:
	DNAParser(dna_type pdna);
	t_base read_base();
	t_codon read_codon();
	void unread_codon(t_codon codon);
	inline int DNAParser::getIndex() {
		assert(saved_codon == "");	// otherwise index is wrong. probably.
		return index;
	}
	void jump(int index);
	int nat();
	std::string consts();
	int green_offset();
	int get_green_int(int offset);	// warning: causes jump
};

#endif /* DNAPARSER_H */
