#pragma once

#include <cassert>


template<typename T>
class shared_ptr {
	T *raw_ptr;
public:
	shared_ptr() : raw_ptr(0) { }
	shared_ptr(T *p) : raw_ptr(p) {
		if (p)
			raw_ptr->ref_count++;
	}
	shared_ptr(shared_ptr<T> &p) : raw_ptr(p.raw_ptr) {
		if (raw_ptr)
			raw_ptr->ref_count++;
	}
	void operator=(T *p) {
		destroy();
		raw_ptr = p;
		if (p)
			raw_ptr->ref_count++;
	}
	void operator=(shared_ptr<T> &p) {
		// in exactly this order because assignment to itself is possible
		if (p->ref_count)
			p->ref_count++;
		destroy();
		raw_ptr = p.raw_ptr;
	}
	//operator T*() {
	//	return raw_ptr;
	//}
	template<typename Derived>
	operator Derived*() {
		return (Derived*)raw_ptr;
	}
	T* operator ->() {
		return raw_ptr;
	}
	void destroy() {
		if (raw_ptr == 0)
			return;
		assert(raw_ptr->ref_count > 0);
		if (--raw_ptr->ref_count == 0)
			delete raw_ptr;
	}
	~shared_ptr() {
		destroy();
	}
};