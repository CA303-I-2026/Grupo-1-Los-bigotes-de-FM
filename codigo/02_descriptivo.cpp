// 02_descriptivo.cpp
// Analisis descriptivo de los datos
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
#include <unordered_set>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <thread>

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

// Clase descriptivo
class descriptivo {

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

        // Funcion para calcular las entropias
        void makeentropy() {

            newdata.resize(datacom.size());

            size_t n = datacom.size();
            size_t chunks = thread::hardware_concurrency();
            size_t sizes = n / chunks;

            vector<thread> threads;

            for (size_t t = 0; t < chunks; t++) {

                size_t a = t * sizes;
                size_t b = (t == chunks - 1) ? n : a + sizes;

                threads.push_back(thread([this, a, b]() {

                    for (size_t i = a; i < b; i++) {

                        newdata[i].password = datacom[i].password;
                        newdata[i].entropyS = entropyShannon(datacom[i].password);
                        newdata[i].entropyD = entropyDensity(datacom[i].password);

                    }

                }));

            }

            for (auto& t : threads) t.join();

        }

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

            // Guardar entropias
            ofstream fEnt("../datos/procesados/rockyoue.txt");
            fEnt << "password,entropyS,entropyD\n";

            for (size_t i = 0; i < newdata.size(); i++) {

                fEnt << newdata[i].password << "," << newdata[i].entropyS << "," << newdata[i].entropyD << "\n";

            }

            fEnt.close();

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

        // Funcion para calcular mascaras de formato ponderadas por frecuencia
        void makeMasksFreq() {

            ifstream fFreq("../datos/originales/rockyou-with-count.txt");
            string line;

            unordered_map<string, long long> maskCount;
            long long total = 0;

            while (getline(fFreq, line)) {

                if (line.empty()) continue;

                istringstream iss(line);
                long long freq = 0;
                string pwd;
                iss >> freq >> pwd;

                if (pwd.empty() || pwd.length() > 16) continue;

                // Construir mascara
                string mask = "";
                for (size_t i = 0; i < pwd.length(); i++) {

                    if (isupper(pwd[i]))       mask += 'U';
                    else if (islower(pwd[i]))  mask += 'L';
                    else if (isdigit(pwd[i]))  mask += 'D';
                    else                       mask += 'S';

                }

                maskCount[mask] += freq;
                total += freq;

            }

            fFreq.close();

            // Ordenar mascaras por frecuencia descendente
            vector<pair<string, long long>> maskSorted(maskCount.begin(), maskCount.end());
            sort(maskSorted.begin(), maskSorted.end(), [](const pair<string,long long>& a, const pair<string,long long>& b) {
                return a.second > b.second;
            });

            // Patrones comprimidos
            unordered_map<string, long long> patternCount;

            for (size_t i = 0; i < maskSorted.size(); i++) {

                string mask = maskSorted[i].first;
                string pattern = "";

                char prev = mask[0];
                int run = 1;
                for (size_t j = 1; j < mask.length(); j++) {
                    if (mask[j] == prev) {
                        run++;
                    } else {
                        pattern += prev;
                        pattern += to_string(run);
                        prev = mask[j];
                        run = 1;
                    }
                }
                pattern += prev;
                pattern += to_string(run);

                patternCount[pattern] += maskSorted[i].second;

            }

            // Ordenar patrones por frecuencia descendente
            vector<pair<string, long long>> patSorted(patternCount.begin(), patternCount.end());
            sort(patSorted.begin(), patSorted.end(), [](const pair<string,long long>& a, const pair<string,long long>& b) {
                return a.second > b.second;
            });

            // Escritura resumen
            ofstream fSum("../datos/procesados/rockyoumasksresumen.txt");

            fSum << "=== Mascaras de formato (ponderadas por frecuencia) ===\n\n";
            fSum << "Total passwords (con repeticion): " << total << "\n";
            fSum << "Mascaras unicas encontradas: " << maskSorted.size() << "\n\n";

            fSum << "=== Cobertura acumulada top mascaras ===\n";
            fSum << "top_n,cobertura\n";
            long long acc = 0;
            for (size_t i = 0; i < maskSorted.size(); i++) {
                acc += maskSorted[i].second;
                if (i < 10 || i == 24 || i == 49 || i == 99) {
                    fSum << (i+1) << "," << fixed << setprecision(6) << (double)acc / total << "\n";
                }
            }

            fSum << "\n=== Patrones comprimidos (runs) ===\n";
            fSum << "patron,frecuencia,proporcion\n";
            for (size_t i = 0; i < patSorted.size(); i++) {
                fSum << patSorted[i].first << "," << patSorted[i].second << ","
                    << fixed << setprecision(6) << (double)patSorted[i].second / total << "\n";
            }

            fSum.close();

            // Escritura frecuencias
            ofstream fFreqOut("../datos/procesados/rockyoumasks.txt");

            fFreqOut << "mascara,frecuencia,proporcion\n";
            for (size_t i = 0; i < maskSorted.size(); i++) {
                fFreqOut << maskSorted[i].first << "," << maskSorted[i].second << ","
                        << fixed << setprecision(6) << (double)maskSorted[i].second / total << "\n";
            }

            fFreqOut.close();

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
            vector<pair<int, long long>> lenSorted(freqByLen.begin(), freqByLen.end());
            sort(lenSorted.begin(), lenSorted.end());

            auto percentile = [&](double p) -> int {
                long long target = (long long)(p * total);
                long long acc = 0;
                for (auto& x : lenSorted) {
                    acc += x.second;
                    if (acc >= target) return x.first;
                }
                return lenSorted.back().first;
            };

            int p10 = percentile(0.10);
            int p25 = percentile(0.25);
            int p50 = percentile(0.50);
            int p75 = percentile(0.75);
            int p90 = percentile(0.90);
            int p95 = percentile(0.95);
            int p99 = percentile(0.99);

            // Escritura resumen
            ofstream fSum("../datos/procesados/rockyoulengthstats.txt");

            fSum << "=== Estadisticas de longitud (ponderadas por frecuencia) ===\n\n";
            fSum << "Total passwords (con repeticion): " << total << "\n";
            fSum << "Media:    " << fixed << setprecision(4) << mean << "\n";
            fSum << "Mediana:  " << p50 << "\n";
            fSum << "Moda:     " << moda << " (" << modaCount << " ocurrencias)\n";
            fSum << "Varianza: " << fixed << setprecision(4) << var << "\n";
            fSum << "Desv std: " << fixed << setprecision(4) << sd << "\n";
            fSum << "Sesgo:    " << fixed << setprecision(4) << skew << "\n";
            fSum << "Curtosis: " << fixed << setprecision(4) << kurt << " (exceso)\n";

            fSum << "\n=== Percentiles ===\n";
            fSum << "P10: " << p10 << "\n";
            fSum << "P25: " << p25 << "\n";
            fSum << "P50: " << p50 << "\n";
            fSum << "P75: " << p75 << "\n";
            fSum << "P90: " << p90 << "\n";
            fSum << "P95: " << p95 << "\n";
            fSum << "P99: " << p99 << "\n";

            fSum.close();

            // Escritura frecuencias
            ofstream fFreqOut("../datos/procesados/rockyoulengthfreq.txt");

            fFreqOut << "=== Histograma ===\n";
            fFreqOut << "longitud,frecuencia,proporcion\n";
            for (auto& p : lenSorted) {
                fFreqOut << p.first << "," << p.second << ","
                    << fixed << setprecision(6) << (double)p.second / total << "\n";
            }

            fFreqOut << "\n=== ECDF ===\n";
            fFreqOut << "longitud,ecdf\n";
            long long acc = 0;
            for (auto& p : lenSorted) {
                acc += p.second;
                fFreqOut << p.first << "," << fixed << setprecision(6) << (double)acc / total << "\n";
            }

            fFreqOut.close();

        }

};

// main
int main() {

    descriptivo datos;
    datos.txttodataNew();

    cout << "carga terminada" << endl;

    datos.makedist();
    datos.makebenford();
    datos.makeentropy();
    datos.datatotxtNew();

    cout << "dist, benford y entropias terminadas" << endl;

    datos.makedistFreq();
    datos.makebenfordFreq();

    cout << "dist y benford freq terminadas" << endl;

    datos.makeLengthStatsFreq();

    cout << "length stats terminadas" << endl;

    datos.makeMasksFreq();

    cout << "mascaras terminadas" << endl;

    return 0;

    // Compilar con g++ -g 02_descriptivo.cpp conteos.cpp entropias.cpp -o 02_descriptivo.exe

}