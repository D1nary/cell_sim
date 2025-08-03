# Minimum required version of CMake
cmake_minimum_required(VERSION 3.10)

# Ensures the user has at least version 3.10 of CMake.
# If the user has an older version, CMake will display an error.

# Defines the project name
# The project name is used internally by CMake to organize the configuration.
project(cell_simulation)

# Sets the C++ standard
# If the compiler does not support C++17, configuration will fail.
set(CMAKE_CXX_STANDARD 17) # Use the C++17 standard
set(CMAKE_CXX_STANDARD_REQUIRED True) # Enforce the use of C++17

# Adds the project executable
# The first argument (main) is the name of the generated executable
# The following files are the source files needed for compilation
# Source files required for compilation are main.cpp, controller_3d.cpp, grid_3d.cpp, and cell.cpp.
add_executable(main
    src/main.cpp         # Main file containing the main function
    src/controller_3d.cpp # Source file implementing the Controller class
    src/grid_3d.cpp       # Source file implementing the Grid class
    src/cell.cpp          # Source file implementing the Cell class
)

# The command target_include_directories(<target> <ACCESS_MODE> <DIRECTORY>...) in CMake
# is used to specify directories where the header files (.h) required for
# compiling a target are located. Where:
# <target> → Name of the target (executable or library).
# <ACCESS_MODE> → Type of access these directories have relative to dependent targets.
# <DIRECTORY> → One or more directories containing the header files.
target_include_directories(main PRIVATE src)