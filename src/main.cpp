#include <iostream>
#include <fstream>
#include <chrono>
using namespace std;

// ================= CONFIGURACION =================
const int MAX_N = 100000;
const int REPS = 30;                       // repeticiones por condicion
const long long SEMILLA = 12345;           // semilla base
const char* COMMIT_HASH = "pendiente";     

// ================= VARIABLES GLOBALES =================
int A[MAX_N];                              // arreglo a ordenar
int aux[MAX_N];                            // arreglo auxiliar de Merge Sort
long long comparaciones, intercambios;     // contadores
int profundidad;                           // solo Merge Sort (en burbuja queda en 0)
long long semilla = SEMILLA;               // estado del generador aleatorio

// ================= BURBUJA (InterDirectoDer) =================
void interDirectoDer(int A[], int n) {
    comparaciones = 0; intercambios = 0; profundidad = 0;
    for (int i = 1; i <= n - 1; i++) {
        for (int j = 0; j < n - i; j++) {
            comparaciones++;
            if (A[j] > A[j + 1]) {
                int temp = A[j];
                A[j] = A[j + 1];
                A[j + 1] = temp;
                intercambios++;
            }
        }
    }
}

// ================= MERGE SORT =================
void mezclar(int A[], int inicio, int medio, int fin) {
    int i = inicio, j = medio + 1, k = inicio;
    while (i <= medio && j <= fin) {
        comparaciones++;
        if (A[i] <= A[j]) {                // <= conserva la estabilidad
            aux[k] = A[i];
            i++;
        } else {
            aux[k] = A[j];
            j++;
        }
        k++;
        intercambios++;                    // movimiento al arreglo auxiliar
    }
    while (i <= medio) { aux[k] = A[i]; i++; k++; intercambios++; }
    while (j <= fin)   { aux[k] = A[j]; j++; k++; intercambios++; }
    for (k = inicio; k <= fin; k++)
        A[k] = aux[k];
}

void dividir(int A[], int inicio, int fin, int nivel) {
    if (nivel > profundidad) profundidad = nivel;
    if (inicio < fin) {
        int medio = (inicio + fin) / 2;
        dividir(A, inicio, medio, nivel + 1);
        dividir(A, medio + 1, fin, nivel + 1);
        mezclar(A, inicio, medio, fin);
    }
}

void mergeSort(int A[], int n) {
    comparaciones = 0; intercambios = 0; profundidad = 0;
    dividir(A, 0, n - 1, 1);
}

// ================= GENERADOR ALEATORIO =================
void fijarSemilla(long long s) {
    semilla = s;
}

int aleatorio(int maximo) {                // devuelve un valor entre 1 y maximo
    semilla = (semilla * 1103515245LL + 12345LL) % 2147483648LL;
    return (int)((semilla / 1024) % maximo) + 1;
}

// ================= PATRONES DE ENTRADA =================
// 1 = aleatorio, 2 = ascendente, 3 = descendente, 4 = casi ordenado, 5 = duplicados
void generar(int A[], int n, int patron) {
    if (patron == 1) {
        for (int i = 0; i < n; i++)
            A[i] = aleatorio(1000000);
    }
    if (patron == 2) {
        for (int i = 0; i < n; i++)
            A[i] = i + 1;
    }
    if (patron == 3) {
        for (int i = 0; i < n; i++)
            A[i] = n - i;
    }
    if (patron == 4) {                     // ascendente con ~5% de elementos movidos
        for (int i = 0; i < n; i++)
            A[i] = i + 1;
        int cambios = n / 40;              // cada cambio mueve 2 elementos
        if (cambios < 1) cambios = 1;
        for (int c = 0; c < cambios; c++) {
            int p = aleatorio(n) - 1;
            int q = aleatorio(n) - 1;
            int temp = A[p];
            A[p] = A[q];
            A[q] = temp;
        }
    }
    if (patron == 5) {                     // 15 valores unicos repetidos
        for (int i = 0; i < n; i++)
            A[i] = aleatorio(15);
    }
}

// ================= VERIFICAR QUE QUEDO ORDENADO =================
bool estaOrdenado(int A[], int n) {
    for (int i = 0; i < n - 1; i++)
        if (A[i] > A[i + 1]) return false;
    return true;
}

// ================= BENCHMARK =================
int main() {
    int tamanos[3] = {1000, 10000, 100000};
    int numTamanos = 3;                    // prueba rapida: 2 (sin 100000)
    const char* nombresAlg[2] = {"Bubble", "Merge"};
    const char* nombresPatron[5] = {"aleatorio", "ascendente", "descendente",
                                    "casi_ordenado", "duplicados"};

    ofstream csv("resultados.csv");
    if (!csv.is_open()) {
        cout << "ERROR: no se pudo crear resultados.csv" << endl;
        return 1;
    }
    csv.setf(ios::fixed);
    csv.precision(6);
    csv << "algoritmo,n,patron,repeticion,tiempo_ms,comparaciones,intercambios,"
        << "profundidad_recursion,semilla,commit_hash" << endl;

    int errores = 0;

    for (int alg = 1; alg <= 2; alg++) {
        int numTamanosAlg = numTamanos;                          // tamanos de este algoritmo
        if (alg == 1 && numTamanosAlg > 2) numTamanosAlg = 2;    // Bubble: sin n = 100000

        for (int patron = 1; patron <= 5; patron++) {
            for (int t = 0; t < numTamanosAlg; t++) {
                int n = tamanos[t];
                cout << nombresAlg[alg - 1] << " | " << nombresPatron[patron - 1]
                     << " | n=" << n << " ..." << endl;

                for (int rep = 1; rep <= REPS; rep++) {
                    long long semillaFila = SEMILLA + rep;   // igual para ambos algoritmos
                    fijarSemilla(semillaFila);
                    generar(A, n, patron);

                    chrono::steady_clock::time_point inicioT = chrono::steady_clock::now();
                    if (alg == 1) interDirectoDer(A, n);
                    else          mergeSort(A, n);
                    chrono::steady_clock::time_point finT = chrono::steady_clock::now();

                    double ms = chrono::duration_cast<chrono::nanoseconds>(finT - inicioT).count()
                                / 1000000.0;

                    if (!estaOrdenado(A, n)) {
                        errores++;
                        cout << "  ERROR: no quedo ordenado (rep " << rep << ")" << endl;
                    }

                    csv << nombresAlg[alg - 1] << "," << n << ","
                        << nombresPatron[patron - 1] << "," << rep << ","
                        << ms << "," << comparaciones << "," << intercambios << ","
                        << profundidad << "," << semillaFila << ","
                        << COMMIT_HASH << endl;
                }
            }
        }
    }

    csv.close();
    cout << endl << "Listo. Errores de ordenacion: " << errores << endl;
    cout << "Archivo generado: resultados.csv" << endl;
    cin.get();
    return 0;
}
