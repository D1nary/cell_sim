cmake_minimum_required(VERSION 3.10)

# Project that builds the core simulation library and a small demo
project(CellSimLib)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Library with the cellular simulation sources
add_library(cell_sim
    ../src/cell.cpp
    ../src/controller.cpp
    ../src/grid.cpp
)

target_include_directories(cell_sim
    PUBLIC
        ../include
)

