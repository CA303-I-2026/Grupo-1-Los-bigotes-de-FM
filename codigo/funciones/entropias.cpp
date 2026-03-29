// entropias.cpp
// Calculo de entropias de las contrasennas
// Hecho por Anthonny Flores Rojas (C32975)
// Annadir la tipica shanno (la tengo en el repositorio de herramientas I)
// Annadir otros tipos de entropias

// Librerias
#include <iostream>
#include <string>
#include <fstream>
#include <unordered_map>  
#include <unordered_set> 
#include <cmath>

using namespace std;

float entropyShannon(string& password) {
  
  if(password == "") return 0;
    
  unordered_map<char, float> chars; // Caracteres unicos
  unordered_set<char> pw;
  float entropy = 0.0; // Variable auxiliar
  float lenght = password.length();
    
  for (int i = 0; i < password.length(); i++) { // Por cada caracter

    chars[password[i]] += 1; // Agregar el conteo del caracter
    pw.insert(password[i]);

  }
    
  for (char c: pw) { // Por cada elemento unico

    entropy -= (chars[c]/lenght) * log2(chars[c]/lenght); // Calcular la entropia

  }
    
  return entropy;

}

float entropyEffective(string& password) {
  
  if(password == "") return 0;

}
