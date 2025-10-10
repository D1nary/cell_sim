# ---
# File: rein/CMakeLists.txt
# Purpose: Build Python bindings (cell_sim module) for control.py
# ---

cmake_minimum_required(VERSION 3.10)

# Find dependencies
find_package(pybind11 REQUIRED)
find_package(Python3 COMPONENTS Development REQUIRED)

# Build the Python extension module from the cpp_bridge sources
# Use a different target name and set OUTPUT_NAME to "cell_sim"
pybind11_add_module(cell_sim_py cpp_bridge/binding.cpp)
set_target_properties(cell_sim_py PROPERTIES OUTPUT_NAME cell_sim)

# Include headers from the core C++ library
target_include_directories(cell_sim_py PRIVATE
    ${CMAKE_SOURCE_DIR}/CellSimLib/include
)

# Link against the core simulation library
target_link_libraries(cell_sim_py PRIVATE cell_sim)

# Place the built module (cell_sim.so) next to control.py
set_target_properties(cell_sim_py PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/rein
)
