#include <iostream>
#include <cmath>

using namespace std;

void tumor_creation(int dimX, int dimY, int dimZ) {
    // Allocazione dinamica della griglia 3D nella forma tumor_grid[k][i][j]
    int ***tumor_grid = new int**[dimZ];
    for (int k = 0; k < dimZ; k++) {
        tumor_grid[k] = new int*[dimX];
        for (int i = 0; i < dimX; i++) {
            tumor_grid[k][i] = new int[dimY];
        }
    }
    
    // Calcolo del centro in ciascuna dimensione
    int centerX = dimX / 2;
    int centerY = dimY / 2;
    int centerZ = dimZ / 2;
    
    // Definizione dei raggi
    double tumor_radius = 2.0;
    double health_radius = 4.0;
    
    // Calcolo della distanza per ogni voxel e assegnazione dei valori
    for (int k = 0; k < dimZ; k++) {
        for (int i = 0; i < dimX; i++) {
            for (int j = 0; j < dimY; j++) {
                double dx = i - centerX;
                double dy = j - centerY;
                double dz = k - centerZ;
                double distance = sqrt(dx * dx + dy * dy + dz * dz);
                
                if (distance <= tumor_radius) {
                    tumor_grid[k][i][j] = -1;
                } else if (distance <= health_radius) {
                    tumor_grid[k][i][j] = 1;
                } else {
                    tumor_grid[k][i][j] = 0;
                }
            }
        }
    }
    
    // Stampa di ogni layer della griglia
    for (int k = 0; k < dimZ; k++) {
        cout << "Layer " << k << ":\n";
        for (int i = 0; i < dimX; i++) {
            cout << "[";
            for (int j = 0; j < dimY; j++) {
                cout << tumor_grid[k][i][j];
                if (j < dimY - 1)
                    cout << " ";
            }
            cout << "]\n";
        }
        cout << "\n";
    }
    
    // Deallocazione della memoria
    for (int k = 0; k < dimZ; k++) {
        for (int i = 0; i < dimX; i++) {
            delete[] tumor_grid[k][i];
        }
        delete[] tumor_grid[k];
    }
    delete[] tumor_grid;
}

int main() {
    // Dimensioni della griglia (modificabili)
    int dimX = 10, dimY = 10, dimZ = 10;
    tumor_creation(dimX, dimY, dimZ);
    return 0;
}
