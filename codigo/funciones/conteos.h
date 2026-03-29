// conteos.h
#ifndef CONTEOS_H
#define CONTEOS_H

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <cctype>

using namespace std;

unordered_map<int, float> contChunks(vector<string>& letters);
unordered_map<char, float> contDis(vector<char>& chars);

#endif