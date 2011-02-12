#include <string>
#include <sstream>
#include <assert.h>
#include "DNAParser.h"

enum item_type {NONE, BASE, LPAREN, RPAREN, SKIP, SEARCH, REFERENCE, LENGTH};


struct Item 
{
	Item() {};
	virtual std::string str() { assert(false); return "x"; };
	virtual item_type type() { assert(false); return NONE; }
};

struct IBase : Item
{
	t_base b;
	IBase(t_codon a)
	{
		switch (a[0])
		{
			case 'I': b = 'P'; break;
			case 'C': b = 'I'; break;
			case 'F': b = 'C'; break;
			case 'P': b = 'F'; break;
		}
	}
	std::string str()
	{
		std::stringstream ss;
		ss << b;
		return ss.str();
	}
	item_type type() { return BASE; }
};

struct ILParen : Item {
	std::string str() {	return "(";	}
	item_type type() { return LPAREN; }
};

struct IRParen : Item {
	std::string str() { return ")"; }
	item_type type() { return RPAREN; }
};

struct ISkip : Item
{
	int n;
	ISkip(int n) : n(n) {};
	std::string str() {
		std::stringstream ss;
		ss << "!" << n;
		return ss.str();
	}
	item_type type() { return SKIP; }
};

struct ISearch : Item
{
	std::string s;
	ISearch(std::string s) : s(s) {};
	std::string str() { return "?\"" + s + "\""; }
	item_type type() { return SEARCH; }
};

struct IReference : Item
{
	int n, l;
	IReference(int n, int l) : n(n), l(l) {};
	std::string str()
	{
		std::stringstream ss;
		ss << "\\" << n;
		if (l > 0)
			ss << "_" << l;
		return ss.str();
	}
	item_type type() { return REFERENCE; }
};

struct ILength : Item
{
	int n;
	ILength(int n) : n(n) {};
	std::string str()
	{
		std::stringstream ss;
		ss << "|" << n << "|";
		return ss.str();
	}
	item_type type() { return LENGTH; }
};
