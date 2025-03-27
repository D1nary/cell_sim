#include <algorithm>
#include "grid_3d.h"
#include <assert.h> 
#include <math.h> 
#include <iostream>

#include <cstdlib>  // For rand() and srand()

using namespace std;


/**
 * Constructor of CellList
 *
 * CellLists are linked lists of CellNodes that are on each pixel of the Grid
 *
 */
CellList::CellList():head(nullptr), tail(nullptr), size(0), oar_count(0), ccell_count(0) {}

/**
 * Destructor of CellList
 *
 */
CellList::~CellList() {
    CellNode * current = head;
    CellNode * next;
    
    // Delete all the CellNodes and Cells in the CellList
    while (current){ // Continue iteration while 'current' is not a null pointer (nullptr)

        // Accesses the members of an object through a pointer.
        // The first 'next' refers to the pointer declared in the destructor,
        // while the second 'next' refers to a member of the CellNode class.
        // The first 'next' will store the value of the 'next' member of the current node (current->next).
        next = current -> next;
        
        // Deallocating the memory associated with the 'cell' member of the current CellNode object.
        delete current -> cell;
        
        // Deallocating the memory of the CellNode object
        delete current;
        current = next;
    }
}


/**
 * Add a CellNode containing a cell to the CellList
 *
 * It is added at the start of the list if it is contains a Cancer Cell and at the end otherwise
 *
 * @param newNode The CellNode containing the Cell that we want to add to the CellList
 * @param type The type of the Cell
 */
void CellList::add(CellNode * newNode, char type){
    // If the expression (assert parameter 'newNode') is true, the programm continues
    // Otherwise return an error
    assert(newNode);

    if (size == 0){
        head = newNode;
        tail = newNode;
        newNode -> next = nullptr;
    }
    else if (type == 'h' || type == 'o'){ // or
        tail -> next = newNode; // Adding the node at the end
        tail = newNode;
        newNode -> next = nullptr;
    } else if(type == 'c'){
        newNode -> next = head;
        head = newNode; // Adding the node at the end 
    }
    if (type == 'o')
        oar_count++;
    if (type == 'c')
        ccell_count++;
    size++;
}


/**
 * Create a CellNode container for the Cell and add it to the CellList
 *
 * @param cell The cell that we want to add to the CellList
 * @param type The type of the Cell
 */
void CellList::add(Cell *cell, char type) {
    CellNode * newNode = new CellNode; // Create a CellNode object
    assert(cell);
    newNode -> cell = cell;
    newNode -> type = type;
    add(newNode, type);
}

/**
 * Create a CellNode container for the Cell and add it to the CellList, with the coordinates of the cell on the grid
 *
 * @param cell The cell that we want to add to the CellList
 * @param type The type of the Cell
 * @param x The x coordinate of the cell on the grid
 * @param y The y coordinate of the cell on the grid
 * @param z The z coordinate (layer) of the cell on the grid
 */
void CellList::add(Cell *cell, char type, int x, int y, int z) {

    // Creating a new CellNode node
    CellNode * newNode = new CellNode;
    assert(cell);
    newNode -> cell = cell;
    newNode -> type = type;
    newNode -> x = x;
    newNode -> y = y;
    newNode -> z = z;
    add(newNode, type);
}

/**
 * Go through the CellList by deleting and removing cells that have been killed by lack or nutrients or radiation
 *
 * Ensures that the order of cells (cancer cells first) is kept and that the links stay sound to avoid segfaults
 * 
 * The loop scans each node (while(current)):
 * 1. If the cell is dead, the node is removed from memory (if).
 * 2. If it’s the FIRST live cell found (i.e., found_head = false), we update head and tail (else if).
 * 3. If the cell is alive (but not the first), it means we are processing the rest of the list. 
 *    tail is updated to maintain the reference to the last live node. The pointers are updated accordingly.
 */
void CellList::deleteDeadAndSort(){
    bool found_head = false; // Used to ensure that we have a head to the list at the end of traversal
    CellNode * current = head;
    CellNode ** previous_next_pointer;
    
    while(current){ // Iterating over the cells in the list
        if (!(current -> cell -> alive)){ // Dead cell
            delete current->cell;
            if (current -> type == 'o')
                oar_count--;
            if (current -> type == 'c')
                ccell_count--;
            CellNode * toDel = current;
            current = current -> next;
            delete toDel;
            size--;

        // Checking that found_head is false
        // If found_head is false, it means i found the first live node since the previous condition is not met.
        } else if (!found_head){                 
            head = current;
            tail = current;
            
            previous_next_pointer = & (current -> next); // & returns the address of current -> next                                       
            current = current -> next;

            found_head = true;
        }
        else{
            tail = current;

            // Modifying the content of 'next'.
            // Now 'next' corresponds to the address of 'current'.
            *previous_next_pointer = current;

            previous_next_pointer = & (current -> next);
            // Traversing the CellList
            current = current -> next;
        }
    }
    // If no live nodes were found
    if (!found_head){

        // Check if the expression size == 0 is true.
        assert(size == 0);
        head = nullptr;
        tail = nullptr;
    } else{
        // If there is at least one alive node
        tail -> next = nullptr;
    }
}

/**
 * Compute a weighted sum of the cells in this cell list
 *
 * Cancer cells have a weight of -1, healthy cells of 1 and OAR cells have a weight corresponding to the worth assigned
 * to them in the class OARCell
 * 
 * @return The weighted sum
 */
int CellList::CellTypeSum(){
    if (size == 0)
        return 0;
    if(ccell_count > 0)
        return -ccell_count;
    else
        return size;
}

/**
 * Sets all the OARCells present in this list out of quiescence
 *
 */
void CellList::wake_oar(){
    if (oar_count == 0)
        return;
    CellNode * current = head;
    while(current){
        if (current -> type == 'o')
            current -> cell -> wake();
        current = current -> next;
    }
}

/**
 * Constructor of SourceList
 *
 * A SourceList is a linked list of Source (nutrient sources) objects, which ensures that they are easy to iterate and
 * that we can easily add or remove sources of nutrients to or from the simulation
 */
SourceList::SourceList():head(nullptr), tail(nullptr), size(0) {}


/**
 * Destructor of SourceList
 */
SourceList::~SourceList() {
    Source * current = head;
    Source * next;
    while (current){
        next = current -> next;
        delete current;
        current = next;
    }
}

/**
 * Add a source of nutrients to the SourceList with coordinates (x, y) on the grid
 *
 * @param x The x coordinate of the Source on the grid
 * @param y The y coordinate of the Source on the grid
 * @param z The z coordinate of the Source on the grid (layer)
 */
void SourceList::add(int x, int y, int z) {
    // Dynamic allocation of a Source object (new Source) on the heap  
    // This new object will be pointed to by the pointer newNode
    Source * newNode = new Source; 
    newNode -> x = x;
    newNode -> y = y;
    newNode -> z = z;
    newNode -> next = nullptr;
    if (size == 0){
        head = newNode;
    } else{
        // I set the next of the second-to-last node to the new node
        tail -> next = newNode;   
    }
    tail = newNode;
    size++;
}

/**
 * Constructor of Grid without an OAR zone
 *
 * The grid is the base of the simulation, it is made out of 3 superimposed 3D matrixs : one contains the CellLists for
 * each pixel, one contains the glucose amount on each pixel and one contains the oxygen amount on each pixel.
 *
 * @param xsize The number of rows of the grid 
 * @param ysize The number of columns of the grid
 * @param zsize The number of layers of the grid
 * @param sources_num The number of nutrient sources that should be added to the grid
 * 
 */
Grid::Grid(int xsize, int ysize, int zsize, int sources_num):xsize(xsize), ysize(ysize), zsize(zsize), oar(nullptr){
    // Dynamic allocation of the 3D arrays following the convention [z][x][y]
    cells = new CellList**[zsize];
    glucose = new double**[zsize];
    glucose_helper = new double**[zsize];
    oxygen = new double**[zsize];
    oxygen_helper = new double**[zsize];
    neigh_counts = new int**[zsize];

    for(int k = 0; k < zsize; k++) { // z layers
        cells[k] = new CellList*[xsize];
        glucose[k] = new double*[xsize];
        glucose_helper[k] = new double*[xsize];
        oxygen[k] = new double*[xsize];
        oxygen_helper[k] = new double*[xsize];
        neigh_counts[k] = new int*[xsize];

        for(int i = 0; i < xsize; i++) { // Rows (x)
            cells[k][i] = new CellList[ysize];
            glucose[k][i] = new double[ysize];
            glucose_helper[k][i] = new double[ysize];
            oxygen[k][i] = new double[ysize];
            oxygen_helper[k][i] = new double[ysize];
            neigh_counts[k][i] = new int[ysize](); // Initialization to 0 using "()"

            // Initialization of glucose and oxygen values
            std::fill_n(glucose[k][i], ysize, 100.0); // 1E-6 mg O'Neil
            std::fill_n(oxygen[k][i], ysize, 1000.0); // 1 E-6 ml Jalalimanesh
        }
    }

    // Adding offset to the matrix edges
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {

                // Calculating possible values based on position
                // Syntax: condition ? value_if_true : value_if_false;
                int poss_z = (k == 0 || k == zsize - 1) ? 2 : 3;
                int poss_x = (i == 0 || i == xsize - 1) ? 2 : 3;
                int poss_y = (j == 0 || j == ysize - 1) ? 2 : 3;
                
                // Product of possible values
                int prod = poss_z * poss_x * poss_y;
                // Calculating value as: valore = n_max - neighbors = 27 - prod
                int value = 27 - prod;
                
                // Since every element is initialized to 0, we can simply assign:
                neigh_counts[k][i][j] = value;
            }
        }
    }


    // Creation of nutrients list
    sources = new SourceList();

    for (int i = 0; i < sources_num; i++) {
        // Set the sources at random locations on the grid
        sources->add(rand() % xsize, rand() % ysize, rand() % zsize);
    }
}
 /**
 * Constructor of Grid with an OAR zone
 *
 * The grid is the base of the simulation, now made up of a 3D matrices:
 * one contains the CellLists for each voxel, one contains the glucose amount and one contains the oxygen amount.
 * The OAR zone is represented by coordinates that define a cuboid within the grid.
 * Every voxel in that cuboid will contain an OARCell.
 *
 * @param xsize The number of rows of the grid
 * @param ysize The number of columns of the grid
 * @param zsize The number of layers of the grid
 * @param sources_num The number of nutrient sources that should be added to the grid
 * @param oar_zone The OARZone object that contains the cuboid's coordinates
 */
Grid::Grid(int xsize, int ysize, int zsize, int sources_num, OARZone * oar_zone)
    : Grid(xsize, ysize, zsize, sources_num)  // Richiama il costruttore base 3D
{
    oar = oar_zone;
}

/**
 * Destructor of Grid
 *
 */
Grid::~Grid() {
    // Deallocate the 3D matrices
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            // Deallocate the columns of the matrices
            delete[] cells[k][i];
            delete[] glucose[k][i];
            delete[] oxygen[k][i];
            delete[] glucose_helper[k][i];
            delete[] oxygen_helper[k][i];
            delete[] neigh_counts[k][i];
        }
        // Deallocate the rows in the matrices
        delete[] cells[k];
        delete[] glucose[k];
        delete[] oxygen[k];
        delete[] glucose_helper[k];
        delete[] oxygen_helper[k];
        delete[] neigh_counts[k];
    }
    // Deallocate the layer arrays
    delete[] cells;
    delete[] glucose;
    delete[] oxygen;
    delete[] glucose_helper;
    delete[] oxygen_helper;
    delete[] neigh_counts;

    // Deallocates the SourceList
    delete sources;
}

/**
 * Adds "val" to the neighbor count of the voxel at coordinates (x, y, z)
 * 
 * The function updates the counts of the 26 adjacent voxels (around the central voxel)
 *
 * @param x The x-coordinate of the central voxel
 * @param y The y-coordinate of the central voxel
 * @param z The z-coordinate of the central voxel
 * @param val The value to be added (or subtracted, if negative) to the neighbor count
 */
void Grid::change_neigh_counts(int x, int y, int z, int val) {
    // Loop over all possible variations along the z-axis (-1, 0, 1)
    for (int dz = -1; dz <= 1; dz++) {
        int nz = z + dz;
        if (nz < 0 || nz >= zsize)
            continue;  // If we are out of bounds in z, skip this iteration

        // Loop over variations along the x-axis (-1, 0, 1)
        for (int dx = -1; dx <= 1; dx++) {
            int nx = x + dx;
            if (nx < 0 || nx >= xsize)
                continue;  // If we are out of bounds in x, skip this iteration

            // Loop over variations along the y-axis (-1, 0, 1)
            for (int dy = -1; dy <= 1; dy++) {
                int ny = y + dy;
                if (ny < 0 || ny >= ysize)
                    continue;  // If we are out of bounds in y, skip this iteration

                // Exclude the central voxel (no offset)
                if (dz == 0 && dx == 0 && dy == 0)
                    continue;

                // Update the counter for the adjacent voxel
                neigh_counts[nz][nx][ny] += val;
            }
        }
    }
}


/**
 * Add a cell to a position on the grid
 *
 * @param x The x coordinate where we want to add the cell
 * @param y The y coordinate where we want to add the cell
 * @param z The z (layer) coordinate where we want to add the cell
 * @param cell The cell that we want to add to the CellList
 * @param type The type of the Cell
 */
void Grid::addCell(int x, int y, int z, Cell *cell, char type) {
    cells[z][x][y].add(cell, type,x, y, z);
    change_neigh_counts(x, y, z, 1);
}

/**
 * Updates nutrient levels at each source's location and occasionally moves the source.
 *
 * For each nutrient source in the grid, this method adds the specified amounts of glucose and oxygen
 * to the corresponding voxel. It also randomly moves the source to a neighboring voxel to simulate daily movement.
 */
void Grid::fill_sources(double glu, double oxy) {
    Source * current = sources->head;
    while (current) { 
        // Add nutrients in the current voxel
        glucose[current->z][current->x][current->y] += glu;
        oxygen[current->z][current->x][current->y] += oxy;
        
        // The source moves on average once per day
        if ((rand() % 24) < 1) {
            int newPos = sourceMove(current->x, current->y, current->z);
            // Decode the new position:
            int newZ = newPos / (xsize * ysize);
            int rem = newPos % (xsize * ysize);
            int newX = rem / ysize;
            int newY = rem % ysize;
            current->z = newZ;
            current->x = newX;
            current->y = newY;
        
        }
        current = current->next;
    }
}

int Grid::sourceMove(int x, int y, int z) {

    // Movement toward the center of the tumor
    if (rand() % 50000 < CancerCell::count) {
        // cout << "center_x = " << center_x << endl;
        // cout << "center_y = " << center_y << endl;
        // cout << "center_z = " << center_z << endl;
        if (x < center_x)
            x++;
        else if (x > center_x)
            x--;
            
        if (y < center_y)
            y++;
        else if (y > center_y)
            y--;
            
        if (z < center_z)
            z++;
        else if (z > center_z)
            z--;
            
        // Encode the new position into a single integer
        // (z * xsize * ysize) + (x * ysize) + y
        return z * xsize * ysize + x * ysize + y;
    } else { 
        // Movement in a random direction
        return rand_adj(x, y, z); 
    }
}

/**
 * Find a random neighbouring voxel in 3D.
 *
 * @param x The x-coordinate of the central voxel.
 * @param y The y-coordinate of the central voxel.
 * @param z The z-coordinate (layer) of the central voxel.
 * @return An integer encoding the coordinates of the chosen neighbouring voxel,
 *         using the formula: index = z * (xsize * ysize) + x * ysize + y.
 */
int Grid::rand_adj(int x, int y, int z) {
    int counter = 0;
    int pos[26]; // In 3D, a voxel has maximum 26 neighbors

    // Loop through all directions along the z, x, and y axes.
    for (int dz = -1; dz <= 1; dz++) {
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                // Escludiamo il voxel centrale (nessun offset)
                if (dz == 0 && dx == 0 && dy == 0)
                    continue;
                    
                // Checks if the voxel (x+dx, y+dy, z+dz) is within bounds and, if so,
                // adds it to the array of candidate positions.
                // NOTE:
                // "pos" and "counter" are local to rand_adj but passed by pointer/reference to adj_helper,
                // so their updates are reflected directly without needing to return them.
                adj_helper(x + dx, y + dy, z + dz, pos, counter);
            }
        }
    }
    
    // If no valid adjacent voxel was found (a rare case, e.g., in a corner in 3D)
    if (counter == 0)
        return -1;
    
    // Select radomly a position
    return pos[rand() % counter];
}

/**
 * Helper for rand_adj 
 *
 * Verifica che le coordinate (x, y, z) siano all'interno dei limiti della griglia.
 * Se lo sono, codifica le coordinate in un unico intero usando la formula:
 * index = z * (xsize * ysize) + x * ysize + y
 * e lo aggiunge all'array dei candidati.
 *
 * @param x The x-coordinate to check.
 * @param y The y-coordinate to check.
 * @param z The z-coordinate to check.
 * @param pos L'array in cui vengono salvate le posizioni valide.
 * @param counter Riferimento al contatore delle posizioni valide trovate.
 */
void Grid::adj_helper(int x, int y, int z, int* pos, int& counter) {
    if (x >= 0 && x < xsize &&
        y >= 0 && y < ysize &&
        z >= 0 && z < zsize) {
        pos[counter++] = z * xsize * ysize + x * ysize + y;
    }
}

/**
 * Compute the average position of cancer cells in the 3D grid.
 */
void Grid::compute_center(){ 
    int count = 0;
    center_x = 0.0;
    center_y = 0.0;
    center_z = 0.0;
    
    // Itera su tutti i voxel: z (layer), x (righe) e y (colonne)
    for (int k = 0; k < zsize; k++){
        for (int i = 0; i < xsize; i++){
            for (int j = 0; j < ysize; j++){
                // count += cells[k][i][j].ccell_count;
                // center_x += cells[k][i][j].ccell_count * i;
                // center_y += cells[k][i][j].ccell_count * j;
                // center_z += cells[k][i][j].ccell_count * k;
                count += 1;
                center_x += 1 * i;
                center_y += 1 * j;
                center_z += 1 * k;
            }
        }
    }
    // Si presuppone che count > 0, altrimenti occorre gestire il caso di divisione per zero.
    center_x /= count;
    center_y /= count;
    center_z /= count;
    // cout << "\nCentro del tumore:" << endl;
    // cout << "center_x = " << center_x << endl;
    // cout << "center_y = " << center_y << endl;
    // cout << "center_z = " << center_z << "\n" <<  endl;

}

double Grid::get_center_x(){
    return center_x;
}

double Grid::get_center_y(){
    return center_y;
}

double Grid::get_center_z(){
    return center_z;
}

/**
 * Go through all cells on the grid and advance them by one hour in their cycle
 *
 */
void Grid::cycle_cells() {
    // Creiamo una lista temporanea per accumulare le nuove cellule
    CellList *toAdd = new CellList();
    
    // Iteriamo su tutti i voxel: k -> layer (z), i -> righe (x), j -> colonne (y)
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                CellNode *current = cells[k][i][j].head;
                while (current) {
                    // Avanziamo il ciclo della cellula corrente
                    // Nota: il parametro della densità è dato dal contatore dei vicini sommato al numero di cellule nel voxel
                    cell_cycle_res result = current->cell->cycle(
                        glucose[k][i][j],
                        oxygen[k][i][j],
                        neigh_counts[k][i][j] + cells[k][i][j].size
                    );
                    
                    // Aggiorniamo il glucosio e l'ossigeno in base al consumo
                    glucose[k][i][j] -= result.glucose;
                    oxygen[k][i][j] -= result.oxygen;
                    
                    // Gestiamo la nascita di nuove cellule in base al valore di result.new_cell
                    if (result.new_cell == 'h') { // Nuova cellula sana
                        int downhill = rand_min(i, j, k, 5);
                        if (downhill >= 0) {
                            // Decodifichiamo l'indice in coordinate (newX, newY, newZ)
                            int newZ = downhill / (xsize * ysize);
                            int rem = downhill % (xsize * ysize);
                            int newX = rem / ysize;
                            int newY = rem % ysize;
                            toAdd->add(new HealthyCell('q'), 'h', newX, newY, newZ);
                        } else {
                            current->cell->sleep();
                        }
                    }
                    
                    if (result.new_cell == 'c') { // Nuova cellula cancerosa
                        int downhill = rand_adj(i, j, k);
                        if (downhill >= 0) {
                            int newZ = downhill / (xsize * ysize);
                            int rem = downhill % (xsize * ysize);
                            int newX = rem / ysize;
                            int newY = rem % ysize;
                            toAdd->add(new CancerCell('1'), 'c', newX, newY, newZ);
                        }
                    }
                    
                    if (result.new_cell == 'o') { // Nuova cellula OAR
                        int downhill = find_missing_oar(i, j, k);
                        if (downhill >= 0) {
                            int newZ = downhill / (xsize * ysize);
                            int rem = downhill % (xsize * ysize);
                            int newX = rem / ysize;
                            int newY = rem % ysize;
                            toAdd->add(new OARCell('1'), 'o', newX, newY, newZ);
                        } else {
                            current->cell->sleep();
                        }
                    }
                    
                    if (result.new_cell == 'w') { // La cellula è morta per carenza di nutrienti
                        wake_surrounding_oar(i, j, k);
                    }
                    
                    current = current->next;
                }
                // Salviamo il numero iniziale di cellule nel voxel per aggiornare i contatori dei vicini
                int init_count = cells[k][i][j].size;
                cells[k][i][j].deleteDeadAndSort();
                change_neigh_counts(i, j, k, cells[k][i][j].size - init_count);
            }
        }
    }
    // Aggiungiamo tutte le nuove cellule accumulate nella lista toAdd alla griglia 3D
    addToGrid(toAdd);
}

/**
 * Add all the cells in newCells to their corresponding voxel's CellList in the grid.
 *
 * @param newCells The CellList of new cells that we want to add to the grid.
 */
void Grid::addToGrid(CellList * newCells) {
    CellNode * current = newCells->head;
    while (current) {
        // Save pointer to the next node before reassigning current
        CellNode * next = current->next;
        // Insert the current node into the correct voxel's CellList using its (x, y, z) coordinates.
        cells[current->z][current->x][current->y].add(current, current->type);
        current = next;
    }
    // Clear the newCells list and free its memory.
    newCells->head = nullptr;
    newCells->tail = nullptr;
    newCells->size = 0;
    delete newCells;
}


/**
 * Find a neighboring voxel with the minimum cell density among the 26 neighbors.
 *
 * @param x The x coordinate of the central voxel.
 * @param y The y coordinate of the central voxel.
 * @param z The z coordinate of the central voxel.
 * @param max The maximum density threshold to consider.
 * @return An encoded integer representing the coordinates of the chosen voxel 
 *         (using the formula: z * (xsize * ysize) + x * ysize + y), or -1 if no suitable voxel is found.
 */
int Grid::rand_min(int x, int y, int z, int max) {
    int counter = 0;
    int curr_min = 100000;
    int pos[26]; // Al massimo 26 vicini in 3D

    // Itera su tutti i voxel adiacenti (dx, dy, dz) escluso il centro
    for (int dz = -1; dz <= 1; dz++) {
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                if (dz == 0 && dx == 0 && dy == 0)
                    continue; // Escludi il voxel centrale
                min_helper(x + dx, y + dy, z + dz, curr_min, pos, counter);
            }
        }
    }

    if (curr_min < max)
        return pos[rand() % counter];
    else
        return -1;
}

/**
 * Helper function for rand_min.
 * Aggiorna l'array dei candidati (pos) con il voxel (x, y, z) se la sua densità è inferiore o uguale a quella minima trovata.
 *
 * @param x The x coordinate of the candidate voxel.
 * @param y The y coordinate of the candidate voxel.
 * @param z The z coordinate of the candidate voxel.
 * @param curr_min Reference to the current minimum cell density found.
 * @param pos Array to store encoded positions of voxels with minimum cell density.
 * @param counter Reference to the count of candidate positions.
 */
void Grid::min_helper(int x, int y, int z, int &curr_min, int *pos, int &counter) {
    // Se il voxel appartiene alla zona OAR, lo saltiamo
    if (oar && x >= oar->x1 && x < oar->x2 &&
              y >= oar->y1 && y < oar->y2 &&
              z >= oar->z1 && z < oar->z2)
        return;

    // Verifica che il voxel sia all'interno della griglia
    if (x >= 0 && x < xsize &&
        y >= 0 && y < ysize &&
        z >= 0 && z < zsize) {
        if (cells[z][x][y].size < curr_min) {
            pos[0] = z * xsize * ysize + x * ysize + y;
            counter = 1;
            curr_min = cells[z][x][y].size;
        } else if (cells[z][x][y].size == curr_min) {
            pos[counter] = z * xsize * ysize + x * ysize + y;
            counter++;
        }
    }
}

/**
 * Find a neighboring voxel within the OAR zone that lacks an OAR cell.
 *
 * @param x The x coordinate of the central voxel.
 * @param y The y coordinate of the central voxel.
 * @param z The z coordinate of the central voxel.
 * @return An encoded integer representing the coordinates of a voxel (using the formula: z * (xsize * ysize) + x * ysize + y)
 *         that is within the OAR zone and has no OAR cell, or -1 if no such voxel is found.
 */
int Grid::find_missing_oar(int x, int y, int z) {
    int counter = 0;
    int curr_min = 100000;
    int pos[26]; // Al massimo 26 vicini

    // Itera su tutti i voxel adiacenti (escluso il centro)
    for (int dz = -1; dz <= 1; dz++) {
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                if (dz == 0 && dx == 0 && dy == 0)
                    continue;
                missing_oar_helper(x + dx, y + dy, z + dz, curr_min, pos, counter);
            }
        }
    }
    
    return (counter > 0) ? pos[rand() % counter] : -1;
}

/**
 * Helper function for find_missing_oar.
 * Aggiorna l'array dei candidati con il voxel (x, y, z) se esso appartiene alla zona OAR, non contiene OARCell,
 * e possiede una densità cellulare minima.
 *
 * @param x The x coordinate of the candidate voxel.
 * @param y The y coordinate of the candidate voxel.
 * @param z The z coordinate of the candidate voxel.
 * @param curr_min Reference to the current minimum cell density found among candidates.
 * @param pos Array to store encoded candidate positions.
 * @param counter Reference to the count of candidate positions.
 */
void Grid::missing_oar_helper(int x, int y, int z, int &curr_min, int *pos, int &counter) {
    // Considera solo i voxel all'interno della zona OAR che non hanno OARCells
    if (oar && x >= oar->x1 && x < oar->x2 &&
              y >= oar->y1 && y < oar->y2 &&
              z >= oar->z1 && z < oar->z2 &&
              cells[z][x][y].oar_count == 0) {
        if (cells[z][x][y].size < curr_min) {
            pos[0] = z * xsize * ysize + x * ysize + y;
            counter = 1;
            curr_min = cells[z][x][y].size;
        } else if (cells[z][x][y].size == curr_min) {
            pos[counter] = z * xsize * ysize + x * ysize + y;
            counter++;
        }
    }
}

/**
 * Wake up (remove from quiescence) all OAR cells in the voxels surrounding the given voxel.
 *
 * @param x The x coordinate of the central voxel.
 * @param y The y coordinate of the central voxel.
 * @param z The z coordinate of the central voxel.
 */
void Grid::wake_surrounding_oar(int x, int y, int z) {
    // Itera su tutti i voxel adiacenti (escluso il centro)
    for (int dz = -1; dz <= 1; dz++) {
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                if (dz == 0 && dx == 0 && dy == 0)
                    continue;
                wake_helper(x + dx, y + dy, z + dz);
            }
        }
    }
}

/**
 * Helper function for wake_surrounding_oar.
 * Sveglia le OARCells presenti nel voxel specificato se questo appartiene alla zona OAR.
 *
 * @param x The x coordinate of the voxel.
 * @param y The y coordinate of the voxel.
 * @param z The z coordinate of the voxel.
 */
void Grid::wake_helper(int x, int y, int z) {
    // Se il voxel è nella zona OAR, sveglia tutte le OARCells presenti
    if (oar && x >= oar->x1 && x < oar->x2 &&
              y >= oar->y1 && y < oar->y2 &&
              z >= oar->z1 && z < oar->z2) {
        cells[z][x][y].wake_oar();
    }
}

/**
 * Helper for diffuse in 3D.
 *
 * Spreads the float amount of each entry in a 3D array (voxel) to its neighboring voxels 
 * with a fraction determined by diff_factor. Each voxel retains (1 - diff_factor) of its
 * original amount and diffuses the remaining diff_factor equally among its up to 26 adjacent neighbors.
 *
 * @param src The 3D array with the initial amounts.
 * @param dest The 3D array where the diffused amounts will be stored.
 * @param xsize The number of rows (x-dimension) in the arrays.
 * @param ysize The number of columns (y-dimension) in the arrays.
 * @param zsize The number of layers (z-dimension) in the arrays.
 * @param diff_factor The fraction of each voxel's value to be diffused to its neighbors.
 */
void diffuse_helper(double ***src, double ***dest, int xsize, int ysize, int zsize, double diff_factor) {
    // Iterate over every voxel in the 3D grid.
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                // Each voxel retains a portion of its original value.
                dest[k][i][j] = (1.0 - diff_factor) * src[k][i][j];
                
                // Diffuse to all 26 neighboring voxels.
                for (int dz = -1; dz <= 1; dz++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        for (int dy = -1; dy <= 1; dy++) {
                            // Skip the central voxel.
                            if (dz == 0 && dx == 0 && dy == 0)
                                continue;
                            
                            int nk = k + dz;
                            int ni = i + dx;
                            int nj = j + dy;
                            
                            // Check that neighbor indices are within bounds.
                            if (nk >= 0 && nk < zsize &&
                                ni >= 0 && ni < xsize &&
                                nj >= 0 && nj < ysize) {
                                // Add the diffused portion from the neighbor.
                                dest[k][i][j] += (diff_factor / 26.0) * src[nk][ni][nj];
                            }
                        }
                    }
                }
            }
        }
    }
}

/**
 * Diffuse glucose and oxygen over the entire 3D grid.
 *
 * This function applies the diffusion process to both the glucose and oxygen arrays
 * across the 3D grid. For each substance, it calls the 3D version of diffuse_helper(),
 * which computes the new diffused values for every voxel based on a given diffusion factor.
 * Once the diffusion is computed, the source array is swapped with the helper array so that
 * the updated (diffused) values become the current state of the grid.
 *
 * @param diff_factor The fraction of each voxel's content that should be diffused to its neighboring voxels.
 */
void Grid::diffuse(double diff_factor) {
    // Diffuse the glucose in the 3D grid.
    diffuse_helper(glucose, glucose_helper, xsize, ysize, zsize, diff_factor);
    double ***temp = glucose;
    glucose = glucose_helper;
    glucose_helper = temp;
    
    // Diffuse the oxygen in the 3D grid.
    diffuse_helper(oxygen, oxygen_helper, xsize, ysize, zsize, diff_factor);
    temp = oxygen;
    oxygen = oxygen_helper;
    oxygen_helper = temp;
}

/**
 * Compute the weighted sum of cell types for the CellList on position x, y, z
 */
int Grid::pixel_density(int x, int y, int z){
    return cells[z][x][y].CellTypeSum();
}

/**
 * Returns the type of the first cell on the given position
 *
 * @return 0 if there are no cells on this position, -1 if there is a cancer cell, 1 for a healthy cell and 2 for an OAR cell
 */
int Grid::pixel_type(int x, int y, int z){
    if (cells[z][x][y].head){
        char t = cells[z][x][y].head -> type;
        if (t == 'c'){
            return -1; 
        } else if (t == 'h'){
            return 1;
        } else {
            return 2;
        }
    } else {
        return 0;
    }
}

/**
 * Return the current glucose array
 */
double *** Grid::currentGlucose(){
    return glucose;
}

/**
 * Return the current oxygen array
 */
double *** Grid::currentOxygen(){
    return oxygen;
}

/**
 * Return the number of helathy cells of a voxel
 */
int Grid::getHealthyCount(int x, int y, int z) {
    // Le cellule sane sono ottenute sottraendo il numero di cellule cancerose (ccell_count)
    // e il numero di cellule OAR (oar_count) al numero totale di cellule (size)
    return cells[z][x][y].size - cells[z][x][y].ccell_count - cells[z][x][y].oar_count;
}

/**
 * Return the number of cancer cells of a voxel
 */
int Grid::getCancerCount(int x, int y, int z) {
    return cells[z][x][y].ccell_count;
}

/**
 * Return the number of oar cells of a voxel
 */
int Grid::getOARCount(int x, int y, int z) {
    return cells[z][x][y].oar_count;
}

/**
 * Calcola la distanza euclidea tra due punti in uno spazio 3D.
 *
 * @param x1, y1, z1 Coordinate del primo punto (tipicamente indici interi della griglia).
 * @param x2, y2, z2 Coordinate del secondo punto (valori in virgola mobile).
 * @return La distanza euclidea tra i due punti.
 */
double distance(int x1, int y1, int z1, double x2, double y2, double z2) {
    // Calcola le differenze lungo ciascun asse
    double dist_x = x1 - x2;
    double dist_y = y1 - y2;
    double dist_z = z1 - z2;
    // Restituisce la radice quadrata della somma dei quadrati delle differenze
    return sqrt(dist_x * dist_x + dist_y * dist_y + dist_z * dist_z);
}
/**
 * Computes the dose depending on the distance to the tumor's center
 *
 * @param rad Radius of the radiation (95 % of the full dose at 1 radius from the center)
 * @param x Distance from the center
 * @return The Euclidean distance between the two points
 */
double conv(double rad, double x){
    double denom = 3.8;//sqrt(2) * 2.7
    return erf((rad - x)/denom) - erf((-rad - x) / denom);
}



double get_multiplicator(double dose, double radius){
    return dose / conv(14, 0);
}

double scale(double radius, double x, double multiplicator){
    return multiplicator * conv(14.0, x * 10.0 / radius);
}

/**
 * Irradia le cellule intorno ad un centro specifico con una dose e un raggio dati. No OAR cells
 *
 * @param dose La dose di radiazione (in grays)
 * @param radius Il raggio della radiazione (95 % della dose completa a 1 raggio dal centro)
 * @param center_x La coordinata x del centro di radiazione
 * @param center_y La coordinata y del centro di radiazione
 * @param center_z La coordinata z del centro di radiazione
 */
void Grid::irradiate(double dose, double radius, double center_x, double center_y, double center_z) {
    // Se la dose è 0, non si applica alcuna irradiazione
    if (dose == 0)
        return;

    // Calcola il moltiplicatore per normalizzare la dose in base al raggio
    double multiplicator = get_multiplicator(dose, radius);
    // Parametri del modello per il calcolo della dose (valori fissi, eventualmente modificabili)
    double oer_m = 3.0;
    double k_m = 3.0;

    // Itera su ogni voxel della griglia 3D: k per la profondità (z), i per le righe (x) e j per le colonne (y)
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                // Calcolo la distanza dal centro
                double dist = distance(i, j, k, center_x, center_y, center_x);
                if (cells[k][i][j].size && dist < 3 * radius){ //If there are cells on the pixel
                    CellNode * current = cells[k][i][j].head;
                    while (current){
                        // Include the effect of hypoxia, Powathil formula
                        double omf = (oxygen[k][i][j] / 100.0 * oer_m + k_m) / (oxygen[k][i][j] / 100.0 + k_m) / oer_m;
                        current -> cell -> radiate(scale(radius, dist, multiplicator) * omf);

                        current = current -> next;
                    }
                    int init_count = cells[k][i][j].size;
                    cells[k][i][j].deleteDeadAndSort();
                    change_neigh_counts(i, j, k, cells[k][i][j].size - init_count);
                }
            }
        }
    }
}

/**
 * Find the cancer cell most distant from the given center, and return its distance from this center
 *
 * @param center_x The x coordinate which we want to compute the radius
 * @param center_y The y coordinate which we want to compute the radius
 * @param center_z The z coordinate which we want to compute the radius
 * @return The distance from the cell furthest away from the center to the center
 */

double Grid::tumor_radius(int center_x, int center_y, int center_z) {
    if (CancerCell::count == 0) {
        return -1.0;
    }
    double dist = -1.0;
    // Itera su ogni voxel della griglia 3D
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                // Se il voxel contiene almeno una cellula e la prima cellula è cancerosa
                if (cells[k][i][j].size > 0 && cells[k][i][j].head->type == 'c') {
                    int dist_x = i - center_x;
                    int dist_y = j - center_y;
                    int dist_z = k - center_z;
                    double d = sqrt(dist_x * dist_x + dist_y * dist_y + dist_z * dist_z);
                    dist = std::max(dist, d);
                }
            }
        }
    }
    // Si vuole il raggio massimo
    if (dist < 3.0)
        dist = 3.0;
    return dist;
}

/**
 * Irradiate the tumor present on the grid with the given dose
 */
void Grid::irradiate(double dose){
    compute_center();
    double radius = tumor_radius(center_x, center_y, center_z);
    irradiate(dose, radius, center_x, center_y, center_z);
}


//Questo processo permette di aggiornare direttamente il campo next dei nodi senza dover tenere esplicitamente un puntatore "precedente" e senza dover scorrere nuovamente la lista. 