// conteos.h
#ifndef CONTEOS_H
#define CONTEOS_H

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <cctype>

using namespace std;

unordered_map<int, int> contChunks(vector<string>& letters);
unordered_map<char, int> contDis(vector<char>& chars);

#endif