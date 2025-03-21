#include <iostream>
#include <filesystem> // Per la creazione dei path

#include <vector> // Per la gestione dei path
#include <string> // Per la gestione dei path

#include "grid_3d.h" 
#include "controller_3d.h"

#include <algorithm> // Per verificare se elemento all'interno di un vettore

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
    int num_hour = 400;
    int divisor = 100;
    int* intervals;
    int*** noFilledGrid;

    std::filesystem::path current = std::filesystem::current_path();
    std::filesystem::path res_path = current.parent_path() / "cpp" / "results"; // results path
    std::filesystem::path data_path = res_path / "data";// data path
    std::filesystem::path data_path_tab = data_path / "tabs";// data tab
    std::filesystem::path data_path_num = data_path / "cell_num";// data cell_num
    std::filesystem::path graph_path = res_path / "graphs"; // grap path
    std::filesystem::path graph_path_3d = graph_path / "3d"; // grap path 3d
    std::filesystem::path graph_path_2d = graph_path / "2d"; // grap path 2d

    std::vector<std::string> paths = {res_path, data_path, data_path_tab, data_path_num, 
                                        graph_path, graph_path_2d, graph_path_3d};
    

    Controller * controller = new Controller(xsize, ysize, zsize, sources_num, intervals);

    // Creazione degli intervalli per il salvataggio dei dati
    intervals = controller -> get_intervals(num_hour, divisor);

    // intervals per il salvataggio dei risultati
    controller->createDirectories(paths);

    // Creazione file_name
    std::vector<std::string> file_name;
    for (int i = 0; i <= divisor; i++) {
        file_name.push_back("t" + std::to_string(intervals[i]) + "_gd.txt");
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

    // Riempimento della griglia creata
    controller -> fill_grid(hcells, ccells, noFilledGrid);

    // Controllo i valori di intervals
    // cout << "\n" << endl;
    // for (int i = 0; i <= divisor; i++) {
    //     std::cout << "interval[" << i << "] = " << intervals[i] << std::endl;
    //     cout << file_name[i] << endl;
    // }
    // cout << "\n" << endl;

    
    int count = -1;
    for (int i = 0; i <= num_hour; i++){
        // cout << i << ", " << controller -> tick << endl;
        if (std::find(intervals, intervals + (divisor + 1), i) != intervals + (divisor + 1)) {
            count += 1;
            // Nota: ad ogni chiamata di saveDataTab salvo su un file diverso
            controller -> saveDataTab(data_path_tab, file_name[count]);
            // Nota: ad ogni chiamata di tempCellCounts salvo i dati in un array
            controller -> tempCellCounts(divisor);

            cout << controller -> tick << ", " << HealthyCell::count << ", " 
            << CancerCell::count << ", " << OARCell::count << endl;
        }
        controller->go();
    }
    controller -> saveCellCounts(data_path_num, "cell_counts.txt");

    return 0;
}