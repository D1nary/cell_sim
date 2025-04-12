# Build Requirements

- **C++ Compiler**: GCC 13.3.0 (tested with `g++ (Ubuntu 13.3.0-6ubuntu2~24.04)`)
- **Build System**: CMake 3.28.3
- **Operating System**: Linux (tested on Ubuntu 24.04)

Make sure `g++` and `cmake` are installed and accessible from your terminal. You can check your versions with:

```bash
g++ --version
cmake --version
```

# Simulation Code Directories Structure

This directory contains the main code folders for the simulation:

- `src`: Source files for the simulation.

- `graph_codes`: Scripts used for generating plots and visualizations.

- `tested`: Contains test files for various simulation features.

- `results`: Stores simulation results. This includes folders for saving text files from both the growth and treatment phases, as well as directories for saving plots. For detailed information on how data is saved, refer to the file [grid_contr.md](../notes/grid_contr.md).

# How to run

## Project Structure

```
cell_sim/
├── cpp/
│   ├── CMakeLists.txt       # <-- The correct CMake file to use
│   ├── src/
│   │   ├── main.cpp
│   │   ├── controller_3d.cpp
│   │   ├── grid_3d.cpp
│   │   ├── cell.cpp
│   │   ├── controller_3d.h
│   │   ├── grid_3d.h
│   │   └── cell.h
```

## Build folder location
The `build` folder must be placed inside the `cpp/` directory to avoid issues with the management of the `results` folder during simulation. Additionally, this is where the `CMakeLists.txt` file is located.

## Run from terminal

### Terminal commands

```bash
cd cpp           # Navigate to the directory with the correct CMakeLists.txt
mkdir build      # Create the build directory
cd build         # Enter the build directory
cmake ..         # Configure the project
make             # Compile the project
./main           # Run the compiled executable
```

### Output
After compilation, the `main` executable will be located at:
```
cell_sim/cpp/build/main
```

## Run with VSCode CMake Tools
**Tip**: To ensure that the `build` folder is created in the correct location, add the following lines to the `settings.json` file inside the `.vscode` directory:

```
{
  "cmake.sourceDirectory": "${workspaceFolder}/cpp",
  "cmake.buildDirectory": "${workspaceFolder}/cpp/build"
}
```
This way, CMake Tools will understand that it should use `cpp/CMakeLists.txt` and the `build/` folder will be created inside `cpp/`.