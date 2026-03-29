// conteos.cpp
// Conteo para la creacion de las funciones de distribucion de la aparacion de los caracteres y numeros
// Hecho por Anthonny Flores Rojas (C32975)
// Tienen que ser una funcion dim() = 16 con 37 valores posibles (Se pueden annadir caracteres especiales)
// CONTEO DE los primeros numeros de los chunks que sean numeros

// Librerias
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cctype>
#include <unordered_map>  
#include <unordered_set> 

using namespace std;

// Funcion para contar los primeros numeros de los chunks numericos 
unordered_map<char, float> contChunks(vector<string>& letters) {

    unordered_map<char, float> chars_map;

    for (int i = 0; i < letters.size(); i++) { // Por cada chunk
    
        if (letters[i].empty()) continue; // Si es un espacio vacio
        if (isdigit(letters[i][0])) { // Si el primer caracter es un numero
            chars_map[letters[i][0]] += 1; // Agregar el conteo del caracter
        }
    
    }
    
    return chars_map;

}

// Funcion para contar la distribucion de los caracteres de las contrasennas
unordered_map<char, float> contDis(vector<char>& chars) {

    unordered_map<char, float> chars_map; // Caracteres unicos
    unordered_set<char> pw;

    for (int i = 0; i < chars.size(); i++) { // Por cada caracter

        if (chars[i] == 0) continue; // Si es un espacio vacio
        chars_map[chars[i]] += 1; // Agregar el conteo del caracter
        pw.insert(chars[i]);

    }

    return chars_map;

}

