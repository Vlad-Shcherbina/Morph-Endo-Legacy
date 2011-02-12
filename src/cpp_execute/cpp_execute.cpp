

#include <iostream>
#include <string>
#include "treap_rope.h"

using namespace std;

int main(int argc, char* argv[])
{
	test();

	Node *s = new Leaf("hello");
	Node *sss = s->concat_with(s->concat_with(s));
	Node *slice = sss->slice(1, 7);

	cout<<slice->as_string()<<endl;

	Iterator iter(sss);
	for (; iter.valid; iter.advance(2)) {
		cout<<iter.current()<<" ";
	}
	cout<<endl;

	return 0;
}

