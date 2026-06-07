// 01_limpieza.cpp
// Limpieza y preparación de los datos crudos
// Hecho por Anthonny Flores Rojas (C32975)

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cctype>
#include "conteos.h"
#include "entropias.h"
#include <unordered_map>
#include <chrono>
#include <thread>

using namespace std;

// Estructura para manejo de datos por letras
struct Data {
    string password;
    vector<char> w;
};

// Estructura para manejo de datos por chuncks
struct Datac {
    string password;
    vector<string> chunks;
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

    size_t maxLen = 0;

    for(size_t i = 0; i < dt.size(); i++) {

        if (dt[i].password.length() > maxLen) {

            maxLen = dt[i].password.length();

        }

    }

    return maxLen;

}

// Funcion para contar cuantas contrasennas exceden el maximo de 16 caracteres
size_t contEx(vector<Data>& dt) {

    size_t ex = 0;

    for(size_t i = 0; i < dt.size(); i++) {

        if (dt[i].password.length() > 16) {

            ex++;

        }

    }

    return ex;

}

// Funcion para contar cuantos caracteres diferentes a los chunks y contraseñas
size_t contDif(vector<Datac>& dt) {

    size_t cf = 0;
    size_t a = 0;

    for(size_t i = 0; i < dt.size(); i++) {

        for(size_t j = 0; j < 8; j++) {

            a =+ dt[i].chunks[j].length();

        }

        cf =+ dt[i].password.length();

    }

    cf = cf - a;

    return cf;

}

// Clase cleaner
class cleaner {

    public:

        vector<Data> datacom;
        vector<Datac> datacomp;
        vector<Databenf> benford;
        vector<Datadist> distribution;

        // Funcion para devolver los chunks de una contraseña
        vector<string> chunksdetector(string password) {

            vector<string> list;

            if (password.empty()) return list;

            string current = "";
            current += password[0];

            for (size_t i = 1; i < password.length(); i++) {

                if (isdigit(password[i]) == isdigit(password[i-1])) {

                    current += password[i];

                } else {

                    if (current.length() >= 2) list.push_back(current);
                    current = "";
                    current += password[i];

                }

            }

            if (current.length() >= 2) list.push_back(current);

            return list;

        }

        // Funcion para encontrar los chunks
        void tochunks(int maxC) {

            vector<string> list;

            for(size_t i = 0; i < datacomp.size(); i++) {

                list = chunksdetector(datacomp[i].password);

                for(size_t j = 0; j < list.size() && (int)j < maxC; j++) { // Cambiasr el 8 por el maximo de chunks deseados

                    datacomp[i].chunks[j] = list[j];

                }

            }

        }

        // Funcion para partir en letras
        void toletters(int maxL) {

            for(size_t i = 0; i < datacom.size(); i++) {

                for(size_t j = 0; j < datacom[i].password.length() && (int)j < maxL; j++) {

                    datacom[i].w[j] = datacom[i].password[j];

                }

            }

        }

        // Funcion para pasar de data a txt (LETTERS)
        void datatotxt() {

            ofstream fLoc("../datos/procesados/rockyou.txt");

            for (size_t i = 0; i < datacom.size(); i++) {

                fLoc << datacom[i].password;

                for (size_t j = 0; j < datacom[i].w.size(); j++) { // Cambiar el 16 para guardar el maximo deseado del largo de las contraseñas

                    fLoc << ",";

                    if (datacom[i].w[j] != '\0') {
                        fLoc << datacom[i].w[j];
                    } else {
                        fLoc << " ";
                    }

                }

                fLoc << "\n";

            }

            fLoc.close();

        }

        // Funcion para pasar de data a txt (CHUNKS)
        void datatotxtc() {

            ofstream fLoc("../datos/procesados/rockyouchunk.txt");

            for (size_t i = 0; i < datacomp.size(); i++) {

                fLoc << datacomp[i].password;

                for (size_t j = 0; j < datacomp[i].chunks.size(); j++) { // Cambiar el 8 para guardar el maximo deseado de chunks
                    fLoc << ",";

                    if (datacomp[i].chunks[j] != "") {
                        fLoc << datacomp[i].chunks[j];
                    } else {
                        fLoc << " ";
                    }

                }

                fLoc << "\n";

            }

            fLoc.close();

        }

        // Funcion para pasar de txt a data
        void txttodata(int maxL, int maxC) {

            ifstream fLoc("../datos/originales/rockyou.txt");
            string line;

            while (getline(fLoc, line)) {

                if (!line.empty() && line.length() <= 16) { // Aca se puede cambiar el largo maximo de los caracteres admitidos

                    Data a;
                    Datac b;
                    a.password = line;
                    a.w.resize(maxL, '\0');
                    b.password = line;
                    b.chunks.resize(maxC);
                    datacom.push_back(a);
                    datacomp.push_back(b);

                }

            }

            fLoc.close();

        }

};

// main
int main() {

    int maxLetras = 16;
    int maxChunks = 8;

    char opcion;
    cout << "Bienvenido al menu de limpieza de datos" << endl;
    
    cout << "Maximo de letras actual: " << maxLetras << " | Desea cambiarlo? (s/n): ";
    cin >> opcion;
    if (opcion == 's' || opcion == 'S') {
        cout << "Ingrese el nuevo maximo de letras: ";
        cin >> maxLetras;
    }

    cout << "Maximo de chunks actual: " << maxChunks << " | Desea cambiarlo? (s/n): ";
    cin >> opcion;
    if (opcion == 's' || opcion == 'S') {
        cout << "Ingrese el nuevo maximo de chunks: ";
        cin >> maxChunks;
    }

    cout << "\nUsando maxLetras = " << maxLetras << ", maxChunks = " << maxChunks << "\n" << endl;


    cout << "Cargando los datos" << endl;

    cleaner datos;
    datos.txttodata(maxLetras, maxChunks);

    cout << "Carga terminada" << endl;

    datos.toletters(maxLetras);
    datos.datatotxt();

    cout << "Letras terminadas" << endl;

    datos.tochunks(maxChunks);
    datos.datatotxtc();

    cout << "chunks terminados" << endl;

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

    // Compilar con g++ -g 01_limpieza.cpp conteos.cpp entropias.cpp -o 01_limpieza.exe

}