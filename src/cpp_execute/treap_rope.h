/*

Nodes represent strings and are immutable.
Operations:
  Node *pNode = new Leaf("ICFPC")
  pNode->length()
  pNode->concat_with(pNode2)
  pNode->slice(begin, end)
  pNode->as_string()
  Iterator i = Iterator(pNode);

Iterators are mutable. 
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

const int MAX_HEAP_KEY = 100000;

struct Iterator;

struct Node {
	int heap_key;

	virtual bool is_leaf() = 0;
	virtual int length() = 0;
	virtual std::string as_string() = 0;
	virtual Node* slice(int begin, int end) = 0;

	Node* concat_with(Node *other);
};

static Node* concat(Node *left, Node *right);
Node* Node::concat_with(Node *other) {
	return concat(this, other);
}


struct Leaf : Node {
	char *s; // no null at the end
	int begin, end;

	Leaf(std::string str) {
		this->heap_key = MAX_HEAP_KEY;
		s = new char[str.length()];
		memcpy(s, &str[0], str.length());
		begin = 0;
		end = str.length();
	}

	Leaf(char *s, int begin, int end) : s(s), begin(begin), end(end) {
		this->heap_key = MAX_HEAP_KEY;
	}

	virtual bool is_leaf() { return true; }
	virtual int length() { return end-begin; }
	virtual std::string as_string() { return std::string(s+begin, s+end); }
	virtual Node* slice(int begin, int end) {
		assert(0 <= begin);
		assert(begin <= end);
		assert(end <= length());
		if (begin == 0 && end == length())
			return this;
		return new Leaf(s, this->begin+begin, this->begin+end);
	}
};


struct InnerNode : Node {
	int len;
	Node *left, *right;

	InnerNode(int heap_key, Node *left, Node *right) :
		left(left),
		right(right),
		len(left->length()+right->length()) {
		this->heap_key = heap_key;
		assert(heap_key <= left->heap_key);
		assert(heap_key <= right->heap_key);
	}

	virtual bool is_leaf() { return false; }
	virtual int length() { return len; }
	virtual std::string as_string() { return left->as_string()+right->as_string(); }
	virtual Node* slice(int begin, int end) {
		assert(0 <= begin);
		assert(begin <= end);
		assert(end <= length());
		if (begin == 0 && end == length())
			return this;
		int L = left->length();
		if (end <= L)
			return left->slice(begin, end);
		if (begin >= L)
			return right->slice(begin-L, end-L);
		return concat(left->slice(begin, L), right->slice(0, end-L));
	}
};

static Node* concat(Node *left, Node *right) {
	if (left->is_leaf() && right->is_leaf()) {
		if (left->length() + right->length() < 100) 
			return new Leaf(left->as_string()+right->as_string());
		else
			return new InnerNode((unsigned int)rand()%MAX_HEAP_KEY, left, right);
	}
	if (left->heap_key < right->heap_key)
		return new InnerNode(
			left->heap_key, 
			((InnerNode*)left)->left, 
			concat(((InnerNode*)left)->right, right) );
	else
		return new InnerNode(
			right->heap_key,
			concat(left, ((InnerNode*)right)->left), 
			((InnerNode*)right)->right );
}



class Iterator { 
	std::vector<InnerNode*> path;
	Leaf *leaf;
	int position;

public:
	bool valid;

	Iterator(Node *node) {
		while (!node->is_leaf()) {
			path.push_back((InnerNode*)node);
			node = ((InnerNode*)node)->left;
		}
		leaf = (Leaf*)node;
		position = 0;
		advance(0); // to deal with possible empty leafs
	}

	const char& current() {
		assert(valid);
		return leaf->s[position];
	}

	void advance(int d) {
		assert(d >= 0);
		if (position+d < leaf->length()) {
			position += d;
			return;
		}
		d += position;

		Node *prev = leaf;
		while (true) {
			if (path.empty()) {
				valid = false;
				return; // we reached the end
			}
			if (path.back()->right == prev) {
				d += path.back()->left->length();
			}
			prev = path.back();
			if (d < path.back()->length())
				break;
			path.pop_back();
		} 

		while (true) {
			Node *next;
			if (d < path.back()->length())
				next = path.back()->left;
			else {
				d -= path.back()->left->length();
				next = path.back()->right;
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
