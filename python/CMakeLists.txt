cmake_minimum_required(VERSION 3.10)
project(cell_sim_python)

# FetchContent per pybind11
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# Include la cartella degli header C++
include_directories(${CMAKE_SOURCE_DIR}/../cpp/src)

# Crea il modulo Python 'cell_sim'
pybind11_add_module(cell_sim
    binding.cpp
    ../cpp/src/controller_3d.cpp
    ../cpp/src/grid_3d.cpp
    ../cpp/src/cell.cpp
)

target_link_libraries(cell_sim PRIVATE pybind11::module)

# Configura output in python/ accanto a control.py
set_target_properties(cell_sim PROPERTIES
    PREFIX ""
    OUTPUT_NAME "cell_sim"
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}
)
