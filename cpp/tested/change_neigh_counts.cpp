/*
 * Given the initial state of the neigh_counts matrix and the coordinates of a voxel within it,
 * this program updates the neighbor count of the voxels adjacent to the selected voxel 
 * using the change_neigh_counts function.
 */

 #include <iostream>
 #include <ctime> // For time()
 
 #include "grid_3d.h"  
 
 using namespace std;
 
 int main() {
 
     // Generate seed
     std::srand(static_cast<unsigned int>(std::time(nullptr)));
 
     int xsize = 4;
     int ysize = 4;
     int zsize = 4;
     int source_num = 4;
     int *** neigh_counts;
     
     // Build the grid; pay attention to the order of parameters:
     // Grid(int xsize, int ysize, int zsize, int sources_num)
     Grid grid(xsize, ysize, zsize, source_num);
     neigh_counts = grid.getNeighCounts();
 
     // Example: update the neighbor count of voxel (2,2,1) by incrementing its neighbors by 1
     grid.change_neigh_counts(2, 2, 1, 1);
 
     // Print to screen each layer (z-axis) of the neigh_counts matrix:
     for (int z = 0; z < zsize; z++) {
         cout << "Layer z = " << z << ":\n";
         for (int x = 0; x < xsize; x++) {
             for (int y = 0; y < ysize; y++) {
                 cout << neigh_counts[z][x][y] << "\t";
             }
             cout << "\n";
         }
         cout << "\n";
     }
 
     return 0;
 }
 