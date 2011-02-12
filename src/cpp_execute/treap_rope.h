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
#include <iostream>
#include <algorithm>

const int MAX_HEAP_KEY = 1000000000;
const int CONCAT_THRESHOLD = 32;

struct Iterator;

struct Node {
	int heap_key;

	virtual bool is_leaf() = 0;
	virtual int length() = 0;
	virtual std::string as_string() = 0;
	virtual Node* slice(int begin, int end) = 0;
	virtual void debug_print(int indent = 0) = 0;
	virtual int depth() = 0;
	Node* concat_with(Node *other);
};

Node* concat(Node *left, Node *right);
Node* Node::concat_with(Node *other) {
	Node* result = concat(this, other);
	assert(result->as_string() == this->as_string()+other->as_string()); // ridiculously slow
	return result;
}


struct Leaf : Node {
	char *s; // no null at the end
	int begin, end;

	Leaf(std::string str) {
		this->heap_key = MAX_HEAP_KEY;
		if (str.empty())
			s = 0;
		else {
			s = new char[str.length()];
			memcpy(s, &str[0], str.length());
		}
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
	virtual void debug_print(int indent = 0) {
		for (int i = 0; i<indent; i++)
			std::cout<<' ';
		std::cout<<"Leaf("<<as_string()<<")"<<std::endl;
	}
	virtual int depth() {
		return 0;
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
		Node *result;
		if (begin == 0 && end == length())
			result = this;
		else {
			int L = left->length();
			if (end <= L)
				result = left->slice(begin, end);
			else if (begin >= L)
				result = right->slice(begin-L, end-L);
			else
				result = concat(left->slice(begin, L), right->slice(0, end-L));
		}
		assert(result->as_string() == as_string().substr(begin, end-begin)); // ridiculously slow
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
};

Node *merge(int new_key, Node* left, Node* right) {
	if (new_key <= left->heap_key && new_key <= right->heap_key)
		return new InnerNode(new_key, left, right);
	if (left->heap_key < right->heap_key)
		return new InnerNode(
			left->heap_key, 
			((InnerNode*)left)->left, 
			merge(new_key, ((InnerNode*)left)->right, right) );
	else
		return new InnerNode(
			right->heap_key,
			merge(new_key, left, ((InnerNode*)right)->left),
			((InnerNode*)right)->right);
}

Node* concat(Node *left, Node *right) {
	if (left->is_leaf() && right->is_leaf() &&
		left->length() + right->length() <= CONCAT_THRESHOLD) 
			return new Leaf(left->as_string()+right->as_string());

	int new_key = rand()%MAX_HEAP_KEY;
	return merge(new_key, left, right);

	//return new InnerNode(std::min(left->heap_key, right->heap_key), left, right); // unbalanced implementation
}



class Iterator { 
	std::vector<InnerNode*> path;
	std::vector<bool> dirs; // false - left, true - right
	Leaf *leaf;
	int position;

public:
	bool valid;

	Iterator(Node *node) {
		while (!node->is_leaf()) {
			path.push_back((InnerNode*)node);
			dirs.push_back(false);
			node = ((InnerNode*)node)->left;
		}
		leaf = (Leaf*)node;
		position = 0;
		valid = true;
		advance(0); // to deal with possible empty leafs
	}

	const char& current() {
		assert(valid);
		return leaf->s[leaf->begin+position];
	}

	void advance(int d) {
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


bool check_node(Node *node) {
	std::string s = node->as_string();
	assert(s.length() == node->length());
	Iterator iter = Iterator(node);
	for (std::string::iterator i = s.begin(); i != s.end(); i++, iter.advance(1))
		assert(iter.current() == *i);
	assert(!iter.valid);
	return true;
}



void test() {
	Node *hello = new Leaf("hello");
	Node *world = new Leaf("world");
	//check_node(hello);
	Node *hw = hello->concat_with(world);
	//hw->debug_print();
	check_node(hw);

	//concatenation
	for (int i = 0; i<100; i++) {
		if (i%20 == 0)
			std::cout<<i<<std::endl;
		hw = hw->concat_with(hello);
		//hw->debug_print();
		assert(check_node(hw));
	}
	assert(check_node(hw));

	//random access
	for (int i = 0; i<100; i++) {
		Iterator iter = Iterator(hw);
		int pos = 0;
		std::string s = hw->as_string();
		while (pos < hw->length()) {
			//std::cout<<pos<<" ";
			assert(s[pos] == iter.current());
			int d = rand()%100;
			pos += d;
			iter.advance(d);
		}
		assert(!iter.valid);
		//std::cout<<std::endl;
	}

	//slices
	for (int i = 0; i<100; i++) {
		int begin = rand()%(hw->length()+1);
		int end = begin+rand()%(hw->length()-begin+1);
		Node *slice = hw->slice(begin, end);
		assert(check_node(slice));
		std::cout<<begin<<" "<<end<<std::endl;
	}
	std::cout<<"hw depth "<<hw->depth()<<std::endl;
}