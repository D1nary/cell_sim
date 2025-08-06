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


# Ensures that all headers under ../include are visible
# when compiling cell_sim and any targets that will then bind it.
target_include_directories(cell_sim
    PUBLIC
        ../include
)

# Define an executable that compiles main.cpp
add_executable(CellSimDemo
  main.cpp
)

# Link the executable to the library
target_link_libraries(CellSimDemo
  PRIVATE
    cell_sim
)