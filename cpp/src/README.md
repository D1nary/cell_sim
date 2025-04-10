# Source Code Overview

This directory contains the source code files for the simulation:

- `main.cpp`: The main file that controls the simulation.

- `cell.cpp` and `cell.h`: Implement the classes for the different types of cells and how they respond to radiation.

- `grid_3d.cpp` and `grid_3d.h`: Implement the class for the list of cells present within each voxel of the grid and the 3D grid itself. They integrate the simulation of cell behavior (division, death, awakening) and the dynamics of nutrients and radiation.

- `controller_3d.cpp` and `controller_3d.h`: Coordinate the initialization, updating, and monitoring of the entire simulation, integrating both cell dynamics and the management of treatments and data collection.

- `2d_version`: Contiene la versione 2D della simulazione. Sono i file che si trovano nel progetto [radio_rl](https://github.com/gregoire-moreau/radio_rl.git) di [Grégoire Moreau](https://github.com/gregoire-moreau).

- `CmakeList.txt`: Build configuration file used to compile `main.cpp`.

