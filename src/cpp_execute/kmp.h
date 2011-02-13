#include <string>
#include <vector>

#include "treap_rope.h"

int kmp_search(Node* text, std::string &pattern, int start)
{
	int pattern_len = pattern.size();
	// shifts table
    std::vector<int> shifts(pattern_len + 1, 1);
    int shift = 1;
	for (int pos = 0; pos < pattern_len; pos++)
	{
		while ((shift <= pos) && (pattern[pos] != pattern[pos-shift]))
			shift += shifts[pos-shift];
		shifts[pos+1] = shift;
	}
    
	// the actual search
	int start_pos = start;
	Iterator iter(text);
	iter.advance(start);

	int match_len = 0;
	

	while (iter.valid)
	{
		while ((match_len == pattern_len) ||
			(match_len >= 0) && (pattern[match_len] != iter.current()))
		{
			start_pos += shifts[match_len];
			match_len -= shifts[match_len];
		}
		match_len += 1;
		if (match_len == pattern_len)
			return start_pos;
		iter.advance();
	}
	return text->length();
}
