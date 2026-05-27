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
#include <chrono>
#include <thread>
#include <cmath>
#include <algorithm>
#include <iomanip>

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
        vector<Datact> newdata;
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
        void tochunks() {

            vector<string> list;

            for(size_t i = 0; i < datacomp.size(); i++) {

                list = chunksdetector(datacomp[i].password);

                for(size_t j = 0; j < list.size() && j < 8; j++) {

                    datacomp[i].chunks[j] = list[j];

                }
                
            }

        }

        // Funcion para partir en letras
        void toletters() {

            for(size_t i = 0; i < datacom.size(); i++) {

                for(size_t j = 0; j < datacom[i].password.length(); j++) {

                    datacom[i].w[j] = datacom[i].password[j];

                }
                
            }

        }

        // Funcion para pasar de data a txt (LETTERS)
        void datatotxt() {

            ofstream fLoc("../datos/procesados/rockyou.txt");

            for (size_t i = 0; i < datacom.size(); i++) {

                fLoc << datacom[i].password;

                for (size_t j = 0; j < 16; j++) {

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

        // // Funcion para pasar de data a txt (CHUNKS)
        // void datatotxtc() {

        //     ofstream fLoc("../datos/procesados/rockyouchunk.txt");

        //     for (size_t i = 0; i < datacomp.size(); i++) {

        //         fLoc << datacomp[i].password;

        //         for (size_t j = 0; j < 8; j++) {

        //             fLoc << ",";

        //             if (datacomp[i].chunks[j] != "") {
        //                 fLoc << datacomp[i].chunks[j];
        //             } else {
        //                 fLoc << " ";
        //             }

        //         }

        //         fLoc << "\n";

        //     }

        //     fLoc.close();

        // }

        // Funcion para pasar de txt a data
        void txttodata() {

            ifstream fLoc("../datos/originales/rockyou.txt");
            string line;
            
            while (getline(fLoc, line)) {

                if (!line.empty() && line.length() <= 16) {

                    Data a;
                    Datac b;
                    a.password = line;
                    b.password = line;
                    datacom.push_back(a);
                    datacomp.push_back(b);

                }

            }

            fLoc.close();

        }

        // Funcion para pasar de txt a data (CREACION DE TABLAS)
        void txttodataNew() {

            ifstream fLoc("../datos/procesados/rockyou.txt");
            string line;
            
            while (getline(fLoc, line)) {

                if (line.empty()) continue;

                stringstream ss(line);
                string token;
                Data a;

                getline(ss, a.password, ',');

                for (size_t i = 0; i < 16; i++) {

                    getline(ss, token, ',');

                    if (!token.empty() && token[0] != ' ') {

                        a.w[i] = token[0];

                    }

                }

                datacom.push_back(a);

            }

            fLoc.close();

            ifstream fLocc("../datos/procesados/rockyouchunk.txt");

            while (getline(fLocc, line)) {

                if (line.empty()) continue;

                stringstream ss(line);
                string token;
                Datac b;

                getline(ss, b.password, ',');

                for (size_t i = 0; i < 8; i++) {

                    getline(ss, token, ',');

                    if (!token.empty() && token[0] != ' ') {

                        b.chunks[i] = token;

                    }

                }

                datacomp.push_back(b);

            }

        }

        // // Funcion para calcular las entropias
        // void makeentropy() {

        //     newdata.resize(datacom.size());

        //     size_t n = datacom.size();
        //     size_t chunks = thread::hardware_concurrency();
        //     size_t sizes = n / chunks;

        //     vector<thread> threads;

        //     for (size_t t = 0; t < chunks; t++) {

        //         size_t a = t * sizes;
        //         size_t b = (t == chunks - 1) ? n : a + sizes;

        //         threads.push_back(thread([this, a, b]() {

        //             for (size_t i = a; i < b; i++) {

        //                 newdata[i].password = datacom[i].password;
        //                 newdata[i].entropyS = entropyShannon(datacom[i].password);
        //                 newdata[i].entropyD = entropyDensity(datacom[i].password);

        //             }

        //         }));

        //     }

        //     for (auto& t : threads) t.join();

        // }

        // Funcion para calcular la distribucion de los caracteres
        void makedist() {

            for (size_t pos = 0; pos < 16; pos++) {

                vector<char> chars;

                for (size_t j = 0; j < datacom.size(); j++) {

                    chars.push_back(datacom[j].w[pos]);

                }

                Datadist d;
                d.map = contDis(chars);
                distribution.push_back(d);

            }

        }

        // Funcion para calcular la distribucion de los primeros numeros de los chunks
        void makebenford() {

            for (size_t pos = 0; pos < 8; pos++) {

                vector<string> chunks;

                for (size_t j = 0; j < datacomp.size(); j++) {

                    chunks.push_back(datacomp[j].chunks[pos]);

                }

                Databenf b;
                b.benfC = contChunks(chunks);
                benford.push_back(b);

            }

        }

        // Funcion para calcular y guardar rockyouedistfreq desde el dataset de frecuencias
        void makedistFreq() {

            ifstream fFreq("../datos/originales/rockyou-with-count.txt");
            string line;

            vector<unordered_map<char, int>> distFreq(16);

            while (getline(fFreq, line)) {

                if (line.empty()) continue;

                istringstream iss(line);
                size_t freq = 0;
                string pwd;
                iss >> freq >> pwd;

                if (pwd.empty() || pwd.length() > 16) continue;

                for (size_t j = 0; j < pwd.length(); j++) {

                    distFreq[j][pwd[j]] += freq;

                }

            }

            fFreq.close();

            ofstream fDist("../datos/procesados/rockyouedistfreq.txt");

            fDist << "char";
            for (size_t i = 1; i <= 16; i++) fDist << ",pos" << i;
            fDist << "\n";

            unordered_set<char> allChars;
            for (size_t i = 0; i < 16; i++)
                for (auto& pair : distFreq[i])
                    allChars.insert(pair.first);

            for (char c : allChars) {

                if ((unsigned char)c > 127) continue;
                fDist << c;

                for (size_t j = 0; j < 16; j++) {

                    fDist << ",";

                    if (distFreq[j].count(c))
                        fDist << distFreq[j][c];
                    else
                        fDist << "0";

                }

                fDist << "\n";

            }

            fDist.close();

        }

        // Funcion para calcular y guardar rockyoubenfordfreq desde el dataset de frecuencias
        void makebenfordFreq() {

            ifstream fFreq("../datos/originales/rockyou-with-count.txt");
            string line;

            vector<unordered_map<int, int>> benfFreq(8);

            while (getline(fFreq, line)) {

                if (line.empty()) continue;

                istringstream iss(line);
                size_t freq = 0;
                string pwd;
                iss >> freq >> pwd;

                if (pwd.empty() || pwd.length() > 16) continue;

                vector<string> chunks = chunksdetector(pwd);

                for (size_t j = 0; j < chunks.size() && j < 8; j++) {

                    if (!chunks[j].empty() && isdigit(chunks[j][0])) {

                        int firstDigit = chunks[j][0] - '0';
                        benfFreq[j][firstDigit] += freq;

                    }

                }

            }

            fFreq.close();

            ofstream fBenf("../datos/procesados/rockyoubenfordfreq.txt");

            fBenf << "digit";
            for (size_t i = 1; i <= 8; i++) fBenf << ",chunk" << i;
            fBenf << "\n";

            for (size_t d = 0; d <= 9; d++) {

                fBenf << d;

                for (size_t j = 0; j < 8; j++) {

                    fBenf << ",";

                    if (benfFreq[j].count(d))
                        fBenf << benfFreq[j][d];
                    else
                        fBenf << "0";

                }

                fBenf << "\n";

            }

            fBenf.close();

        }

        // Funcion para pasar de data a txt (CREACION DE TABLAS)
        void datatotxtNew() {

            // // Guardar entropias
            // ofstream fEnt("../datos/procesados/rockyoue.txt");
            // fEnt << "password,entropyS,entropyD\n";

            // for (size_t i = 0; i < newdata.size(); i++) {

            //     fEnt << newdata[i].password << "," << newdata[i].entropyS << "," << newdata[i].entropyD << "\n";
            
            // }

            // fEnt.close();
            
            // Guardar distribucion de caracteres por posicion
            ofstream fDist("../datos/procesados/rockyouedist.txt");

            fDist << "char";
            for (size_t i = 1; i <= 16; i++) fDist << ",pos" << i;
            fDist << "\n";

            unordered_set<char> allChars;
            for (size_t i = 0; i < distribution.size(); i++)
                for (auto& pair : distribution[i].map)
                    allChars.insert(pair.first);

            for (char c : allChars) {

                if ((unsigned char)c > 127) continue;
                fDist << c;

                for (size_t j = 0; j < 16; j++) {

                    fDist << ",";

                    if (distribution[j].map.count(c))
                        fDist << distribution[j].map[c];
                    else
                        fDist << "0";

                }

                fDist << "\n";

            }

            fDist.close();

            // Guardar distribucion de Benford por posicion de chunk
            ofstream fBenf("../datos/procesados/rockyoubenford.txt");

            fBenf << "digit";
            for (size_t i = 1; i <= 8; i++) fBenf << ",chunk" << i;
            fBenf << "\n";

            for (size_t d = 0; d <= 9; d++) {

                fBenf << d;

                for (size_t j = 0; j < 8; j++) {

                    fBenf << ",";

                    if (benford[j].benfC.count(d))
                        fBenf << benford[j].benfC[d];
                    else
                        fBenf << "0";

                }

                fBenf << "\n";
            
            }

            fBenf.close();
            
        }



    // Funcion para calcular estadisticas de longitud ponderadas por frecuencia
    void makeLengthStatsFreq() {

        ifstream fFreq("../datos/originales/rockyou-with-count.txt");
        string line;

        unordered_map<int, long long> freqByLen;
        long long total = 0;

        while (getline(fFreq, line)) {

            if (line.empty()) continue;

            istringstream iss(line);
            long long freq = 0;
            string pwd;
            iss >> freq >> pwd;

            if (pwd.empty()) continue;

            freqByLen[(int)pwd.length()] += freq;
            total += freq;

        }

        fFreq.close();

        // Media
        double mean = 0;
        for (auto& p : freqByLen) mean += p.first * (double)p.second / total;

        // Varianza, sesgo, curtosis
        double var = 0, skew = 0, kurt = 0;
        for (auto& p : freqByLen) {
            double d = p.first - mean;
            double w = (double)p.second / total;
            var  += w * d * d;
            skew += w * d * d * d;
            kurt += w * d * d * d * d;
        }
        double sd = sqrt(var);
        skew = skew / (sd * sd * sd);
        kurt = kurt / (var * var) - 3.0;

        // Moda
        int moda = 0;
        long long modaCount = 0;
        for (auto& p : freqByLen) {
            if (p.second > modaCount) { modaCount = p.second; moda = p.first; }
        }

        // Ordenar por longitud para percentiles y ECDF
        vector<pair<int, long long>> sorted(freqByLen.begin(), freqByLen.end());
        sort(sorted.begin(), sorted.end());

        auto percentile = [&](double p) -> int {
            long long target = (long long)(p * total);
            long long acc = 0;
            for (auto& x : sorted) {
                acc += x.second;
                if (acc >= target) return x.first;
            }
            return sorted.back().first;
        };

        int p10 = percentile(0.10);
        int p25 = percentile(0.25);
        int p50 = percentile(0.50);
        int p75 = percentile(0.75);
        int p90 = percentile(0.90);
        int p95 = percentile(0.95);
        int p99 = percentile(0.99);

        // Escritura
        ofstream fOut("../datos/procesados/rockyoulengthstats.txt");

        fOut << "=== Estadisticas de longitud (ponderadas por frecuencia) ===\n\n";
        fOut << "Total passwords (con repeticion): " << total << "\n";
        fOut << "Media:    " << fixed << setprecision(4) << mean << "\n";
        fOut << "Mediana:  " << p50 << "\n";
        fOut << "Moda:     " << moda << " (" << modaCount << " ocurrencias)\n";
        fOut << "Varianza: " << fixed << setprecision(4) << var << "\n";
        fOut << "Desv std: " << fixed << setprecision(4) << sd << "\n";
        fOut << "Sesgo:    " << fixed << setprecision(4) << skew << "\n";
        fOut << "Curtosis: " << fixed << setprecision(4) << kurt << " (exceso)\n";

        fOut << "\n=== Percentiles ===\n";
        fOut << "P10: " << p10 << "\n";
        fOut << "P25: " << p25 << "\n";
        fOut << "P50: " << p50 << "\n";
        fOut << "P75: " << p75 << "\n";
        fOut << "P90: " << p90 << "\n";
        fOut << "P95: " << p95 << "\n";
        fOut << "P99: " << p99 << "\n";

        fOut << "\n=== Histograma ===\n";
        fOut << "longitud,frecuencia,proporcion\n";
        for (auto& p : sorted) {
            fOut << p.first << "," << p.second << ","
                << fixed << setprecision(6) << (double)p.second / total << "\n";
        }

        fOut << "\n=== ECDF ===\n";
        fOut << "longitud,ecdf\n";
        long long acc = 0;
        for (auto& p : sorted) {
            acc += p.second;
            fOut << p.first << "," << fixed << setprecision(6) << (double)acc / total << "\n";
        }

        fOut.close();

    }

};

// main
int main() {

    cleaner datos;
    datos.txttodataNew();

    cout << "termino" << endl;

    // datos.makedist();
    // datos.makebenford();
    // datos.datatotxtNew();
    // datos.toletters();
    // datos.datatotxt();

    // datos.makedistFreq();
    // datos.makebenfordFreq();

    datos.makeLengthStatsFreq();

    // // datos.makeentropy();
    // // datos.tochunks();
    // // datos.datatotxtc();

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