#include <iostream>
#include "grid_3d.h" 

#include <ctime> // DA RIMUOVERE

using namespace std;

// Funzione che stampa il layer "layer" della matrice 3D
// Parametri:
// - matrix: la matrice 3D (ad es. glucose o oxygen)
// - layer: il numero (indice) del layer da stampare
// - xsize: il numero di righe del layer
// - ysize: il numero di colonne del layer

void printMatrixLayer(double*** matrix, int layer, int xsize, int ysize) {
    cout << "Layer " << layer << ":\n";
    for (int i = 0; i < xsize; i++) {
        for (int j = 0; j < ysize; j++) {
            cout << matrix[layer][i][j] << "\t";
        }
        cout << "\n";
    }
    cout << "\n";
}

int main() {

    // Da inserire una funzione (main in questo caso)
    std::srand(static_cast<unsigned int>(std::time(nullptr))); 

    int xsize = 4;
    int ysize = 4;
    int zsize = 4;
    int source_num = 1;

    // Creazione della griglia
    Grid grid(xsize, ysize, zsize, source_num);

    // Calcolo centro del tumore
    grid.compute_center();

    // Per quante volte muovo la source
    for (int i = 0; i<3; i++){
        // Esecuzione del metodo fill_sources (che internamente esegue anche sourceMove)
        grid.fill_sources(5.0, 10.0);

        // Stampa dopo l'aggiornamento
        cout << "Dopo fill_sources (prima del nuovo movimento):" << endl;
        for(int i = 0; i < zsize; i++){
            printMatrixLayer(grid.glucose, i, xsize, ysize);
        }
        
        // Scorro nella source list con un solo elemento per stampare
        // la nuova posizione della fonte
        Source * current = grid.sources->head;
        while (current) { 
            cout << "\nPosizione dopo movimeto" << endl;
            cout << "newX = " << current->x << endl;
            cout << "newY = " << current->y << endl;
            cout << "newZ = " << current->z << "\n" << endl;   

            current = current->next;
        }
    }

    return 0;
}