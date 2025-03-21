// controller_3d.cpp

#include "controller_3d.h"
#include <stdlib.h>
#include <iostream>
#include <cmath>

#include <fstream> //  Gestione dei flussi di input/output su file

#include <vector> // Per la gestione dei path
#include <filesystem> // Per la creazione delle directory

#include <cstdlib>  // Per rand() e srand()

using namespace std;

/**
 * Constructor of a Controller with the Grid already constructed.
 *
 * Simply creates the Controller object with the given grid, without adding any cells.
 *
 * @param grid The provided grid.
 * @param hcells The number of HealthyCells originally intended (currently not used).
 * @param xsize The number of rows of the grid.
 * @param ysize The number of columns of the grid.
 * @param zsize The number of vertical layers of the grid.
 */

 Controller::Controller(int xsize, int ysize, int zsize, int sources_num,int *intervals)
 : xsize(xsize),
   ysize(ysize),
   zsize(zsize),
   sources_num(sources_num),
   tick(0),
   oar(nullptr),
   intervals(intervals)  // Inizializzazione del nuovo membro
{
    // Azzeriamo i contatori delle cellule
    HealthyCell::count = 0;
    CancerCell::count = 0;
    OARCell::count = 0;
    
    std::vector<std::vector<int>> tempCounts;
}


/**
 * Constructor of a Controller with an Organ-at-Risk (OAR) zone in 3D
 *
 * Will first create the grid, then randomly set hcells HealthyCells on the grid 
 * (only outside the OAR zone), and place a CancerCell in the center.
 * The OAR zone is a rectangular prism defined by (x1, x2), (y1, y2) and (z1, z2)
 *
 * @param hcells The number of HealthyCells to set randomly on the grid
 * @param xsize The number of rows of the grid
 * @param ysize The number of columns of the grid
 * @param zsize The number of vertical layers of the grid
 * @param sources_num The number of nutrient sources to put on the grid
 * @param x1, x2 The first and opposite x coordinates of the OAR zone
 * @param y1, y2 The first and opposite y coordinates of the OAR zone
 * @param z1, z2 The first and opposite z coordinates of the OAR zone
 */
Controller::Controller(int hcells, int xsize, int ysize, int zsize, int sources_num,
    int x1, int x2, int y1, int y2, int z1, int z2)
: xsize(xsize), ysize(ysize), zsize(zsize), tick(0), self_grid(true), grid(nullptr), oar(nullptr)
{
// Azzeriamo i contatori delle cellule
HealthyCell::count = 0;
CancerCell::count = 0;
OARCell::count = 0;

// Assicuriamo che le coordinate siano in ordine crescente
if(x1 > x2) { int temp = x1; x1 = x2; x2 = temp; }
if(y1 > y2) { int temp = y1; y1 = y2; y2 = temp; }
if(z1 > z2) { int temp = z1; z1 = z2; z2 = temp; }

// Creazione della zona OAR e assegnazione dei limiti
oar = new OARZone;
oar->x1 = x1;
oar->x2 = x2;
oar->y1 = y1;
oar->y2 = y2;
oar->z1 = z1;
oar->z2 = z2;

    // Creazione della griglia in 3D con la zona OAR
    grid = new Grid(xsize, ysize, zsize, sources_num, oar);

    char stages[5] = {'1', 's', '2', 'm', 'q'};

    // Aggiungiamo le cellule OAR in tutte le posizioni comprese nella zona definita (OAR)
    for (int k = z1; k < z2; k++){
        for (int i = x1; i < x2; i++){
            for (int j = y1; j < y2; j++){
                Cell *new_cell = new OARCell('q');
                grid->addCell(i, j, k, new_cell, 'o');
            }
        }
    }

    // Aggiungiamo hcells HealthyCells in posizioni casuali fuori dalla zona OAR
    for (int i = 0; i < hcells; i++){
        int x = rand() % xsize;
        int y = rand() % ysize;
        int z = rand() % zsize;
        if (!(x >= x1 && x < x2 && y >= y1 && y < y2 && z >= z1 && z < z2)) {
            Cell *new_cell = new HealthyCell(stages[rand() % 5]);
            grid->addCell(x, y, z, new_cell, 'h');
        }
    }

    // Aggiungiamo la cellula cancerosa nel centro della griglia
    grid->addCell(xsize / 2, ysize / 2, zsize / 2, new CancerCell(stages[rand() % 4]), 'c');
}

/**
 * Destructor of the controller
 */
Controller::~Controller() {
    if (self_grid)
        delete grid;
    if(oar)
        delete oar;
}

/**
 * Crea una matrice 3D (int***) in cui ogni voxel viene valorizzato in base alla distanza dal centro della griglia.
 *
 * La griglia è composta da xsize righe, ysize colonne e zsize layer (queste dimensioni sono membri della classe Controller).
 * La funzione calcola il centro della griglia come il punto medio delle dimensioni e per ciascun voxel:
 * - Se il quadrato della distanza dal centro è minore o uguale a (cradius)^2, il voxel viene impostato a -1.
 * - Se il quadrato della distanza è maggiore di (cradius)^2 ma minore o uguale a (hradius)^2, il voxel viene impostato a 1.
 * - In tutti gli altri casi il voxel viene impostato a 0.
 *
 * @param cradius Il raggio interno (in voxel) per cui i voxel vengono marcati con -1.
 * @param hradius Il raggio esterno (in voxel) per cui i voxel con distanza compresa tra cradius e hradius vengono marcati con 1.
 *                Si assume che cradius < hradius.
 * @return Un puntatore alla matrice 3D (int***) allocata dinamicamente contenente i valori -1, 1 o 0.
 */
int*** Controller::grid_creation(double cradius, double hradius) {
    // Allocazione dinamica della griglia 3D
    int ***noFilledGrid = new int**[zsize];
    for (int k = 0; k < zsize; k++) {
        noFilledGrid[k] = new int*[xsize];
        for (int i = 0; i < xsize; i++) {
            noFilledGrid[k][i] = new int[ysize];
        }
    }
    
    // Calcolo del centro della griglia
    int centerX = xsize / 2.0;
    int centerY = ysize / 2.0;
    int centerZ = zsize / 2.0;
    
    // Calcolo della distanza per ogni voxel e assegnazione dei valori
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                double dx = i - centerX;
                double dy = j - centerY;
                double dz = k - centerZ;
                double distance = sqrt(dx * dx + dy * dy + dz * dz);
                
                if (distance <= cradius) {
                    noFilledGrid[k][i][j] = -1;
                } else if (distance <= hradius) {
                    noFilledGrid[k][i][j] = 1;
                } else {
                    noFilledGrid[k][i][j] = 0;
                }
            }
        }
    }
    
    // Stampa di ogni layer della griglia
    // for (int k = 0; k < zsize; k++) {
    //     cout << "Layer " << k << ":\n";
    //     for (int i = 0; i < xsize; i++) {
    //         cout << "[";
    //         for (int j = 0; j < ysize; j++) {
    //             cout << noFilledGrid[k][i][j];
    //             if (j < ysize - 1)
    //                 cout << " ";
    //         }
    //         cout << "]\n";
    //     }
    //     cout << "\n";
    // }
    
    return noFilledGrid;
}



/**
 * Crea e popola un oggetto Grid a partire dalla matrice noFilledGrid.
 *
 * Viene creato un oggetto Grid utilizzando le dimensioni xsize, ysize, zsize e il numero di sorgenti (sources_num)
 * memorizzati nella classe Controller. Per ogni voxel della matrice noFilledGrid:
 * - Se il valore è 1 o -1 vengono aggiunte hcells cellule sane con stato iniziale casuale.
 * - Se il valore è -1 vengono aggiunte anche ccells cellule cancerose con stato iniziale casuale,
 *   in modo che in questi voxel siano presenti sia hcells cellule sane che ccells cellule cancerose.
 *
 * Gli stati iniziali sono scelti casualmente:
 * - Per le HealthyCell vengono scelti tra: '1', 's', '2', 'm', 'q'
 * - Per le CancerCell vengono scelti tra: '1', 's', '2', 'm'
 *
 * @param hcells Numero di cellule sane da aggiungere per ogni voxel in cui noFilledGrid è 1 o -1.
 * @param ccells Numero di cellule cancerose da aggiungere per ogni voxel in cui noFilledGrid è -1.
 * @param noFilledGrid Puntatore alla matrice 3D (int***) contenente i valori -1, 1 e 0.
 * @return Puntatore all'oggetto Grid creato e popolato.
 */
Grid* Controller::fill_grid(int hcells, int ccells, int*** noFilledGrid) {
    // Crea un nuovo oggetto Grid con le dimensioni e il numero di sorgenti definiti nella classe Controller
    grid = new Grid(xsize, ysize, zsize, sources_num);
    
    // Array dei possibili stati iniziali per le cellule sane e cancerose
    char healthy_stages[5] = {'1', 's', '2', 'm', 'q'};
    char cancer_stages[4]  = {'1', 's', '2', 'm'};
    
    // Itera su tutti i voxel della griglia (ordine: [z][x][y])
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                int cellValue = noFilledGrid[k][i][j];
                // Se il voxel ha valore 1 o -1, aggiunge hcells cellule sane con stato casuale
                if (cellValue == 1 || cellValue == -1) {
                    for (int h = 0; h < hcells; h++) {
                        grid->addCell(i, j, k, new HealthyCell(healthy_stages[rand() % 5]), 'h');
                    }
                }
                // Se il voxel ha valore -1, aggiunge anche ccells cellule cancerose con stato casuale
                if (cellValue == -1) {
                    for (int c = 0; c < ccells; c++) {
                        grid->addCell(i, j, k, new CancerCell(cancer_stages[rand() % 4]), 'c');
                    }
                }
            }
        }
    }
    
    // Dealloca la matrice noFilledGrid, dato che non serve più
    deallocateNoFilledGrid(noFilledGrid);
    
    return grid;
}

/**
 * Dealloca la matrice noFilledGrid precedentemente creata.
 *
 * @param grid Puntatore alla matrice noFilledGrid da deallocare.
 */
void Controller::deallocateNoFilledGrid(int*** grid) {
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            delete[] grid[k][i];
        }
        delete[] grid[k];
    }
    delete[] grid;
}


/**
 * Simulate one hour
 *
 * Refill the sources, cycle all the cells, diffuse the nutrients on the grid
 */
void Controller::go() {
    grid -> fill_sources(130, 4500); //O'Neil, Jalalimanesh
    grid -> cycle_cells();
    grid -> diffuse(0.2);
    tick++;
    if(tick % 24 == 0){ // Once a day, recompute the current center of the tumor (used for angiogenesis)
        grid -> compute_center();
    }
}

/**
 * Irradiate the tumor with a certain dose
 *
 * @param dose The dose of radiation in grays
 */
void Controller::irradiate(double dose){
    grid -> irradiate(dose);
}


/**
 * Return a weighted sum of the types of cells at a certain position in the 3D grid.
 *
 * @param x The x coordinate of the voxel.
 * @param y The y coordinate of the voxel.
 * @param z The z coordinate of the voxel.
 * @return The weighted sum of cell types.
 */
int Controller::pixel_density(int x, int y, int z) {
    return grid->pixel_density(x, y, z);
}

/**
 * Return the type of the first cell at a given position in the 3D grid.
 *
 * @param x The x coordinate of the voxel.
 * @param y The y coordinate of the voxel.
 * @param z The z coordinate of the voxel.
 * @return An integer representing the type.
 */
int Controller::pixel_type(int x, int y, int z) {
    return grid->pixel_type(x, y, z);
}

/**
 * Return the current glucose 3D array.
 *
 * @return A triple pointer representing the current glucose levels.
 */
double *** Controller::currentGlucose() {
    return grid->currentGlucose();
}

/**
 * Return the current oxygen 3D array.
 *
 * @return A triple pointer representing the current oxygen levels.
 */
double *** Controller::currentOxygen() {
    return grid->currentOxygen();
}


double Controller::get_center_x(){
    return grid -> get_center_x();
}

double Controller::get_center_y(){
    return grid -> get_center_y();
}

double Controller::get_center_z(){
    return grid -> get_center_z();
}


int* Controller::get_intervals(int num_hour, int divisor) {
    int* intervals = new int[divisor + 1];
    for (int i = 0; i <= divisor; i++) {
        intervals[i] = (i * num_hour) / divisor;
    }
    return intervals;
}

/**
 * Salva le matrici grid, glucose ed oxigen in un file di testo
 *
 * @param filename Path per il salvataggio dei dati
 * @param path
 */

 void Controller::saveDataTab(const std::string &path, const std::string &filename) {
    // Verifica che il path termini con '/' o '\' e, in caso contrario, aggiunge uno slash.
    string dir = path;
    if (!dir.empty() && dir.back() != '/' && dir.back() != '\\') {
        dir += "/";
    }
    // Costruisce il percorso completo unendo il path e il filename.
    string filePath = dir + filename;
    
    //Apro un oggetto ofstream (output file stream)
    ofstream out(filePath);
    
    // Se il file non viene aperto correttamente, viene stampato un messaggio di errore 
    if (!out.is_open()) {
        cerr << "Errore nell'apertura del file " << filePath << " per la scrittura." << endl;
        return;
    }

    // Scrive la riga di commento con i nomi delle colonne
    out << "# x y z nCells HealthyCells CancerCells OarCells glucose oxygen voxel_type" << endl;

    // Recupera i puntatori alle matrici di glucosio e ossigeno
    double ***glu = grid->currentGlucose();
    double ***oxy = grid->currentOxygen();

    // Itera su tutti i voxel della griglia
    for (int z = 0; z < zsize; ++z) {
        for (int x = 0; x < xsize; ++x) {
            for (int y = 0; y < ysize; ++y) {
                // Calcolo numero di cellule presenti in quel voxel
                int cellsCount = grid->pixel_density(x, y, z);
                
                out << x << " " << y << " " << z << " " 
                    << cellsCount << " " 
                    << grid->getHealthyCount(x, y, z)<< " "
                    << grid->getCancerCount(x, y, z)<< " "
                    << grid->getOARCount(x, y, z)<< " "
                    << glu[z][x][y] << " " 
                    << oxy[z][x][y] << " "
                    << grid->pixel_type(x, y, z) << "\n";

            }
        }
    }

    out.close();
    cout << "Dati salvati correttamente in " << filePath << endl;
}

void Controller::saveCellCounts(const std::string &path, const std::string &filename) {
    // Verifica che il path termini con '/' o '\' e, in caso contrario, aggiunge uno slash.
    std::string dir = path;
    if (!dir.empty() && dir.back() != '/' && dir.back() != '\\') {
        dir += "/";
    }
    // Costruisce il percorso completo unendo il path e il filename.
    std::string filePath = dir + filename;

    // Apro il file (ad ogni nuovo salvataggio, il contenuto viene sovrascritto al precedente)
    std::ofstream out(filePath);
    if (!out.is_open()) {
        std::cerr << "Errore nell'apertura del file " << filePath << " per la scrittura." << std::endl;
        return;
    }

    // Creazione dell'header
    out << "# Tick HealthyCells CancerCells OARCells\n";

    // Itera su ogni riga della matrice tempCounts e la scrive nel file
    for (const auto &row : tempCounts) {
        // row[0] contiene già il tick
        out << row[0] << " " 
            << row[1] << " " 
            << row[2] << " " 
            << row[3] << "\n";
    }

    out.close();
    std::cout << "Cell counts saved successfully in file " << filePath << std::endl;
}


void Controller::createDirectories(const std::vector<std::string>& paths) {
    for (const auto& path : paths) {
        try {
            // Crea la directory e tutte le directory intermedie se non esistono
            if (std::filesystem::create_directories(path)) {
                std::cout << "Directory creata: " << path << "\n";
            } else {
                std::cout << "La directory esiste già o non può essere creata: " << path << "\n";
            }
        } catch (const std::filesystem::filesystem_error& ex) {
            std::cerr << "Errore nella creazione della directory " << path << ": " << ex.what() << "\n";
        }
    }
}


void Controller::tempCellCounts(int divisor) {

    std::vector<int> row = { tick, HealthyCell::count, CancerCell::count, OARCell::count };
    // Aggiunge la nuova riga alla matrice
    tempCounts.push_back(row);
}