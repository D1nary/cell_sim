#include <iostream>
#include <filesystem> // Per la creazione dei path

#include <vector> // Per la gestione dei path
#include <string> // Per la gestione dei path

#include "grid_3d.h" 
#include "controller_3d.h"

#include <algorithm> // Per find()

#include <cstdlib>  // Per rand() e srand()
#include <ctime>    // Per time()

using namespace std;

int main() {

    // Da inserire una funzione (main in questo caso)
    std::srand(static_cast<unsigned int>(std::time(nullptr))); 
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

    int num_hour = 400;

    // Radiation variables
    int week = 2; // Weeks of tratments
    int rad_days = 5; // Number of days in which we send radiation
    int rest_days = 2; // Number of days without radiation
    double dose = 2.0; // Dose per day

    std::filesystem::path current = std::filesystem::current_path();
    std::filesystem::path res_path = current.parent_path() / "cpp" / "results"; // results path
    std::filesystem::path data_path = res_path / "data";// data path
    std::filesystem::path data_path_tab = data_path / "tabs";// data tab
    std::filesystem::path data_path_tab_growth = data_path_tab / "growth";// growth tab
    std::filesystem::path data_path_tab_treat = data_path_tab / "treatments";// treatments tab
    std::filesystem::path data_path_num = data_path / "cell_num";// data cell_num


    std::vector<std::string> paths = {res_path, data_path, data_path_tab, data_path_num,
        data_path_tab_growth, data_path_tab_treat};
    

    Controller * controller = new Controller(xsize, ysize, zsize, sources_num, intervals1);

    // Creazione degli intervalli per il salvataggio dei dati (2D e 3D)
    
    int divisor1 = 4;
    intervals1 = controller -> get_intervals(num_hour, divisor1);

    // Creazione degli intervalli per il salvataggio dei dati (sum)
    int divisor2 = 100;
    intervals2 = controller -> get_intervals(num_hour, divisor2);

    // intervals per il salvataggio dei risultati
    controller->createDirectories(paths);

    // Creazione del vettore di path per i trattamenti
    // std::vector<std::filesystem::path> treatmentPaths;
    // for (int i = 1; i <= week; i++) {
    //     // Ogni path si basa su data_path_tab_treat con l'aggiunta della sottocartella "tr<i>"
    //     std::filesystem::path treatmentPath = data_path_tab_treat / ("tr" + std::to_string(i));
    //     treatmentPaths.push_back(treatmentPath);
    //     std::filesystem::create_directories(treatmentPath);
    // }


    // Creazione file_name per i dati 2D e 3D per growth
    std::vector<std::string> file_name_g;
    for (int i = 0; i <= divisor1; i++) {
        file_name_g.push_back("t" + std::to_string(intervals1[i]) + "_gd.txt");
    }

    // Creazione della griglia con 1, -1 e 0
    noFilledGrid = controller->grid_creation(cradius, hradius);


    // for (int k = 0; k < zsize; k++) {
    //     cout << "Layer " << k << ":\n";
    //     for (int i = 0; i < xsize; i++) {
    //         for (int j = 0; j < ysize; j++) {
    //             cout << noFilledGrid[k][i][j] << " ";
    //         }
    //         cout << endl;
    //     }
    //     cout << endl; // Riga vuota per separare i layer
    // }


    // Controllo i valori di intervals
    // cout << "\n" << endl;
    // for (int i = 0; i <= divisor; i++) {
    //     std::cout << "interval[" << i << "] = " << intervals[i] << std::endl;
    //     cout << file_name[i] << endl;
    // }
    // cout << "\n" << endl;
    // exit(0);

    // Riempimento della griglia creata
    controller -> fill_grid(hcells, ccells, noFilledGrid);

    // --- GROWING ---
    int count = -1;
    for (int i = 0; i <= num_hour; i++){
        // cout << i << ", " << controller -> tick << endl;
        if (std::find(intervals1, intervals1 + (divisor1 + 1), i) != intervals1 + (divisor1 + 1)) {
            count += 1;
            // Nota: ad ogni chiamata di saveDataTab salvo su un file diverso
            // controller -> saveDataTab(data_path_tab_growth, file_name[count]);
            controller -> tempDataTab();

            // Print cell count
            cout << controller -> tick << ", " << HealthyCell::count << ", " 
            << CancerCell::count << ", " << OARCell::count << endl;
        }
        if (std::find(intervals2, intervals2 + (divisor2 + 1), i) != intervals2 + (divisor2 + 1)) {
            // Nota: ad ogni chiamata di tempCellCounts salvo i dati in un array
            controller -> tempCellCounts();
        }
        controller->go();
    }
    controller -> saveDataTab(data_path_tab_growth, file_name_g, intervals1, (divisor1 + 1));
    controller -> saveCellCounts(data_path_num, "cell_counts_gr.txt");

    // --- RADIATON TREATMENT ---

    controller -> tick = 0;

    num_hour =  24 * (rad_days + rest_days) * week;
    // divisor1 = (rad_days + rest_days) * week; // For sum data treatment
    divisor1 = 2;

    // intervals vector creation for tratment files
    intervals1 = controller -> get_intervals(num_hour, divisor1);

    // Creazione file_name per i dati 2D e 3D per theraphy
    std::vector<std::string> file_name_t;
    for (int i = 0; i <= divisor1; i++) {
        file_name_t.push_back("t" + std::to_string(intervals1[i]) + "_gd.txt");
    }
    // for (int i = 0; i <= divisor1; i++){
    //     cout << file_name_t[i]<< endl;
    // }

    controller -> treatment(week, rad_days, rest_days, dose); 
    controller -> saveCellCounts(data_path_num, "cell_counts_tr.txt");
    controller -> saveDataTab(data_path_tab_treat, file_name_t, intervals1, (divisor1+1));

    return 0;
}

