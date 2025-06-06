#include <iostream>
#include <filesystem> // For path creation

#include <vector> // For path management
#include <string> // For path management

#include <algorithm> // For find()

#include <cstdlib>  // For rand() and srand()
#include <ctime>    // For time()

#include "grid_3d.h" 
#include "controller_3d.h"

using namespace std;

int main() {

    // Generate seed
    std::srand(static_cast<unsigned int>(std::time(nullptr)));

    // Grid variables
    int xsize = 21;
    int ysize = 21;
    int zsize = 21;
    double cradius =2.0;
    double hradius = 4.0;
    int hcells = 1;
    int ccells = 1;
    int sources_num = 20;
    int* intervals1; // For: 2D/3D Data growth, 2D/3D Data treatment  
    int* intervals2; // For sum data growth, sum data treatment
    int*** noFilledGrid;

    // Radiation variables
    int week = 2; // Weeks of tratments
    int rad_days = 5; // Number of days in which we send radiation
    int rest_days = 2; // Number of days without radiation
    double dose = 2.0; // Dose per day

    // Hours for tumor growth
    int num_hour = 150;

    // Create directories paths
    std::filesystem::path current = std::filesystem::current_path();
    std::filesystem::path res_path = current.parent_path() / "results"; // results path
    std::filesystem::path data_path = res_path / "data";// data path
    std::filesystem::path data_path_tab = data_path / "tabs";// data tab
    std::filesystem::path data_path_tab_growth = data_path_tab / "growth";// growth tab
    std::filesystem::path data_path_tab_treat = data_path_tab / "treatments";// treatments tab
    std::filesystem::path data_path_num = data_path / "cell_num";// data cell_num

    // Create a paths array
    std::vector<std::string> paths = {res_path, data_path, data_path_tab, data_path_num,
        data_path_tab_growth, data_path_tab_treat};
    
    // Initialize the controller (and the grid)
    Controller * controller = new Controller(xsize, ysize, zsize, sources_num, intervals1);

    // Create intervals for voxels data saving (2D and 3D)
    int divisor1 = 4;
    intervals1 = controller -> get_intervals(num_hour, divisor1);

    // Create intervals for cell counters data saving
    int divisor2 = 100;
    intervals2 = controller -> get_intervals(num_hour, divisor2);

    // Create directories
    controller->createDirectories(paths);


    // Create file names for tumor growth
    std::vector<std::string> file_name_g;
    for (int i = 0; i <= divisor1; i++) {
        file_name_g.push_back("t" + std::to_string(intervals1[i]) + "_gd.txt");
    }

    /// Create grid with 1, 0, -1
    noFilledGrid = controller->grid_creation(cradius, hradius);

    // Fill the Grid object with helthy and cancer cells
    controller -> fill_grid(hcells, ccells, noFilledGrid);


    // --- GROWING ---
    cout << "\n" << "TUMOR GROWTH" << endl;
    int count = -1;
    // Loop through each hour in the growth simulation
    for (int i = 0; i <= num_hour; i++){
        
        // Check if the current hour matches a growth data saving interval
        if (std::find(intervals1, intervals1 + (divisor1 + 1), i) != intervals1 + (divisor1 + 1)) {
            count += 1;

            // Save voxel data
            controller -> tempDataTab();

            // Print cell counters
            cout << "tick: " << controller -> tick << "\n"
            << "Healthy cells: " << HealthyCell::count << "\n" 
            << "Cancer cells: " << CancerCell::count << endl;
        }
        // Check if the current hour matches a cell count saving interval
        if (std::find(intervals2, intervals2 + (divisor2 + 1), i) != intervals2 + (divisor2 + 1)) {

            // Save countrer data in a matrix
            controller -> tempCellCounts();
        }
        // Advance the grid cells by one hour
        controller->go();
    }

    // Save growth data in files
    controller -> saveDataTab(data_path_tab_growth, file_name_g, intervals1, (divisor1 + 1));
    controller -> saveCellCounts(data_path_num, "cell_counts_gr.txt");


    // --- RADIATON TREATMENT ---

    cout << "\n" << "BEGIN RADIATON TREATMENT" << endl;

    num_hour =  24 * (rad_days + rest_days) * week;
    // divisor1 = (rad_days + rest_days) * week; // For sum data treatment
    divisor1 = 2;

    // intervals vector creation for tratment files
    intervals1 = controller -> get_intervals(num_hour, divisor1);

    // File name (file_name) creation for 2D and 3D therapy data
    std::vector<std::string> file_name_t;

    for (int i = 0; i <= divisor1; i++) {
        file_name_t.push_back("t" + std::to_string(intervals1[i]) + "_gd.txt");
    }


    // Reset tick counter
    controller -> tick = 0;

    // Perform the tratment to the grid
    controller -> treatment(week, rad_days, rest_days, dose); 
    
    //Save treatment data in files
    controller -> saveCellCounts(data_path_num, "cell_counts_tr.txt");
    controller -> saveDataTab(data_path_tab_treat, file_name_t, intervals1, (divisor1+1));

    return 0;
}
