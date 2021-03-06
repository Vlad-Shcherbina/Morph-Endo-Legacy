/*

Nodes represent strings and are immutable.
Operations:
  NodePtr pNode = new Leaf("ICFPC")
  pNode->length()
  pNode->concat_with(pNode2)
  pNode->slice(begin, end)
  pNode->as_string()
  Iterator i = Iterator(pNode);

Iterators are mutable. Iterator does not hold references!
Operations:
  i.advance(delta);
  i.current();
  i.valid - if it's false we reached the end

*/


#pragma once

#include <string>
#include <vector>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <algorithm>

#include "shared_ptr.h"


//#define SLOW_ASSERTS

const int MAX_HEAP_KEY = 2000000000;
const int CONCAT_THRESHOLD = 32;

struct Iterator;

struct Node;
//typedef Node *NodePtr;
typedef shared_ptr<Node> NodePtr;

extern int node_count;

struct Node {
	int ref_count;
	int heap_key;

	Node() : ref_count(0) { node_count++; }

	virtual bool is_leaf() = 0;
	virtual int length() = 0;
	virtual std::string as_string() = 0;
	virtual NodePtr slice(int begin, int end) = 0;
	virtual void debug_print(int indent = 0) = 0;
	virtual int depth() = 0;
	NodePtr concat_with(NodePtr other);
	virtual void accumulate_string(std::string &s) = 0;

protected:
	virtual ~Node() {
		node_count--;
		//std::cout<<"deleting node"<<std::endl;
		//std::cout<<"never delete me, I'm shared"<<std::endl;
		//assert(false); // never delete me, I'm shared
	}
	friend class shared_ptr<Node>;
};

NodePtr concat(NodePtr left, NodePtr right);
NodePtr merge(int new_key, NodePtr left, NodePtr right);

bool check_node(NodePtr node);
void test();


struct Leaf : Node {
	char* s; // no null at the end
	int *sRefCount; // ref count for s
	int begin, end;

	Leaf(std::string str) {
		this->heap_key = MAX_HEAP_KEY;
		if (str.empty())
			s = 0;
		else {
			s = new char[str.length()];
			memcpy(s, &str[0], str.length());
		}
		sRefCount = new int(1);
		begin = 0;
		end = str.length();
	}

	Leaf(Leaf *leaf, int begin, int end) : 
		s(leaf->s), 
		sRefCount(leaf->sRefCount),
		begin(leaf->begin+begin), 
		end(leaf->begin+end) {
		++*sRefCount;
		this->heap_key = MAX_HEAP_KEY;
	}

	virtual bool is_leaf() { return true; }
	virtual int length() { return end-begin; }
	virtual std::string as_string() { return std::string(s+begin, s+end); }
	virtual NodePtr slice(int begin, int end) {
		assert(0 <= begin);
		assert(begin <= end);
		assert(end <= length());
		if (begin == 0 && end == length())
			return this;
		return new Leaf(this, begin, end);
	}
	virtual void debug_print(int indent = 0) {
		for (int i = 0; i<indent; i++)
			std::cout<<' ';
		//std::string s = as_string();
		//if (s.length()>10)
		//	s = s.substr(0, 10)+"...";
		int len = std::min(10, length());
		std::cout<<"Leaf("<<std::string(s+begin, s+begin+len)<<", "<<length()<<")"<<std::endl;
	}
	virtual int depth() {
		return 0;
	}
	virtual void accumulate_string(std::string &s) {
		s.append(this->s+begin, this->s+end);
	}
	virtual ~Leaf() {
		assert(*sRefCount > 0);
		if (--*sRefCount == 0) {
			delete sRefCount;
			delete[] s;
		}
	}
};


struct InnerNode : Node {
	int len;
	NodePtr left, right;

	InnerNode(int heap_key, NodePtr left, NodePtr right) :
		left(left),
		right(right),
		len(left->length()+right->length()) {
		this->heap_key = heap_key;
		assert(heap_key <= left->heap_key);
		assert(heap_key <= right->heap_key);
#ifdef SLOW_ASSERTS
		assert(check_node(left));
		assert(check_node(right));
#endif
	}

	virtual bool is_leaf() { return false; }
	virtual int length() { return len; }
	virtual std::string as_string() { return left->as_string()+right->as_string(); }
	virtual NodePtr slice(int begin, int end) {
		assert(0 <= begin);
		assert(begin <= end);
		assert(end <= length());
		NodePtr result;
		if (begin == 0 && end == length()) {
			result = this;
		} else {
			int L = left->length();
			if (end <= L)
				result = left->slice(begin, end);
			else if (begin >= L)
				result = right->slice(begin-L, end-L);
			else
				result = concat(left->slice(begin, L), right->slice(0, end-L));
		}
#ifdef SLOW_ASSERTS
		assert(result->as_string() == as_string().substr(begin, end-begin));
#endif
		return result;
	}
	virtual void debug_print(int indent = 0) {
		for (int i = 0; i<indent; i++)
			std::cout<<' ';
		std::cout<<"Node "<<heap_key<<":"<<std::endl;
		left->debug_print(indent+2);
		right->debug_print(indent+2);
	}
	virtual int depth() {
		return 1+std::max(left->depth(), right->depth());
	}
	virtual void accumulate_string(std::string &s) {
		left->accumulate_string(s);
		right->accumulate_string(s);
	}
};

class Iterator { 
	std::vector<InnerNode*> path;
	std::vector<bool> dirs; // false - left, true - right
	Leaf *leaf;
	int position;

public:
	bool valid;

	Iterator(Node *node) {
		Node *prev = node;
		while (!node->is_leaf()) {
			path.push_back((InnerNode*)node);
			dirs.push_back(false);
			prev = node;
			node = ((InnerNode*)node)->left;
		}
		leaf = (Leaf*)node;
		position = 0;
		valid = true;
		advance(0); // to deal with possibly empty leafs
	}

	const char& current() {
		assert(valid);
		return leaf->s[leaf->begin+position];
	}

	void advance(int d=1) {
		assert(d >= 0);
		if (position+d < leaf->length()) {
			position += d;
			return;
		}
		d += position;

		//Node *prev = leaf;
		while (true) {
			if (path.empty()) {
				valid = false;
				return; // we reached the end
			}
			if (dirs.back()) {
				d += path.back()->left->length();
			}
			//prev = path.back();
			if (d < path.back()->length())
				break;
			path.pop_back();
			dirs.pop_back();
		} 
		dirs.pop_back();

		while (true) {
			Node *next;
			if (d < path.back()->left->length()) {
				next = path.back()->left;
				dirs.push_back(false);
			} else {
				d -= path.back()->left->length();
				next = path.back()->right;
				dirs.push_back(true);
			}
			
			if (next->is_leaf()) {
				leaf = (Leaf*)next;
				position = d;
				break;
			}
			path.push_back((InnerNode*)next);
		}
	}
};
