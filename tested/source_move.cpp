#include <iostream>
#include "grid_3d.h" 

#include <ctime>

using namespace std;

// Utility function to print a specific layer of a 3D matrix
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
    
    std::srand(static_cast<unsigned int>(std::time(nullptr))); 

    int xsize = 4;
    int ysize = 4;
    int zsize = 4;
    int source_num = 1;
    
    SourceList * sources;
    double *** glucose;

    // Grid creation
    Grid grid(xsize, ysize, zsize, source_num);

    sources = grid.getSources();
    glucose = grid.getGlucose();

    // Compute the tumor center
    grid.compute_center();

    // Number of source movements
    for (int i = 0; i < 3; i++) {
        // Execute fill_sources (which internally also calls sourceMove)
        grid.fill_sources(5.0, 10.0);

        // Print matrix after the update
        cout << "After fill_sources (before next movement):" << endl;
        for(int i = 0; i < zsize; i++){
            printMatrixLayer(glucose, i, xsize, ysize);
        }
        
        // Traverse the source list (only one element in this case) to print the new position
        Source * current = sources->head;
        while (current) { 
            cout << "\nPosition after movement:" << endl;
            cout << "newX = " << current->x << endl;
            cout << "newY = " << current->y << endl;
            cout << "newZ = " << current->z << "\n" << endl;   

            current = current->next;
        }
    }

    return 0;
}
