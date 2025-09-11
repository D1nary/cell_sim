#ifndef RADIO_RL_CONTROLLER_H
#define RADIO_RL_CONTROLLER_H

#include "CellLib/grid.h"
#include "cell.h"

#include <vector> // Per la gestione dei path
#include <string>  // Necessario per std::string


class Controller {
public:

    Controller(int xsize, int ysize, int zsize, int sources_num,
        double cradius, double hradius, int hcells, int ccells);
    ~Controller();

    int*** grid_creation(double hradius, double cradius);
    Grid* fill_grid(int hcells, int ccells, int*** noFilledGrid);
    void deallocateNoFilledGrid(int*** grid);

    void irradiate(double dose);
    // void irradiate_center(double dose);
    // void irradiate(double dose, double radius);
    // void irradiate_center(double dose, double radius);
    void go();
    int pixel_density(int x, int y, int z);
    int pixel_type(int x, int y, int z);
    double *** currentGlucose();
    double *** currentOxygen();
    // double tumor_radius();
    int xsize, ysize, zsize;
    int sources_num;
    int tick;
    double get_center_x();
    double get_center_y();
    double get_center_z();
    std::vector<int> get_intervals(int num_hour, int divisor);

    void saveDataTab(const std::string &path, const std::vector<std::string>& filenames, 
        const std::vector<int>& intervals, int intervalsSize);
    void saveCellCounts(const std::string &path, const std::string &filename);
    void createDirectories(const std::vector<std::string>& paths);
    void tempCellCounts();
    void clear_tempCellCounts();
    void tempDataTab();
    void clear_tempDataTab();
    void printIntervals(int divisor, int* intervals);

    void test_treatment(int week, int rad_days, int rest_days, double dose);
    std::vector<int> get_cell_counts() const;


private:
    bool self_grid;
    Grid * grid;
    OARZone * oar;
    int* intervals_sum;
    std::vector<std::vector<int>> tempCounts;
    std::vector<std::vector<double>> tempDataTabMatrix;

    int num_hour;
    std::vector<int> intervals;
};


#endif //RADIO_RL_CONTROLLER_H