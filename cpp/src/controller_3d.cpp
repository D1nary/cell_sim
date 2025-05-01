// controller_3d.cpp

#include "controller_3d.h"
#include <stdlib.h>
#include <iostream>
#include <cmath>

#include <fstream> // Handling file input/output streams

#include <vector> // For path handling  
#include <filesystem> // For directory creation

#include <cstdlib>  // For rand() and srand()  

#include <algorithm> // For find()  

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

 Controller::Controller(int xsize, int ysize, int zsize, int sources_num, 
    double cradius, double hradius, int hcells, int ccells)
 : xsize(xsize),
   ysize(ysize),
   zsize(zsize),
   sources_num(sources_num),
   tick(0),
   oar(nullptr)
{
    int*** noFilledGrid;
    // Reset the cell counters
    HealthyCell::count = 0;
    CancerCell::count = 0;
    OARCell::count = 0;
    
    vector<vector<int>> tempCounts;

    // Create grid with 1, 0, -1
    noFilledGrid = grid_creation(cradius, hradius);

    // Fill the Grid object with helthy and cancer cells
    fill_grid(hcells, ccells, noFilledGrid);

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
// Reset cell counters
HealthyCell::count = 0;
CancerCell::count = 0;
OARCell::count = 0;

// Ensure that the coordinates are in ascending order  
if(x1 > x2) { int temp = x1; x1 = x2; x2 = temp; }
if(y1 > y2) { int temp = y1; y1 = y2; y2 = temp; }
if(z1 > z2) { int temp = z1; z1 = z2; z2 = temp; }

// Create the OAR zone and assign its boundaries  
oar = new OARZone;
oar->x1 = x1;
oar->x2 = x2;
oar->y1 = y1;
oar->y2 = y2;
oar->z1 = z1;
oar->z2 = z2;

    // Create the 3D grid with the OAR zone  
    grid = new Grid(xsize, ysize, zsize, sources_num, oar);

    char stages[5] = {'1', 's', '2', 'm', 'q'};

    // Add OAR cells to all positions within the defined OAR zone  
    for (int k = z1; k < z2; k++){
        for (int i = x1; i < x2; i++){
            for (int j = y1; j < y2; j++){
                Cell *new_cell = new OARCell('q');
                grid->addCell(i, j, k, new_cell, 'o');
            }
        }
    }

    // Add hcells (HealthyCells) in random positions outside the OAR zone  
    for (int i = 0; i < hcells; i++){
        int x = rand() % xsize;
        int y = rand() % ysize;
        int z = rand() % zsize;
        if (!(x >= x1 && x < x2 && y >= y1 && y < y2 && z >= z1 && z < z2)) {
            Cell *new_cell = new HealthyCell(stages[rand() % 5]);
            grid->addCell(x, y, z, new_cell, 'h');
        }
    }

    // Add the cancerous cell at the center of the grid  
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
 * Creates a 3D matrix (int***) where each voxel is assigned a value based on its distance from the center of the grid.
 *
 * The grid consists of xsize rows, ysize columns, and zsize layers (these dimensions are members of the Controller class).
 * The function calculates the center of the grid as the midpoint of the dimensions, and for each voxel:
 * - If the squared distance from the center is less than or equal to (cradius)^2, the voxel is set to -1.
 * - If the squared distance is greater than (cradius)^2 but less than or equal to (hradius)^2, the voxel is set to 1.
 * - In all other cases, the voxel is set to 0.
 *
 * @param cradius The inner radius (in voxels) for which voxels are marked with -1.
 * @param hradius The outer radius (in voxels) for which voxels with distance between cradius and hradius are marked with 1.
 *                It is assumed that cradius < hradius.
 * @return A pointer to the dynamically allocated 3D matrix (int***) containing the values -1, 1, or 0.
 */
int*** Controller::grid_creation(double cradius, double hradius) {
    // Dynamic allocation of the 3D grid  
    int ***noFilledGrid = new int**[zsize];
    for (int k = 0; k < zsize; k++) {
        noFilledGrid[k] = new int*[xsize];
        for (int i = 0; i < xsize; i++) {
            noFilledGrid[k][i] = new int[ysize];
        }
    }
    
    // Calculation of the center of the grid  
    int centerX = xsize / 2.0;
    int centerY = ysize / 2.0;
    int centerZ = zsize / 2.0;
    
    // Distance calculation for each voxel and value assignment  
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
    // Printing each layer of the grid  
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
 * Creates and populates a Grid object based on the noFilledGrid matrix.
 *
 * A Grid object is created using the dimensions xsize, ysize, zsize, and the number of sources (sources_num)
 * stored in the Controller class. For each voxel in the noFilledGrid matrix:
 * - If the value is 1 or -1, hcells healthy cells with a random initial state are added.
 * - If the value is -1, ccells cancerous cells with a random initial state are also added,
 *   so that these voxels contain both hcells healthy cells and ccells cancerous cells.
 *
 * Initial states are chosen randomly:
 * - For HealthyCell: one of '1', 's', '2', 'm', 'q'
 * - For CancerCell: one of '1', 's', '2', 'm'
 *
 * @param hcells Number of healthy cells to add for each voxel where noFilledGrid is 1 or -1.
 * @param ccells Number of cancerous cells to add for each voxel where noFilledGrid is -1.
 * @param noFilledGrid Pointer to the 3D matrix (int***) containing values -1, 1, and 0.
 * @return Pointer to the created and populated Grid object.
 */
Grid* Controller::fill_grid(int hcells, int ccells, int*** noFilledGrid) {
    // Create a new Grid object with dimensions and number of sources defined in the Controller class  
    grid = new Grid(xsize, ysize, zsize, sources_num);
    
    // Arrays of possible initial states for healthy and cancerous cells  
    char healthy_stages[5] = {'1', 's', '2', 'm', 'q'};
    char cancer_stages[4]  = {'1', 's', '2', 'm'};
    
    // Iterate over all voxels in the grid (order: [z][x][y])  
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                int cellValue = noFilledGrid[k][i][j];
                // If the voxel has value 1 or -1, add hcells healthy cells with a random state  
                if (cellValue == 1 || cellValue == -1) {
                    for (int h = 0; h < hcells; h++) {
                        grid->addCell(i, j, k, new HealthyCell(healthy_stages[rand() % 5]), 'h');
                    }
                }
                // If the voxel has value -1, also add ccells cancerous cells with a random state  
                if (cellValue == -1) {
                    for (int c = 0; c < ccells; c++) {
                        grid->addCell(i, j, k, new CancerCell(cancer_stages[rand() % 4]), 'c');
                    }
                }
            }
        }
    }
    
    // Deallocate the noFilledGrid matrix, since it is no longer needed  
    deallocateNoFilledGrid(noFilledGrid);
    
    return grid;
}

/**
 * Deallocates the previously created noFilledGrid matrix.
 *
 * @param grid Pointer to the noFilledGrid matrix to be deallocated.
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

/**
 * Calculate an array that contains the tick points at which we intend to save the data.
 * @return An array with the ticks
 */
// int* Controller::get_intervals(int num_hour, int divisor) {
//     int* intervals = new int[divisor + 1];
//     for (int i = 0; i <= divisor; i++) {
//         intervals[i] = (i * num_hour) / divisor;
//     }
//     return intervals;
// }

/**
 * Calculate an array that contains the tick points at which we intend to save the data.
 * @return std::vector<int> of lenght (divisor+1) with the ticks
 */
std::vector<int> Controller::get_intervals(int num_hour, int divisor) {
    std::vector<int> intervals(divisor + 1);
    for (int i = 0; i <= divisor; ++i) {
        intervals[i] = (i * num_hour) / divisor;
    }
    return intervals;
}

/**
 * Save voxels data
 * 
 * Save in a matrix, for each voxel of the grid, the following data: tick, x, y, z,
 * total cell number, healthy cell number, cancer cell number, oar cell number,
 * glucose level, oxygen level, voxel type.
 * 
 * The matrix will be saved to a text file.
 */

void Controller::tempDataTab() {
    // Get the pointers to the glucose and oxygen matrices from the grid  
    double*** glu = grid->currentGlucose();
    double*** oxy = grid->currentOxygen();

    // Iterate over all voxels in the grid  
    for (int z = 0; z < zsize; ++z) {
        for (int x = 0; x < xsize; ++x) {
            for (int y = 0; y < ysize; ++y) {

                double health = grid->getHealthyCount(x, y, z);
                double cancer = grid->getCancerCount(x, y, z);
                double  oar = grid->getOARCount(x, y, z);
                double total = health + cancer + oar;

                std::vector<double> row;
                
                row.push_back(static_cast<double>(tick)); // Current tick  
                row.push_back(static_cast<double>(x)); // x coordinate  
                row.push_back(static_cast<double>(y)); // y coordinate
                row.push_back(static_cast<double>(z));  // z coordinate  
                row.push_back(static_cast<double>(total)); // total number of cells  
                row.push_back(static_cast<double>(health)); // number of healthy cells  
                row.push_back(static_cast<double>(cancer));  // number of cancerer cells  
                row.push_back(static_cast<double>(oar)); // number of OAR cells  
                row.push_back(glu[z][x][y]); // glucose level  
                row.push_back(oxy[z][x][y]); // oxygen level  
                row.push_back(static_cast<double>(grid->pixel_type(x, y, z))); // voxel type  

                // Add the row to the temporary matrix  
                tempDataTabMatrix.push_back(row);
            }
        }
    }
}

/**
 * Reset the temporary matrix
 */
void Controller::clear_tempDataTab() {
    tempDataTabMatrix.clear();
}


/**
 * Save the temporary matrix in a text file.
 * @param path Reference to a constant std::string indicating the directory path.
 * @param filenames Reference to a constant vector of strings containing the filenames.
 * @param intervals Pointer to an array of integers representing intervals.
 * @param intervalsSize Integer indicating the number of intervals.
 */
void Controller::saveDataTab(const std::string &path, const std::vector<std::string>& filenames, 
    const std::vector<int>& intervals, int intervalsSize) {
    // Check that the number of filenames matches the number of values in intervals  
    if (filenames.size() != static_cast<size_t>(intervalsSize)) {
        std::cerr << "The number of filenames does not match the number of values in intervals" << std::endl;
        return;
    }
    
    // For each value in intervals, create a separate file  
    for (int i = 0; i < intervalsSize; ++i) {
        int interval_val = intervals[i];
        std::string currentFilename = filenames[i];
        
        // Construct the full path, ensuring that 'path' ends with a slash  
        std::string dir = path;
        if (!dir.empty() && dir.back() != '/' && dir.back() != '\\') {
            dir += "/";
        }
        std::string filePath = dir + currentFilename;
        
        // Open the output file  
        std::ofstream out(filePath);
        if (!out.is_open()) {
            std::cerr << "Error opening the file " << filePath << " for writing." << std::endl;
            continue;
        }
        
        // Write the header with the column names  
        out << "#Tick x y z nCells HealthyCells CancerCells OarCells glucose oxygen voxel_type" << std::endl;
        
        // Iterate over all rows in the temporary matrix and select those whose 
        // first element (tick) equals interval_val  
        for (const auto &row : tempDataTabMatrix) {
            if (!row.empty() && static_cast<int>(row[0]) == interval_val) {
                // Write each value in the row separated by a space  
                for (size_t j = 0; j < row.size(); ++j) {
                    out << row[j];
                    if (j < row.size() - 1)
                        out << " ";
                }
                out << "\n";
            }
        }
        
        out.close();
        std::cout << "Data successfully saved in " << filePath << std::endl;
    }
}

/**
 * Save cell counter data
 * 
 * Save the following data in a matrix: tick, number of healthy cells,
 * number of cancerous cells, number of OAR cells
 */
void Controller::tempCellCounts() {

    std::vector<int> row = { tick, HealthyCell::count, CancerCell::count, OARCell::count };
    // Adds the new row to the matrix
    tempCounts.push_back(row);
}

/**
 * Clear tempCounts matrix 
 */
void Controller::clear_tempCellCounts() {
    tempCounts.clear();
}

/**
 * Save the cell counts into a text file.
 * 
 * @param path Reference to a constant std::string indicating the directory path.
 * @param filename Reference to a constant std::string indicating the name of the output file.
 */
void Controller::saveCellCounts(const std::string &path, const std::string &filename) {
    // Check that the path ends with '/' or '\' and, if not, append a slash.
    std::string dir = path;
    if (!dir.empty() && dir.back() != '/' && dir.back() != '\\') {
        dir += "/";
    }
    // Construct the full path by joining the path and the filename
    std::string filePath = dir + filename;

    // Open the file
    std::ofstream out(filePath);
    if (!out.is_open()) {
        std::cerr << "Errore nell'apertura del file " << filePath << " per la scrittura." << std::endl;
        return;
    }

    // Create the header
    out << "#Tick HealthyCells CancerCells OARCells\n";

    // Iterate over each row in the tempCounts matrix and write it to the file
    for (const auto &row : tempCounts) {
        out << row[0] << " " 
            << row[1] << " " 
            << row[2] << " " 
            << row[3] << "\n";
    }

    // Close file
    out.close();
    std::cout << "Cell counts saved successfully in file " << filePath << std::endl;
}


/**
 * Create directory for saving data
 */
void Controller::createDirectories(const std::vector<std::string>& paths) {
    for (const auto& path : paths) {
        try {
            // Crea la directory
            if (std::filesystem::create_directories(path)) {
                std::cout << "Directory created:  " << path << "\n";
            } else {
                std::cout << "The directory already exists or cannot be created:  " << path << "\n";
            }
        } catch (const std::filesystem::filesystem_error& ex) {
            std::cerr << "Error creating the directory" << path << ": " << ex.what() << "\n";
        }
    }
}


/**
 * Tumor therapy treatment control.
 * 
 * @param week Number of treatment weeks
 * @param rad_days Number of days the tumor is irradiated
 * @param rest_days Number of days without irradiation
 * @param dose Daily radiation dose
 */

void Controller::test_treatment(int week, int rad_days, int rest_days, double dose){

    // Clear any previous data
    clear_tempCellCounts();
    clear_tempDataTab();

    // Save data before theraphy
    tempCellCounts();
    tempDataTab();

    for (int w = 0; w < week; w++){
        tempDataTab();
        for (int rd = 0; rd < rad_days; rd++){

            // Irradiate
            irradiate(dose);
            
            // Simulate 1 day (24 hours) 
            for (int h = 0; h < 24; h++){
                go();
            }
            tempCellCounts(); // Save cell counter data every 24h
        }
        for (int rest = 0; rest < rest_days; rest++){
            // Simulate 1 day (24 hours) 
            for (int h = 0; h < 24; h++){
                go();
            }
            tempCellCounts(); // Save cell counter data every 24h
        }
        tempDataTab(); // Save voxel data every theraphy week
    }
}

/**
 * Check the intervals array
 * 
 * @param divisor Divisor of the total number of hours. intervals size will be divisor + 1
 * @param intervals Pointer to the intervals array
 */
void Controller::printIntervals(int divisor, int* intervals){
    cout << "\n" << endl;
    for (int i = 0; i <= divisor; i++) {
        std::cout << "interval[" << i << "] = " << intervals[i] << std::endl;
    }
    cout << "\n" << endl;
}

/**
 * Get the number of healthy and cancer cells in the simulazio
 * @return Array composed of HealthyCell::count and CancerCell::count
 */
std::vector<int> Controller::get_cell_counts() const {
    return {
        HealthyCell::count,   // primo elemento
        CancerCell::count     // secondo elemento
    };
}