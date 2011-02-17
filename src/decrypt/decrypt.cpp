// decrypt.cpp : Defines the entry point for the console application.
//

#include <iostream>
#include <algorithm>

using namespace std;

template<typename It>
void encrypt(It key_begin, It key_end, It data_begin, It data_end, It result_begin) {
	unsigned char x[256];
	unsigned char *key_ptr = key_begin;
	int foo = 0, bar;
	for (int i=0; i < 256; ++i)
		x[i] = i;
	for (bar = 0; bar < 256; ++bar) {
		foo += x[bar]+*key_ptr;
		foo %= 256;
		swap(x[foo], x[bar]);
		++key_ptr;
		if (key_ptr == key_end)
			key_ptr = key_begin;
	}
	foo = bar = 0;
	for (It data_ptr = data_begin, result_ptr = result_begin; 
		 data_ptr != data_end; 
		 ++data_ptr, ++result_ptr) {
		++foo;
		bar += x[foo];
		bar %= 256;
		swap(x[foo], x[bar]);
		*result_ptr = *data_ptr^((x[foo]+x[bar])%256);
	}
}

bool check_data(unsigned char data[]) {
	return data[0] == 0x40 && (data[2]>>4 & 15) == 0 && data[3] == 0xC3 && data[4] == 0x0C;
}

const int MAX_KEY_LEN = 4;
int key_len = 0;
const int data_len = 5;
unsigned char encrypted[data_len] = {157, 121, 2, 136, 149};
unsigned char key[MAX_KEY_LEN] ={0};

void check_keys() {
	unsigned char decrypted[data_len];
		/*for (int i = 0; i<key_len; i++)
			cout<<(int)key[i]<<" ";
		cout<<endl;*/
	encrypt(key, key+key_len, encrypted, encrypted+data_len, decrypted);
	if (check_data(decrypted)) {
		for (int i = 0; i<data_len; i++)
			cout<<(int)decrypted[i]<<", ";
		cout<<";  ";
		for (int i = 0; i<key_len; i++)
			cout<<(int)key[i]<<", ";
		cout<<endl;
	}
	if (key_len == MAX_KEY_LEN)
		return;
	key_len++;
	for (int i = 0; i<256; i++) {
		if (key_len == 1)
			cout<<100*i/256<<"%"<<endl;
		key[key_len-1] = i;
		check_keys();
	}
	key_len--;
}

int main(int argc, char* argv[])
{
	
	//unsigned char encrypted[] = {64, 93, 7, 195};
	//cout<<check_data(encrypted)<<endl;
	check_keys();
	return 0;
}

