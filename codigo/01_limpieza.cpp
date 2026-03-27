// 01_limpieza.R
// Limpieza y preparación de los datos crudos
// Hecho por Anthonny Flores Rojas (C32975)

// Librerias
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <algorithm>

using namespace std;

// Estructura para manejo de datos por letras
struct Data {
    string password;
    char w[8];
};

// Estructura para manejo de datos por chuncks
struct Datac {
    string password;
    string chunks[8];
};

// Funcion para encontrar la contrasenna mas larga
int maxLengh(vector<Data>& dt) {

    size_t maxLen = 0; // Variable de conteo

    for(size_t i = 0; i < dt.size(); i++) { // Recorrer todas las contrasennas

        if (dt[i].password.length() > maxLen) { // Si es mas larga

            maxLen = dt[i].password.length(); // Se copia el largo

        }

    }

    return maxLen;

}

// Funcion para partir en letras
string trim(vector<Data> dt) {

    Data c; // Variable auxiliar

    for(size_t i = 0; i < dt.size(); i++) { // Recorrer todas las contrasennas
        
        c = dt[i]; // Copiar el elemento actual del vector

        for(size_t j = 0; j < c.password.length(); j++) { // Por cada letra del elemento
            c.w[i] = c.password[j]; // Se copia la letra
        }
        
    }

}

class cleaner {

    vector<Data> datacom;

    //
    void chunksdetector() {

    }

    //
    void tochunks() {

    }

    //
    void toletters() {

    }

    //
    void datatotxt() {

    }

    //
    void txttodata() {
        ifstream fLoc("rockyou.txt");
            string line;
           
    }

    //
    void datacleaner() {

    }
};

//
int main() {
    


    return 0;

}
