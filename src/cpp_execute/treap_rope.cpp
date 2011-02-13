#include "treap_rope.h"

Node* Node::concat_with(Node *other) {
	Node* result = concat(this, other);
	assert(result->as_string() == this->as_string()+other->as_string()); // ridiculously slow
	return result;
}

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