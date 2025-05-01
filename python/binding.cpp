#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// Binding for Controller in C++ simulation
#include "../cpp/src/controller_3d.h"

namespace py = pybind11;

PYBIND11_MODULE(cell_sim, m) {
    m.doc() = "Python bindings for the C++ cell simulation Controller";

    py::class_<Controller>(m, "Controller")
        // Constructor
        .def(py::init<int, int, int, int, double, double, int, int>(),
             py::arg("xsize"), py::arg("ysize"), py::arg("zsize"),
             py::arg("sources_num"), py::arg("cradius"), py::arg("hradius"),
             py::arg("hcells"), py::arg("ccells"))
        // Advance simulation by one hour
        .def("go", &Controller::go, "Advance the simulation by one hour")
        // Compute save intervals
        .def("get_intervals", &Controller::get_intervals,
             py::arg("num_hour"), py::arg("divisor"),
             "Compute tick intervals for data saving")
        // Data collection: voxel buffer
        .def("temp_data_tab", &Controller::tempDataTab,
             "Collect voxel data into internal buffer")
        // Clear voxel buffer
        .def("clear_tempDataTab", &Controller::clear_tempDataTab,
             "Clear the temporary voxel data buffer")
        // Data collection: cell counts buffer
        .def("temp_cell_counts", &Controller::tempCellCounts,
             "Collect cell counts into internal buffer")
        // Clear cell counts buffer
        .def("clear_tempCellCounts", &Controller::clear_tempCellCounts,
             "Clear the temporary cell counts buffer")
        // Save data to files
        .def("save_data_tab", &Controller::saveDataTab,
             py::arg("path"), py::arg("filenames"), py::arg("intervals"), py::arg("intervals_size"),
             "Write buffered voxel data to text files")
        .def("save_cell_counts", &Controller::saveCellCounts,
             py::arg("path"), py::arg("filename"),
             "Write buffered cell counts to a text file")
        // Apply radiation dose
        .def("irradiate", &Controller::irradiate,
             py::arg("dose"),
             "Irradiate the tumor with a certain dose")
        // Treatment method: irradiate and simulate treatment cycles
        .def("test_treatment", &Controller::test_treatment,
             py::arg("week"), py::arg("rad_days"), py::arg("rest_days"), py::arg("dose"),
             "Perform radiation treatment: simulate for given weeks, radiation days, rest days, and dose")
        // Check and control tick variable
        .def_readwrite("tick", &Controller::tick, "Current simulation tick")
        .def("get_cell_counts",
          &Controller::get_cell_counts,
          "Return [HealthyCell::count, CancerCell::count]")
        ;

    // For using C++ random numbers in Python
    m.def("seed", [](unsigned int s){
           std::srand(s);
       }, "Seed the C++ RNG");
}
