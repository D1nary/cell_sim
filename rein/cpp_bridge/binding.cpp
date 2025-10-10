#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cstdlib>

// Expose private members in this TU to bind internal fields like `grid`
#define private public
#define protected public
// Binding for Controller in C++ simulation (and Grid through it)
#include "../../CellSimLib/include/CellLib/controller.h"
#undef private
#undef protected

namespace py = pybind11;

PYBIND11_MODULE(cell_sim, m) {
  m.doc() = "Python bindings for the C++ cell simulation Controller";

  // Expose Grid minimally, focusing on deep-copy helpers
  py::class_<Grid>(m, "Grid")
      // Python's copy.copy(obj)
      .def("__copy__",
           [](const Grid &self) {
             return Grid(self); // uses C++ deep-copy constructor
           })
      // Python's copy.deepcopy(obj)
      .def("__deepcopy__",
           [](const Grid &self, py::dict /*memo*/) {
             return Grid(self); // deep copy via copy ctor
           })
      // Optional explicit clone method for convenience from Python
      .def(
          "clone", [](const Grid &self) { return Grid(self); },
          "Return a deep-copied Grid")
      .def("get_cell_counts", &Grid::getCellCounts,
           "Return [healthy_count, cancer_count] tracked on this Grid")
      .def_property_readonly(
          "cell_counts",
          [](const Grid &self) { return self.getCellCounts(); },
          "[healthy_count, cancer_count] for this Grid");

  py::class_<Controller>(m, "Controller")
      // Constructor
      .def(py::init<int, int, int, int, double, double, int, int>(),
           py::arg("xsize"), py::arg("ysize"), py::arg("zsize"),
           py::arg("sources_num"), py::arg("cradius"), py::arg("hradius"),
           py::arg("hcells"), py::arg("ccells"))
      // Expose internal grid pointer as a read-only reference
      .def_property_readonly(
          "grid", [](Controller &self) -> Grid & { return *self.grid; },
          py::return_value_policy::reference,
          "Underlying simulation Grid object")
      // Advance simulation by one hour
      .def("go", &Controller::go, "Advance the simulation by one hour")
      // Replace the internal grid content via deep copy (no pointer swap)
      .def("set_grid", &Controller::set_grid, py::arg("grid"),
           "Deep-copy the given Grid into the controller's internal grid")
      // Compute save intervals
      .def("get_intervals", &Controller::get_intervals, py::arg("num_hour"),
           py::arg("divisor"), "Compute tick intervals for data saving")
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
      .def("save_data_tab", &Controller::saveDataTab, py::arg("path"),
           py::arg("filenames"), py::arg("intervals"),
           py::arg("intervals_size"), "Write buffered voxel data to text files")
      .def("save_cell_counts", &Controller::saveCellCounts, py::arg("path"),
           py::arg("filename"), "Write buffered cell counts to a text file")
      // Apply radiation dose
      .def("irradiate", &Controller::irradiate, py::arg("dose"),
           "Irradiate the tumor with a certain dose")
      // Treatment method: irradiate and simulate treatment cycles
      .def("test_treatment", &Controller::test_treatment, py::arg("week"),
           py::arg("rad_days"), py::arg("rest_days"), py::arg("dose"),
           "Perform radiation treatment: simulate for given weeks, radiation "
           "days, rest days, and dose")
      // Check and control tick variable
      .def_readwrite("tick", &Controller::tick, "Current simulation tick")
      .def("get_cell_counts", &Controller::get_cell_counts,
           "Return [HealthyCell::count, CancerCell::count]")

      ;

  // For using C++ random numbers in Python
  m.def("seed", [](unsigned int s) { std::srand(s); }, "Seed the C++ RNG");
}
