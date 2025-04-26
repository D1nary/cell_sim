#include <pybind11/pybind11.h> // PROBLEMA DI VSCODE
#include <pybind11/stl.h>

// Binding for Controller in C++ simulation
#include "../cpp/src/controller_3d.h"

namespace py = pybind11;

PYBIND11_MODULE(cell_sim, m) {
    m.doc() = "Python bindings for the C++ cell simulation Controller";

    py::class_<Controller>(m, "Controller")
        // Constructor used in main.cpp
        .def(py::init<int, int, int, int, double, double, int, int, const std::vector<int>&>(),
             py::arg("xsize"), py::arg("ysize"), py::arg("zsize"),
             py::arg("sources_num"), py::arg("cradius"), py::arg("hradius"),
             py::arg("hcells"), py::arg("ccells"), py::arg("intervals"))
        // Advance simulation by one hour
        .def("go", &Controller::go, "Advance the simulation by one hour")
        // Compute save intervals
        .def("get_intervals", &Controller::get_intervals,
             py::arg("num_hour"), py::arg("divisor"),
             "Compute tick intervals for data saving")
        // Create directories
        .def("create_directories", &Controller::createDirectories,
             py::arg("paths"),
             "Create output directories for results")
        // Data collection
        .def("temp_data_tab", &Controller::tempDataTab,
             "Collect voxel data into internal buffer")
        .def("temp_cell_counts", &Controller::tempCellCounts,
             "Collect cell counts into internal buffer")
        // Save data to files
        .def("save_data_tab", &Controller::saveDataTab,
             py::arg("path"), py::arg("filenames"), py::arg("intervals"), py::arg("intervals_size"),
             "Write buffered voxel data to text files")
        .def("save_cell_counts", &Controller::saveCellCounts,
             py::arg("path"), py::arg("filename"),
             "Write buffered cell counts to a text file");
        // For using c++ random numbers in python
        m.def("seed", [](unsigned int s){
               std::srand(s);
           }, "Seed the C++ RNG");
}
