cmake_minimum_required(VERSION 3.10)

# Main project definition
project(CELL_SIM VERSION 1.0 LANGUAGES CXX)

# Use C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define PROJECT_ROOT for use in code
add_compile_definitions(PROJECT_ROOT="${CMAKE_SOURCE_DIR}")

# Add subdirectory for the core library and demo
add_subdirectory(CellSimLib/app)