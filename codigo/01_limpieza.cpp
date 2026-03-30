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
#include "conteos.h"
#include "entropias.h"
#include <unordered_map>  

using namespace std;

// Estructura para manejo de datos por letras
struct Data {
    string password;
    char w[16] = {0};
};

// Estructura para manejo de datos por chuncks
struct Datac {
    string password;
    string chunks[8];
};

// Estructura para manejo de datos distribucion y entropia
struct Datact {
    string password;
    float entropyS, entropyD;
};

// Estructura para de dist de Ley de Benford
struct Databenf {
    unordered_map<int, int> benfC;
};

struct Datadist {
    unordered_map<char, int> map;
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

// Funcion para contar cuantos caracteres diferentes a los chuunks y contraseñas
size_t contDif(vector<Datac>& dt) {

    size_t cf = 0; // Variable de conteo
    int a = 0;

    for(size_t i = 0; i < dt.size(); i++) { // Recorrer todas las contrasennas

        for(size_t j = 0; j < 8; j++) {

            a =+ dt[i].chunks[j].length(); // Se suman los largos de los chunks
            // cout << dt[i].chunks[j] << endl; // Se imprimen los chunks
            // cout << dt[i].chunks[j].length() << endl; // Se imprimen los chunks

        }

        cf =+ dt[i].password.length(); // Se suman los largos de las contrasennas
        
    }

    cf = cf - a; // Se resta el largo total de los chunks

    return cf;

}

// Clase cleaner
class cleaner {

    public:

        vector<Data> datacom; // Vector para almacenar los datos
        vector<Datac> datacomp; // Vector para almacenar los datos
        vector<Datact> newdata;
        vector<Databenf> benford;
        vector<Datadist> distribution;
        
        
        // Funcion para devolver los chunks de una contraseña
        vector<string> chunksdetector(string password) {

            vector<string> list;

            if (password.empty()) return list;

            string current = "";
            current += password[0]; // Se empieza el primer chunk con el primer caracter

            for (size_t i = 1; i < password.length(); i++) {

                // Si son del mismo tipo 
                if (isdigit(password[i]) == isdigit(password[i-1])) {

                    current += password[i]; // Se agrega al chunk actual

                } else {

                    if (current.length() >= 2) list.push_back(current); // Se guarda el chunk
                    current = "";
                    current += password[i]; // Se empieza uno nuevo

                }

            }

            if (current.length() >= 2) list.push_back(current); // Se guarda el ultimo chunk

            return list;

        }

        // Funcion para encontrar los chunks
        void tochunks() {

            vector<string> list;

            for(size_t i = 0; i < datacomp.size(); i++) { // Recorrer todas las contrasennas+

                list = chunksdetector(datacomp[i].password);

                for(size_t j = 0; j < list.size() && j < 8; j++) { // copiar cada chunk

                    datacomp[i].chunks[j] = list[j]; // Se copia el chunk

                }
                
            }

        }

        // Funcion para partir en letras
        void toletters() {

            for(size_t i = 0; i < datacom.size(); i++) { // Recorrer todas las contrasennas

                for(size_t j = 0; j < datacom[i].password.length(); j++) { // Por cada letra del elemento

                    datacom[i].w[j] = datacom[i].password[j]; // Se copia la letra

                }
                
            }

        }

        // Funcion para pasar de data a txt (LETTERS)
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

        // Funcion para pasar de data a txt (CHUNKS)
        void datatotxtc() {

            ofstream fLoc("../datos/procesados/rockyouchunk.txt"); // Buscar direccion

            for (size_t i = 0; i < datacomp.size(); i++) {

                fLoc << datacomp[i].password; // Escribir la clave

                for (size_t j = 0; j < 8; j++) { // Recorrer w

                    fLoc << ",";

                    if (datacomp[i].chunks[j] != "") { // Si no esta vacio
                        fLoc << datacomp[i].chunks[j];
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
                    Datac b;
                    a.password = line; // Se copia la clave
                    b.password = line;
                    datacom.push_back(a); // Y se almacena
                    datacomp.push_back(b);

                }

            }

            fLoc.close(); // Cierre de apertura de txt

        }

        // Funcion para pasar de txt a data (CREACION DE TABLAS)
        void txttodataNew() {

            ifstream fLoc("../datos/procesados/rockyou.txt"); // Buscar direccion
            string line; // Variable auxiliar
            
            while (getline(fLoc, line)) { // Mientras allan lineas en el txt

                if (line.empty()) continue;

                stringstream ss(line);
                string token;
                Data a;

                getline(ss, a.password, ','); // Leer la password

                for (int i = 0; i < 16; i++) { // Leer cada letra
                    getline(ss, token, ',');
                    if (!token.empty() && token[0] != ' ') {
                        a.w[i] = token[0];
                    }
                }

                datacom.push_back(a);

            }

            fLoc.close(); // Cierre de apertura de txt

            ifstream fLocc("../datos/procesados/rockyouchunk.txt");

            while (getline(fLocc, line)) {

                if (line.empty()) continue;

                stringstream ss(line);
                string token;
                Datac b;

                getline(ss, b.password, ','); // Leer la password

                for (int i = 0; i < 8; i++) { // Leer cada chunk
                    getline(ss, token, ',');
                    if (!token.empty() && token[0] != ' ') {
                        b.chunks[i] = token;
                    }
                }

                datacomp.push_back(b);

            }

        }

        // Funcion para calcular las entropias
        void makeentropy() {

            for (size_t i = 0; i < datacom.size(); i++) {

                Datact d;
                d.password = datacom[i].password;
                d.entropyS = entropyShannon(datacom[i].password);
                d.entropyD = entropyDensity(datacom[i].password);
                newdata.push_back(d);

            }

        }

        // Funcion para calcular la distribucion de los caracteres
        void makedist() {

            for (size_t pos = 0; pos < 16; pos++) { // Por cada posicion de letra

                vector<char> chars;

                for (size_t j = 0; j < datacom.size(); j++) { // Por cada contrasenna
                    chars.push_back(datacom[j].w[pos]);
                }

                Datadist d;
                d.map = contDis(chars); // Se calcula la distribucion de los caracteres
                distribution.push_back(d);

            }

        }

        // Funcion para calcular la distribucion de los primeros numeros de los chunks
        void makebenford() {

            for (size_t pos = 0; pos < 8; pos++) { // Por cada posicion de chunk

                vector<string> chunks;

                for (size_t j = 0; j < datacomp.size(); j++) { // Por cada contrasenna
                    chunks.push_back(datacomp[j].chunks[pos]);
                }

                Databenf b;
                b.benfC = contChunks(chunks); // Se calcula la distribucion
                benford.push_back(b);

            }

        }

        // Funcion para pasar de data a txt (CREACION DE TABLAS)
        void datatotxtNew() {
 
            /*
            // Guardar entropias
            ofstream fEnt("../datos/procesados/rockyoue.txt");
            fEnt << "password,entropyS,entropyD\n"; // Header

            for (size_t i = 0; i < newdata.size(); i++) { // Por cada contrasenna
                fEnt << newdata[i].password << "," << newdata[i].entropyS << "," << newdata[i].entropyD << "\n";
            }

            fEnt.close(); // Cierre de apertura de txt
            */

            // Guardar distribucion de caracteres por posicion
            ofstream fDist("../datos/procesados/rockyouedist.txt");

            fDist << "char"; // Header
            for (int i = 1; i <= 16; i++) fDist << ",pos" << i;
            fDist << "\n";

            unordered_set<char> allChars; // Caracteres unicos
            for (size_t i = 0; i < distribution.size(); i++) { // Recolectar todos los chars unicos
                for (auto& pair : distribution[i].map) {
                    allChars.insert(pair.first);
                }
            }

            for (char c : allChars) { // Por cada char unico una fila
                if ((unsigned char)c > 127) continue; // Ignorar caracteres no ASCII
                fDist << c;
                for (size_t j = 0; j < 16; j++) { // Por cada posicion
                    fDist << ",";
                    if (distribution[j].map.count(c)) {
                        fDist << distribution[j].map[c];
                    } else {
                        fDist << "0"; // Espacio vacio
                    }
                }
                fDist << "\n";
            }

            fDist.close(); // Cierre de apertura de txt

            // Guardar distribucion de Benford por posicion de chunk
            ofstream fBenf("../datos/procesados/rockyoubenford.txt");

            fBenf << "digit"; // Header
            for (int i = 1; i <= 8; i++) fBenf << ",chunk" << i;
            fBenf << "\n";

            for (int d = 0; d <= 9; d++) { // Por cada digito del 0 al 9 una fila
                fBenf << d;
                for (size_t j = 0; j < 8; j++) { // Por cada posicion de chunk
                    fBenf << ",";
                    if (benford[j].benfC.count(d)) {
                        fBenf << benford[j].benfC[d];
                    } else {
                        fBenf << "0"; // Espacio vacio
                    }
                }
                fBenf << "\n";
            }

            fBenf.close(); // Cierre de apertura de txt

        }

};

// main
int main() {

    // Prubas 
    cleaner datos;
    datos.txttodataNew();
    // datos.makeentropy();
    
    cout << "termino" << endl;
    datos.makebenford();
    datos.makedist();
    datos.datatotxtNew();
    // datos.toletters();
    // datos.tochunks();
    // datos.datatotxt();
    // datos.datatotxtc();
    /*
    se saco aprox menos del 1% de las contraseñas (las mayores a 16 caracteres)
    en total fueron 125936 que se quedaron afuera
    */

    // cout << contDif(datos.datacomp) << endl;
    // Diferencia entre caracteres: 11 (caracteres solos)
    /*
    No tiene sentido contar los caracteres solos en los chunks, ya que estos normalmente 
    son remplazos de letras o casos aislados
    */

    return 0;

} 