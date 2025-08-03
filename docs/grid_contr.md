# `grid_3d.cpp` file

The file models the behavior of a cellular environment in the 3D grid and integrates the dynamics of nutrients and radiation.

## General Description of File Functions
### Cell Management (CellList)
- **Creation and destruction**: A linked list (`CellList`) is implemented to manage the cell nodes (`CellNode`).

- **Adding cells**:  
  - The `add` method is used to insert new cells; cancer cells are added at the beginning, while healthy and OAR cells are added at the end. Internal counters for cancer cells are updated.

- **Cleaning and sorting**: The `deleteDeadAndSort()` function scans the list, removing dead cells and updating the links to maintain order.

### Nutrient Sources Management (SourceList)

- **Creation and update**: A list is used to manage nutrient sources. Nutrient sources are randomly placed within the grid.

### 3D Grid Management (Grid)
- **Allocation and initialization**: Three separate grids are created:
    - One for the lists of cells in each voxel.
    - One for glucose levels (initialized to `100.0`) and oxygen (initialized to `1000.0`).

- **Placement and update of sources**: Nutrient sources are randomly placed and updated via `fill_sources()`, which adds nutrients at the source positions and moves them daily. There is a probability of movement towards the tumor center given by the condition `if (rand() % 50000 < CancerCell::count)`.

- **Cell cycling**: The `cycle_cells()` function iterates over all voxels, advancing the cell cycle based on nutrient consumption and local density. It handles cell division and new cell creation if conditions permit and cleans up dead cells from the list.

- **Nutrient diffusion**: The `diffuse()` function models glucose and oxygen dispersion. Each voxel retains part of its content, while a fraction is equally diffused to the 26 neighboring voxels.

- **Irradiation**: Implemented through the `irradiate()` function, which:
    - Calculates the tumor center and the radius based on the maximum distance of cancer cells.
    - Applies a radiation dose to voxels containing cells, modulating the effect according to the distance from the center (of the tumor) and the oxygen level (using formulas and correction factors).

## Cellular Irradiation

Radiation sent to the cells follows a Gaussian distribution, with cells closer to the irradiation center receiving a higher dose than those farther away, following a bell-shaped curve. The dose is thus adjusted based on the irradiation center.

The irradiation center is considered the tumor center calculated with the `compute_center()` method. This computes the centroid of the cancer cells present in the 3D grid, i.e., the average position weighted by the number of cancer cells in each voxel.

The dose for each cell in each voxel is calculated as:

$$
\text{dose} = \text{multiplicator} \cdot \text{conv(rad, dist)} \cdot \text{omf}
$$

### conv()

$\text{conv(rad, dist)}$ is defined as $\text{erf}(\text{rad} - \text{x}) - \text{erf}(-\text{rad} - \text{x})$

- $\text{erf()}$: Gaussian error function (closely related to the normal distribution)
- $\text{rad}$: Radius in which 95% of the total radiation is contained
- $\text{x}$: **Normalized** distance from the irradiation center

The goal is to obtain a dose value proportional to the distance from the irradiation center. Higher doses should be in positions close to the center, and lower doses farther away. The `conv()` function enables this behavior. Note that `conv()` is not a dose value but a quantity indicating how high or low the dose should be.

`dist` is the normalized distance from the irradiation center. It is passed to the `conv()` function as:

$$
\frac{x \cdot 10}{radius}
$$

Where $x$ is the distance, in voxels, from the center, and $\text{radius}$ is the tumor radius calculated with `tumor_radius()`, which finds the farthest location from the center with a cancer cell and computes its distance.

- Range of $x$ values **before normalization**: $[0, 3 \cdot \text{radius}]$. In `irradiate()` (`grid_3d.cpp`) radiation is applied to cells only if the condition `if (cells[k][i][j].size && dist < 3 * radius)` is met.
- Range of $x$ values **after normalization**: $[0, 30]$ regardless of $\text{radius}$.

### multiplicator

Since `conv()` does not provide an actual dose value, the `multiplicator` parameter is introduced. It is determined via the `get_multiplicator()` method, which calculates the ratio between the maximum `dose` value and the `conv()` value at the distribution center. This way, by multiplying `multiplicator` by the `conv()` value at a given distance from the center, the correct dose value is obtained to pass to `radiate()`.

### Oxygen Modification Factor (OMF)

For each voxel in the grid, the OMF is calculated. It represents the potentiating effect of oxygen on the radiosensitivity of tumor tissues. When oxygen levels in tissues are high, the damage induced by ionizing radiation on tumor cell DNA is amplified. It is calculated as:

$$
\text{OMF} = \frac{\frac{\text{oxygen}}{100} \cdot \text{oer}_m + k_m}{\left(\frac{\text{oxygen}}{100} + k_m\right) \cdot \text{oer}_m}
$$

where:

- $\text{oxygen}$ is the oxygen value in the voxel (read from oxygen[k][i][j]),
- `oer_m` and `k_m` are constants both set to `3.0`.

This factor modifies the radiation dose applied to cells:

- With high oxygenation, OMF will be greater, increasing dose effectiveness.
- With low oxygenation, OMF will be lower, reflecting the higher resistance of hypoxic cells to radiation.

# `controller_3d.cpp` file

The file manages the interaction and overall dynamics of the simulation, orchestrating the actions performed on the 3D grid (`Grid`).

## General Functionality

### Grid Creation and Filling

- Creation of an initial grid: (`grid_creation(cradius, hradius)`):

  An initial grid `noFilledGrid` is generated to serve as the base for creating the grid with cells. It classifies each voxel according to its distance from the center:
  - `-1`: inner voxel (within tumor radius `cradius`).
  - `1`: intermediate voxel (between `cradius` and `hradius`).
  - `0`: outer voxel.

- Grid population: (`fill_grid(hcells, ccells, noFilledGrid)`):
  A 3D grid containing cells is created following the `noFilledGrid` configuration:
  - Adds `hcells` healthy cells in voxels classified as `1` or `-1`.
  - Adds `ccells` cancer cells exclusively in voxels classified as `-1`.

### Cell Evolution and Irradiation

- One hour simulation step (`go()`):
  - Fill nutrient sources (`fill_sources()`).
  - Cell cycle update (`cycle_cells()`).
  - Nutrient diffusion (`diffuse()`).
  - Daily tumor center calculation (`compute_center()`).

- Irradiation (`irradiate(dose)`):
  - Applies radiation to the tumor according to a specified dose.

### Data Saving
Data are saved in two types of files:
- **Grid data files**: In the form `tx_gd.txt` where `x` corresponds to the simulation hour (tick) at which the data were saved. These files contain the following 3D grid information arranged in a row:
  - Tick
  - Voxel coordinates: x, y, z
  - Cell counters in the voxel: healthy, cancer, and OAR cells
  - Nutrient levels: oxygen and glucose
  - Voxel type: `-1` if the voxel contains at least one cancer cell, `1` if it contains only healthy cells, and `0` if it contains no cells

  These files are saved at specific intervals (ticks). Intervals are created with `get_intervals()` and stored in the variable `intervals1` for the growth phase and `intervals2` for the treatment phase.

- **Cell counter files**: These files contain the following information:
  - Tick
  - **Total** number of healthy, cancer, and OAR cells present in the entire grid.

  Two separate files are used:
    - `cell_counts_gr.txt`: For data during the growth phase
    - `cell_counts_gtr.txt`: For data during the treatment phase

  During the growth phase, information is saved at every tick, while in the treatment phase, it is saved every 24 hours.

### Treatment Plan
The therapeutic treatment is managed by the method `treatment()`. It is defined by several parameters:
- `week = 2`: Weeks of treatments
- `rad_days = 5`: Number of days in which radiation is applied
- `rest_days = 2`: Number of days without radiation
- `dose = 2.0`: Dose per day


