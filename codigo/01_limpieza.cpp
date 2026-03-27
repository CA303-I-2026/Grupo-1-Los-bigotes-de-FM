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
size_t maxLengh(vector<Data>& dt) {

    size_t maxLen = 0; // Variable de conteo

    for(size_t i = 0; i < dt.size(); i++) { // Recorrer todas las contrasennas

        if (dt[i].password.length() > maxLen) { // Si es mas larga

            maxLen = dt[i].password.length(); // Se copia el largo

        }

    }

    return maxLen;

}

// Funcion para contar cuantas contraseñas exceden el maximo de 32 caracteres
size_t maxLengh(vector<Data>& dt) {

    size_t maxLen = 0; // Variable de conteo

    for(size_t i = 0; i < dt.size(); i++) { // Recorrer todas las contrasennas

        if (dt[i].password.length() > maxLen) { // Si es mas larga

            maxLen = dt[i].password.length(); // Se copia el largo

        }

    }

    return maxLen;

}

// Clase cleaner
class cleaner {

    public:

        vector<Data> datacom; // Vector para almacenar los datos
        
        //
        void chunksdetector() {

        }

        //
        void tochunks() {

        }

        // Funcion para partir en letras
        void toletters() {

            Data c; // Variable auxiliar

            for(size_t i = 0; i < datacom.size(); i++) { // Recorrer todas las contrasennas
                
                c = datacom[i]; // Copiar el elemento actual del vector

                for(size_t j = 0; j < c.password.length(); j++) { // Por cada letra del elemento

                    c.w[i] = c.password[j]; // Se copia la letra

                }
                
            }

        }

        //
        void datatotxt() {

        }

        // Funcion para pasar de txt a data
        void txttodata() {

            ifstream fLoc("../datos/originales/rockyou.txt");
            string line;
            
            while (getline(fLoc, line)) {

                if (!line.empty()) {  

                    Data a;
                    a.password = line;
                    datacom.push_back(a);

                }

            }

            fLoc.close();

        }

        //
        void datacleaner() {

        }
};

//
int main() {

    cleaner datos;

    datos.txttodata();
    
    size_t x = maxLengh(datos.datacom);
    cout << x << endl;


    return 0;

} 