#ifndef CELLULAR_LIB_GRID_H
#define CELLULAR_LIB_GRID_H

#include "cell.h"
#include <array>

struct CellNode
{
    int x, y, z;
    Cell * cell;
    CellNode *next;
    char type;
};

struct OARZone{
    int x1, x2, y1, y2, z1, z2;
};


class CellList{
private:
    void clear_();
    void copy_from_(const CellList& other);

public:
    CellNode *head, *tail;
    int size;
    int oar_count;
    int ccell_count;
    CellList();
    ~CellList() noexcept;
    void add(Cell * cell, char type);
    void deleteDeadAndSort();
    int CellTypeSum();
    void wake_oar();
    void add(Cell *cell, char type, int x, int y, int z);
    void add(CellNode * toAdd, char type);

    CellList(const CellList& other);
    CellList& operator=(const CellList& other);

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
    ~SourceList() noexcept;
    void add(int x, int y, int z);
    SourceList(const SourceList& other);
    SourceList& operator=(const SourceList& other);

private:
  void clear_();
  void copy_from_(const SourceList& other);

};

class Grid {
public:
    Grid(int xsize, int ysize, int zsize, int sources_num);
    Grid(int xsize, int ysize, int zsize, int sources_num, OARZone * oar);
    ~Grid() noexcept;
    void addCell(int x, int y, int z, Cell * cell, char type);
    void fill_sources(double glu, double oxy);
    void cycle_cells();
    void diffuse(double diff_factor);
    void irradiate(double dose);
    void irradiate(double dose, double radius, double center_x, double center_y, double center_z);
    int pixel_type(int x, int y, int z);
    int pixel_density(int x, int y, int z);
    double *** currentGlucose();
    double *** currentOxygen();
    double tumor_radius(int center_x, int center_y, int center_z);
    void compute_center();
    double get_center_x();
    double get_center_y();
    double get_center_z();
    int getHealthyCount(int x, int y, int z);
    int getCancerCount(int x, int y, int z);
    int getOARCount(int x, int y, int z);
    void change_neigh_counts(int x, int y, int z, int val);

    int*** getNeighCounts() const;
    SourceList* getSources() const;
    double*** getGlucose() const;
    std::array<int, 2> getCellCounts() const { return cell_counts; }
    
    Grid(const Grid& other);
    Grid& operator=(const Grid& other);
    // Evita move semantiche ambigue con raw pointer (fino a implementazione ad hoc)
    Grid(Grid&&) = delete;
    Grid& operator=(Grid&&) = delete;

private:
    // void change_neigh_counts(int x, int y, int z, int val);
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
    // [healthy_count, cancer_count]
    std::array<int, 2> cell_counts;

    void alloc_all_();
    void free_all_(); 
    void copy_from_(const Grid& other);
};
#endif
