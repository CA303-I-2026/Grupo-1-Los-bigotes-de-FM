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
    string password, w1, w2, w3, w4, w5, w6, w7, w8;
};

// Estructura para manejo de datos por chuncks
struct Datac {
    string password, chunk1, chunk2, chunk3, chunk4, chunk5, chunk6, chunk7, chunk8;
};

// Funcion para encontrar la contrasenna mas larga
int maxLengh(vector<Data> bombo) {

    size_t maxLen = 0; // Variable de conteo

    for(size_t i; i < bombo.size(); i++) { // Recorrer todas las contrasennas

        if (bombo[i].password.length() > maxLen) { // Si es mas larga

            maxLen = bombo[i].password.length(); // Se copia el largo

        }

    }

    return maxLen;

}

string trim(const string& s) {

    size_t first = s.find_first_not_of(" \n\r\t");

    if (first == string::npos) return "";

    size_t last = s.find_last_not_of(" \n\r\t");

    return s.substr(first, (last - first + 1));
    
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
