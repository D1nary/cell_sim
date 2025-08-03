/*
 * Test of the behavior of the extreme values in the neigh_counts matrix.
 * The matrix is initialized to 0, and a specific layer is printed.
 * This allows observation of the correct application of a bias at the boundary values.
 */

 #include <iostream>
 #include "grid_3d.h" 
 
 using namespace std;
 
 int main() {
     // 4x4x4 Matrix
     int zsize = 4;
     int xsize = 4;
     int ysize = 4;
 
     int *** neigh_counts;
 
     Grid grid(zsize, zsize, ysize, 0);
 
     // Select the layer to print
     int z_layer = 0;
     cout << "neigh_counts matrix for layer z = " << z_layer << ":\n";
 
     neigh_counts = grid.getNeighCounts();
     
     // Iterate over the rows (x) and columns (y) of the chosen layer and print the value of each element
     for (int i = 0; i < xsize; i++) {
         for (int j = 0; j < ysize; j++) {
             cout << neigh_counts[z_layer][i][j] << "\t";
         }
         cout << "\n";
     }
 
     return 0;
 }
 