#include "treap_rope.h"

int node_count=0;

NodePtr Node::concat_with(NodePtr other) {
	NodePtr result = concat(this, other);
#ifdef SLOW_ASSERTS
	assert(result->as_string() == this->as_string()+other->as_string());
#endif
	return result;
}

NodePtr merge(int new_key, NodePtr left, NodePtr right) {
	if (left->length()+right->length() <= CONCAT_THRESHOLD)
		return new Leaf(left->as_string()+right->as_string());

	if (new_key <= left->heap_key && new_key <= right->heap_key)
		return new InnerNode(new_key, left, right);
	if (left->heap_key < right->heap_key ||
		left->heap_key == right->heap_key && (rand()%2)) {
		assert(!left->is_leaf());
		return new InnerNode(
			left->heap_key, 
			((InnerNode*)left)->left, 
			merge(new_key, ((InnerNode*)left)->right, right) );
	}
	else {
		assert(!right->is_leaf());
		return new InnerNode(
			right->heap_key,
			merge(new_key, left, ((InnerNode*)right)->left),
			((InnerNode*)right)->right);
	}
}

NodePtr concat(NodePtr left, NodePtr right) {
	if (//left->is_leaf() && right->is_leaf() &&
		left->length() + right->length() <= CONCAT_THRESHOLD) 
			return new Leaf(left->as_string()+right->as_string());

	int new_key = rand()%MAX_HEAP_KEY;
	return merge(new_key, left, right);

	//return new InnerNode(std::min(left->heap_key, right->heap_key), left, right); // unbalanced implementation
}

bool check_node(NodePtr node) {
	std::string s = node->as_string();
	assert(s.length() == node->length());
	Iterator iter = Iterator(node);
	for (std::string::iterator i = s.begin(); i != s.end(); i++, iter.advance(1))
		assert(iter.current() == *i);
	assert(!iter.valid);
	return true;
}

void test() {
	NodePtr hello = new Leaf("hello");
	NodePtr world = new Leaf("world");
	//check_node(hello);
	NodePtr hw = hello->concat_with(world);
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
	hw->debug_print();

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
		NodePtr slice = hw->slice(begin, end);
		assert(check_node(slice));
		std::cout<<begin<<" "<<end<<std::endl;
	}
	std::cout<<"hw depth "<<hw->depth()<<std::endl;
}
