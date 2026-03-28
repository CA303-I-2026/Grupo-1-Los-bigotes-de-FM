// 01_limpieza.R
// Limpieza y preparación de los datos crudos
// Hecho por Anthonny Flores Rojas (C32975)

// Librerias
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cctype>

using namespace std;

// Estructura para manejo de datos por letras
struct Data {
    string password;
    char w[16];
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

// Funcion para contar cuantas contrasennas exceden el maximo de 16 caracteres
size_t contEx(vector<Data>& dt) {

    size_t ex = 0; // Variable de conteo

    for(size_t i = 0; i < dt.size(); i++) { // Recorrer todas las contrasennas

        if (dt[i].password.length() > 16) { // Si es mas larga de n caracteres

            ex++; // Se suman al exceso

        }

    }

    return ex;

}

// Clase cleaner
class cleaner {

    public:

        vector<Data> datacom; // Vector para almacenar los datos
        
        // Funcion para devolver los chunks de una contraseña
        vector<string> chunksdetector(string password) {

            vector<string> list;
            bool indicator = false;
            size_t j = 0;

            for(int i = 0; i < password.length()-1; i++) {

                if(isdigit(password[i]) && isdigit(password[i+1])) {

                    j = i;
                    
                    while(isdigit(password[i])) {

                        i++;
                        indicator = true;
                        
                    }

                    if (indicator) {

                        list.push_back(password.substr(j, i)); 
                        indicator = false;

                    }

                }

                else if (!isdigit(password[i]) && !isdigit(password[i+1])) {

                    j = i;
                    
                    while(!isdigit(password[i])) {

                        i++;
                        indicator = true;
                        
                    }

                    if (indicator) {

                        list.push_back(password.substr(j, i)); 
                        indicator = false;

                    }

                }
                

            }

            return list;

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

            ofstream fLoc("../datos/procesados/rockyou.txt"); // Buscar direccion

            for (size_t i = 0; i < datacom.size(); i++) {

                fLoc << datacom[i].password; // Escribir la clave

                for (size_t j = 0; j < 16; j++) { // Recorrer w

                    fLoc << ",";

                    if (datacom[i].w[j] != '\0') { // Si no esta vacio
                        fLoc << datacom[i].w[j];
                    } else {
                        fLoc << " "; // Espacio vacio
                    }

                }

                fLoc << "\n";

            }

            fLoc.close(); // Cierre de apertura de txt

        }

        // Funcion para pasar de txt a data
        void txttodata() {

            ifstream fLoc("../datos/originales/rockyou.txt"); // Buscar direccion
            string line; // Variable auxiliar
            
            while (getline(fLoc, line)) { // Mientras allan lineas en el txt

                if (!line.empty() && line.length() <= 16) {  // Si no son vacias y es menor a la cota eleguida


                    Data a; // Variable auxiliar
                    a.password = line; // Se copia la clave
                    datacom.push_back(a); // Y se almacena

                }

            }

            fLoc.close(); // Cierre de apertura de txt

        }
        
};

//
int main() {

    // Prubas 
    cleaner datos;

    datos.txttodata();
    
    cout << maxLengh(datos.datacom) << endl;
    cout << contEx(datos.datacom) << endl;

    return 0;

} 