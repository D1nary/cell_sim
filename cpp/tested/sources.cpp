// Print on screen the specified number (size) of Source objects contained 
// in SourceList, along with their randomly generated x, y, and z coordinates.


#include <iostream>
#include <ctime>    // For time()

#include "grid_3d.h"  

using namespace std;

int main() {

   // Generate seed
   std::srand(static_cast<unsigned int>(std::time(nullptr)));
   
   int zsize = 4;
   int xsize = 4;
   int ysize = 4;

   int source_num = 4;
   SourceList * sources;

   Grid grid(zsize, zsize, ysize, source_num);

   sources = grid.getSources();
   
   // Print the number of Source objects in SourceList
   cout << "size = " << sources -> size << endl;

   Source* current = sources -> head;

   while (current != nullptr) {
       // Here you can access the properties of the current node, for example:
       std::cout << "Source at:"  << "\n"
        << "z  = " << current -> z << ", "
        << "x =  " <<  current -> x << ", "
        << "y = " << current -> y << std::endl;

       // Move to the next node
       current = current->next;
   }
}

