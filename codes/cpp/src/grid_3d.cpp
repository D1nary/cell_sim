#include <algorithm>
#include "grid_3d.h"
#include <assert.h> 
#include <math.h> 
#include <iostream>

#include <cstdlib>  // Per rand() e srand()

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
    
    //Finché current non è nullptr (nullptr = puntatore nullo)
    while (current){ // Delete all the CellNodes and Cells in the CellList

        // Accede ai membri di un oggetto attraverso un puntatore.
        // ptr->member. 
        // Il primo next è il puntatore dichiarato nel distruttore
        // mentre il secondo next è un MEMBRO di CellNode.
        // Il primo next (cioè la variabile puntatore next dichiarata nel distruttore) 
        // conterrà il valore del membro next del nodo corrente (current->next). 
        // Questo valore rappresenta un puntatore al nodo successivo nella lista concatenata.
        next = current -> next;
        
        //La memoria associata al membro cell dell'oggetto CellNode corrente viene liberata.
        delete current -> cell;
        
        //La memoria dell'oggetto CellNode stesso viene deallocata.
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
    /*
    Esempio assertassert(expression);
    expression è una condizione booleana che si presume essere vera.
     
    Se expression è vera, il programma continua normalmente.
    Se expression è falsa, assert termina il programma, 
    stampa un messaggio di errore sullo standard error (stderr) 
    e indica il file e il numero di riga in cui l'asserzione ha fallito.
    */
    assert(newNode);

    if (size == 0){
        head = newNode;
        tail = newNode;
        newNode -> next = nullptr;
    }
    else if (type == 'h' || type == 'o'){ // or
        // Accedo al membro "next" corrispondente all'oggetto a cui
        // punta il puntatore "tail" e gli assegno il valore di "newNode"
        tail -> next = newNode; // Aggiungo il nodo alla fine
        tail = newNode;
        newNode -> next = nullptr;
    } else if(type == 'c'){
        newNode -> next = head;
        head = newNode; // Aggiungo il nodo all'inizio di CellList
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
    CellNode * newNode = new CellNode; // Creo un oggetto di tipo new CellNode
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
 * @param z The y coordinate of the cell on the grid
 */
void CellList::add(Cell *cell, char type, int x, int y, int z) {
    /*
    Qui viene creato un nuovo nodo CellNode e il puntatore
    newNode contiene l'indirizzo della memoria allocata per questo nodo.
    */
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
 * La funzione CellList::deleteDeadAndSort ha lo scopo di: 
 * - Eliminare le cellule morte dalla lista.
 * - Aggiorna la testa (head) e la coda (tail) della lista.
 * - Mantiene i puntatori coerenti per evitare errori di accesso alla memoria.
 */
void CellList::deleteDeadAndSort(){
    bool found_head = false; // Used to ensure that we have a head to the list at the end of traversal
    CellNode * current = head;
    CellNode ** previous_next_pointer; // Puntatore doppio
    /**
     * Il ciclo scansiona ogni nodo (while(current)):
     * 1. Se la cellula è morta, il nodo viene rimosso dalla memoria (if). 
     * 2. Se è la PRIMA cellula viva trovata, aggiorniamo head e tail (else if).
     * 3. Se la cellula è viva e found_head == true (condizione dell'else), significa 
     *    che stiamo processando il resto della lista. tail viene aggiornata per mantenere 
     *    il riferimento all'ultimo nodo vivo. I puntatori vengono agigornati.
     */
    while(current){
        if (!(current -> cell -> alive)){ // Cellulla morta
            delete current->cell;
            if (current -> type == 'o')
                oar_count--;
            if (current -> type == 'c')
                ccell_count--;
            CellNode * toDel = current;
            current = current -> next;
            delete toDel;
            size--;
        } else if (!found_head){ // Verifico che found_head sia falsa 
                                 // cioè ho già trovato il primo nodo "vivo"
                                 // La condizione precedente non viene soddisfatta --> non ci sono cellule vive
            head = current;
            tail = current;
            previous_next_pointer = & (current -> next);// Puntatore di un puntatore
                                                        // & restituisce l'indirizzo di current -> next
            current = current -> next;
            found_head = true;
        }
        else{
            tail = current;
            // Modifico solo l'assegnazione al primo puntatore,
            // cioè quella relativa al nodo.
            *previous_next_pointer = current;
            // Modifico l'assegnazione al puntatore next del nodo current
            // in consideranzione
            previous_next_pointer = & (current -> next);
            current = current -> next;
        }
    }
    /**
     * Se found_head rimane false alla fine dell'iterazione:
     *  - Significa che non è stata trovata nessuna cellula viva nella lista.
     *  - Tutti i nodi sono stati eliminati perché contenevano cellule morte.
     *  - La lista è quindi completamente vuota.
     * 
     * Verifica che la lista sia effettivamente vuota con assert(size == 0);
     * Se size != 0, significa che c'è un bug nella gestione della memoria e il programma 
     * si interrompe con un errore.
     */
    if (!found_head){// The list is now empty after the traversal

        // Controllo se l'espressione size == 0 è vera (true).
        // Altrimenti stampo un messaggio di errore terminando il programma
        assert(size == 0);
        head = nullptr;
        tail = nullptr;
    } else{
        /**
         * Se invece viene trovata almeno una cellula viva s
         * 
         */
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

/**previous_next_pointer
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
 * @param z The z coordinate of the Source on the grid (which layer)
 */
void SourceList::add(int x, int y, int z) {
    /**
     * Alloco dinamicamente un oggetto di tipo Source (new Source) all'heap
     * Questo nuovo oggetto sarà puntato dal puntatore newNode
     */ 

    Source * newNode = new Source; 
    newNode -> x = x;
    newNode -> y = y;
    newNode -> z = z;
    newNode -> next = nullptr;
    if (size == 0){
        head = newNode;
    } else{
        // Siccome tail sarà il penultimo nodo e newNode l'ultimo, è necessario impostare
        // l'elemento next del penultimo nodo come il nuovo ultimo nodo (newNode)
        tail -> next = newNode;   
    }
    tail = newNode;
    size++;
}

/**
 * Constructor of Grid without an OAR zone
 *
 * The grid is the base of the simulation, it is made out of 3 superimposed 2D layers : one contains the CellLists for
 * each pixel, one contains the glucose amount on each pixel and one contains the oxygen amount on each pixel.
 *
 * @param xsize The number of rows of the grid ****MODIFICA****
 * @param ysize The number of columns of the grid
 * @param zsize The number of columns of the grid
 * @param sources_num The number of nutrient sources that should be added to the grid
 * 
 */
Grid::Grid(int xsize, int ysize, int zsize, int sources_num):xsize(xsize), ysize(ysize), zsize(zsize), oar(nullptr){
    // Allocazione dinamica delle matrici 3D con la nuova convenzione [z][x][y]
    cells = new CellList**[zsize];
    glucose = new double**[zsize];
    glucose_helper = new double**[zsize];
    oxygen = new double**[zsize];
    oxygen_helper = new double**[zsize];
    neigh_counts = new int**[zsize];

    for(int k = 0; k < zsize; k++) { // Profondità (z)
        cells[k] = new CellList*[xsize];
        glucose[k] = new double*[xsize];
        glucose_helper[k] = new double*[xsize];
        oxygen[k] = new double*[xsize];
        oxygen_helper[k] = new double*[xsize];
        neigh_counts[k] = new int*[xsize];

        for(int i = 0; i < xsize; i++) { // Righe (x)
            cells[k][i] = new CellList[ysize];
            glucose[k][i] = new double[ysize];
            glucose_helper[k][i] = new double[ysize];
            oxygen[k][i] = new double[ysize];
            oxygen_helper[k][i] = new double[ysize];
            neigh_counts[k][i] = new int[ysize](); // Inizializzazione a 0 grazie a "()"

            // Inizializzazione dei valori di glucosio e ossigeno
            std::fill_n(glucose[k][i], ysize, 100.0); // 1E-6 mg O'Neil
            std::fill_n(oxygen[k][i], ysize, 1000.0); // 1 E-6 ml Jalalimanesh
        }
    }

    // Aggiunta off-set ai bordi della matrce
    for (int k = 0; k < zsize; k++) {         // Scorri i layer (asse z)
        for (int i = 0; i < xsize; i++) {     // Scorri le righe (asse x)
            for (int j = 0; j < ysize; j++) { // Scorri le colonne (asse y)
                // Determino le possibilità in base alla posizione
                int poss_z = (k == 0 || k == zsize - 1) ? 2 : 3;
                int poss_x = (i == 0 || i == xsize - 1) ? 2 : 3;
                int poss_y = (j == 0 || j == ysize - 1) ? 2 : 3;
                
                // Calcolo il prodotto delle possibilità:
                int prod = poss_z * poss_x * poss_y;
                // Calcolo il valore: valore = n_max - vicini = 27 - prod
                int valore = 27 - prod;
                
                // Poiché ogni elemento è inizializzato a 0, possiamo semplicemente assegnare:
                neigh_counts[k][i][j] = valore;
            }
        }
    }


    // Creazione della lista delle sorgenti di nutrienti
    sources = new SourceList();

    for (int i = 0; i < sources_num; i++) {
        sources->add(rand() % xsize, rand() % ysize, rand() % zsize); // Set the sources at random locations on the grid
    }
}
 /**
 * Constructor of Grid with an OAR zone (3D version)
 *
 * The grid is the base of the simulation, now made up of a 3D matrix:
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
 * Destructor of Grid (3D version)
 *
 */
Grid::~Grid() {
    // Deallocazione delle matrici 3D
    for (int k = 0; k < zsize; k++) { // Itera sui layer (z)
        for (int i = 0; i < xsize; i++) { // Itera sulle righe (x)
            // Dealloca gli array di ogni colonna (y)
            delete[] cells[k][i];
            delete[] glucose[k][i];
            delete[] oxygen[k][i];
            delete[] glucose_helper[k][i];
            delete[] oxygen_helper[k][i];
            delete[] neigh_counts[k][i];
        }
        // Dealloca l'array di puntatori relativo alle righe
        delete[] cells[k];
        delete[] glucose[k];
        delete[] oxygen[k];
        delete[] glucose_helper[k];
        delete[] oxygen_helper[k];
        delete[] neigh_counts[k];
    }
    // Dealloca gli array dei layer
    delete[] cells;
    delete[] glucose;
    delete[] oxygen;
    delete[] glucose_helper;
    delete[] oxygen_helper;
    delete[] neigh_counts;

    // Dealloca la lista delle sorgenti di nutrienti
    delete sources;
}

/**
 * Aggiunge "val" al contatore dei vicini del voxel di coordinate (x, y, z)
 * 
 * La funzione aggiorna i contatori dei 26 voxel adiacenti (intorno al voxel centrale)
 *
 * @param x La coordinata x del voxel centrale
 * @param y La coordinata y del voxel centrale
 * @param z La coordinata z del voxel centrale
 * @param val Il valore da sommare (o sottrarre, se negativo) al contatore dei vicini
 */
void Grid::change_neigh_counts(int x, int y, int z, int val) {
    // Ciclo su tutte le possibili variazioni lungo l'asse z (-1, 0, 1)
    for (int dz = -1; dz <= 1; dz++) {
        int nz = z + dz;
        if (nz < 0 || nz >= zsize)
            continue;  // Se siamo fuori dai limiti in z, salta questa iterazione

        // Ciclo sulle variazioni lungo l'asse x (-1, 0, 1)
        for (int dx = -1; dx <= 1; dx++) {
            int nx = x + dx;
            if (nx < 0 || nx >= xsize)
                continue;  // Se siamo fuori dai limiti in x, salta questa iterazione

            // Ciclo sulle variazioni lungo l'asse y (-1, 0, 1)
            for (int dy = -1; dy <= 1; dy++) {
                int ny = y + dy;
                if (ny < 0 || ny >= ysize)
                    continue;  // Se siamo fuori dai limiti in y, salta questa iterazione

                // Escludo il voxel centrale (nessun offset)
                if (dz == 0 && dx == 0 && dy == 0)
                    continue;

                // Aggiorno il contatore per il voxel adiacente
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
    // Perchè change_neigh_counts? Vedi appunti
    change_neigh_counts(x, y, z, 1);
}

void Grid::fill_sources(double glu, double oxy) {
    Source * current = sources->head;
    while (current) { 
        // Aggiunge nutrienti al voxel corrente (3D: [z][x][y])
        glucose[current->z][current->x][current->y] += glu;
        oxygen[current->z][current->x][current->y] += oxy;
        
        // Il source si muove in media una volta al giorno
        if ((rand() % 24) < 1) {
            int newPos = sourceMove(current->x, current->y, current->z);
            // Decodifica la nuova posizione:
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

    // Movimento verso il centro del tumore
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
            
        // Codifica la nuova posizione in un singolo intero:
        // (z * xsize * ysize) + (x * ysize) + y
        return z * xsize * ysize + x * ysize + y;
    } else { 
        // Movimento in una direzione casuale (assicurarsi di avere la versione 3D di rand_adj)
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
    int pos[26]; // In 3D, un voxel ha al massimo 26 vicini (3^3 - 1 = 26).

    // Scorriamo tutte le variazioni lungo gli assi z, x e y.
    for (int dz = -1; dz <= 1; dz++) {
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                // Escludiamo il voxel centrale (nessun offset)
                if (dz == 0 && dx == 0 && dy == 0)
                    continue;
                // Verifica se il voxel (x+dx, y+dy, z+dz) è all'interno dei limiti e, in caso affermativo,
                // lo aggiunge all'array delle posizioni candidate.
                adj_helper(x + dx, y + dy, z + dz, pos, counter);
            }
        }
    }
    
    // Se non è stato trovato alcun voxel adiacente valido (caso raro, ad es. in un angolo in 3D),
    // si può decidere di restituire -1 oppure gestire diversamente il caso.
    if (counter == 0)
        return -1;
    
    // Seleziona casualmente una posizione tra quelle valide
    return pos[rand() % counter];
}

/**
 * Helper for rand_adj in 3D.
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