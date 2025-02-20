#ifndef RADIO_RL_GRID_H
#define RADIO_RL_GRID_H

#include "cell.h"

struct CellNode
{
    int x, y, z;
    Cell * cell;
    CellNode *next;
    char type;
};

struct OARZone{
    int x1, x2, x3, y1, y2, y3;
};

class CellList
{
public:
    CellNode *head, *tail; // Puntatori a oggetti di tipo CellNode
    int size;
    int oar_count;
    int ccell_count;
    CellList();
    ~CellList();
    void add(Cell * cell, char type);
    void deleteDeadAndSort();
    int CellTypeSum();
    void wake_oar();
    void add(Cell *cell, char type, int x, int y, int z);
    void add(CellNode * toAdd, char type);
};

struct Source{
    int x, y, z;
    Source * next;
};

class SourceList{
public:
    Source *head, *tail;
    int size;
    SourceList();
    ~SourceList();
    void add(int x, int y, int z);
};
class Grid {
public:
    Grid(int xsize, int ysize, int zsize, int sources_num);
    Grid(int xsize, int ysize, int zsize, int sources_num, OARZone * oar);
    ~Grid();
    void addCell(int x, int y, int z, Cell * cell, char type);
    void fill_sources(double glu, double oxy);
    void cycle_cells();
    void diffuse(double diff_factor);
    void irradiate(double dose);
    void irradiate(double dose, double radius);
    void irradiate(double dose, double radius, double center_x, double center_y, double center_z);
    int pixel_type(int x, int y, int z);
    int pixel_density(int x, int y, int z);
    double ** currentGlucose();
    double ** currentOxygen();
    double tumor_radius(int center_x, int center_y, int center_z);
    void compute_center();
    double get_center_x();
    double get_center_y();
    double get_center_z();
    
private:
    void change_neigh_counts(int x, int y, int z, int val);
    int rand_min(int x, int y, int z, int max);
    int rand_adj(int x, int y, int z);
    int find_missing_oar(int x, int y, int z);
    void min_helper(int x, int y, int z, int& curr_min, int * pos, int& counter);
    void adj_helper(int x, int y, int z, int * pos, int& counter);
    void missing_oar_helper(int x, int y, int z, int&  curr_min, int * pos, int& counter);
    void wake_surrounding_oar(int x, int y, int z);
    void wake_helper(int x, int y, int z);
    int rand_cycle(int num);
    void addToGrid(CellList * newCells);
    int sourceMove(int x, int y, int z);
    int xsize;
    int ysize;
    int zsize;
    CellList *** cells;
    double *** glucose;
    double *** oxygen;
    double *** glucose_helper;
    double *** oxygen_helper;
    int *** neigh_counts;
    SourceList * sources;
    OARZone * oar;
    double center_x;
    double center_y;
    double center_z;
    int * rand_helper;
};

#endif //RADIO_RL_GRID_H