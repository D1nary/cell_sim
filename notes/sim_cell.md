# Simulation

The simulation aims to reproduce the dynamics of a three-dimensional cellular environment and to model the impact of ionizing radiation, as occurs in External Beam Radiotherapy (EBR).

The simulation is composed of several files:
- `cell.cpp` and `cell.h`: Implement the classes for the different types of cells and how they respond to radiation.
- `grid_3d.cpp` and `grid_3d.h`: Implement the class for the list of cells present within each voxel of the grid and the 3D grid itself. They integrate the simulation of cell behavior (division, death, awakening) and the dynamics of nutrients and radiation.
- `controller_3d.cpp` and `controller_3d.h`: Coordinate the initialization, updating, and monitoring of the entire simulation, integrating both cell dynamics and the management of treatments and data collection.

# `cell.cpp` file
The `cell.cpp` file manages the behavior of individual cells and the interaction of each with radiation. Each cell is represented by a different class:
- `HealthyCell`: Healthy cells
- `CancerCell`: Cancerous cells
- `OARCell`: Organ At Risk (OAR) cells

The following operations are performed:
- **Cell cycle simulation**: Management of the different phases (quiescence, Gap 1, Synthesis, Gap 2, Mitosis) for each type of cell. Verification of critical nutrient levels (glucose and oxygen) and cell density to decide on progression or cell death.

- **Nutrient consumption**: Calculation of glucose and oxygen consumption based on average values and simulated variability through random distributions.

- **Effects of radiation**: Application of modified models (LQ) to determine the probability of survival after irradiation, with repair mechanisms activated based on the dose.

- **Specific parameters**: Definition of critical constants and coefficients for consumption and response to radiation, differentiated for healthy and tumor cells.


## Glucose/Oxygen efficiency
During the cell cycle, each cell consumes glucose and oxygen. The efficiency with which these nutrients are absorbed is defined by the parameters `glu_efficiency` for glucose and `oxy_efficiency` for oxygen. These parameters are calculated as follows:

- `glu_efficiency = factor * average_glucose_absorption;`
- `oxy_efficiency = factor * average_oxygen_consumption;`

`factor` is obtained by extracting a random number from a **normal distribution**, in order to realistically simulate biological variability.

The use of a normal distribution allows accurate representation of natural variability: many biological phenomena, including glucose absorption, tend to concentrate around a mean (in this case equal to `1.0`) with a certain dispersion determined by a standard deviation (`0.3333`). This distribution produces a bell curve in which most cells exhibit similar behaviors, while some show more marked variations.

To limit maximum absorption, the maximum efficiency value has been set as twice the maximum value (twice the average absorption). This precaution prevents the occurrence of extreme values (negative or excessively high) which, in a biological context, would be meaningless and could compromise the simulation.

For **HealthyCells** and **OARCells**, a stable metabolic behavior is assumed; therefore, the coefficients are fixed at the time of cell instantiation (within the constructor) and remain unchanged throughout the cell's life span. In contrast, for the **CancerCells** class, metabolism is considered more dynamic and variable. Consequently, the parameters related to metabolic efficiency (`glu_efficiency` and `oxy_efficiency`) are recalculated in each life cycle (within the `cycle()` method defined in `cell.cpp`), to reflect possible variations in glucose and oxygen absorption over time.

### Values for oxygen and glucose absorption:
- Glucose:
    - Healthy Cells: `average_glucose_absorption = 0.36` ($\frac{mg}{cell \cdot hour}$. O'Neil)
    - Cancer Cells: `average_cancer_glucose_absorption = 0.54` ($\frac{mg}{cell \cdot hour}$. O'Neil)
- Oxygen:
    - Healthy Cells: `average_oxygen_consumption = 20.0` ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)
    - Cancer Cells: `average_oxygen_consumption = 20.0` ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)

### Threshold values for death and quiescence:
- Glucose:
    - Death: `critical_glucose_level = 6.48` ($\frac{mg}{cell}$. O'Neil)
    - Quiescence: `quiescent_glucose_level = 17.28` ($\frac{mg}{cell}$. O'Neil)
- Oxygen:
    - Death: `critical_oxygen_level = 360.0` ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)
    - Quiescence: `quiescent_oxygen_level = 960.0` ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)

## cell cycle (one hour)
### Healthy Cells
If the cell is not in repair phase (i.e., if `repair` equals 0), the age counter (`age++`) is incremented. If the cell is in repair (repair > 0), the repair counter is decremented and the age is not increased during that hour.

**Cell phases**

The cell has 5 phases: Quiescence (q), Mitosis (m), Gap 2 (2), Synthesis (s), and Gap 1 (1). Every time a phase is completed, the age is reset.
If conditions remain favorable, the cell spends the following number of hours in each phase:
- **Gap 1**: 11 hours
- **Synthesis**: 8 hours
- **Gap 2**: 4 hours
- **Mitosis**: 1 hour

**TOTAL**: 24 hours

If instead, the conditions are not favorable, the cell may return to the quiescence phase only if it is in the Gap 1 phase. In all other phases, no check is performed for the quality of conditions.

The phases are:
- **Phase 'q' (Quiescence)**:
    - The cell consumes 75% of its metabolic capacity (`glu_efficiency` and `oxy_efficiency`).
    - If the external conditions **are** favorable (glucose > `quiescent_glucose_level`, oxygen > `quiescent_oxygen_level`, and number of neighbors less than `critical_neighbors`), the cell "wakes up": age is reset and it moves to phase '1' (Gap 1).

- **Phase '1' (Gap 1)**:
    - The cell consumes its full metabolic capacity.
    - If conditions **are not** favorable (glucose < `quiescent_glucose_level`, oxygen < `quiescent_oxygen_level`, or number of neighbors greater than `critical_neighbors`), the cell returns to quiescence ('q') with age reset. Regarding `critical_neighbors`:
        - In the 2D model a critical number of `9` was chosen.
        - To maintain consistency, a critical value of `27` was chosen for the 3D model.
    - If conditions remain good and age reaches at least **11**, the cell transitions to phase 's' (Synthesis) to prepare for replication.

- **Phase 's' (Synthesis)**:
    - The cell continues to consume at full capacity.
    - When age reaches **8**, the cell completes DNA synthesis and moves to phase '2' (Gap 2), resetting the age.

- **Phase '2' (Gap 2)**:
    - Once again, the cell fully uses its metabolic resources.
    - If age reaches **4**, the cell prepares for division, resets its age, and enters phase 'm' (Mitosis).

- **Phase 'm' (Mitosis)**:
    - During mitosis, the cell consumes full resources.
    - If age equals **1**, the division is complete: the cell returns to Gap 1 (age reset and state change), and a new healthy cell is created (`result.new_cell` set to 'h').

### CancerCells (Differences with HealthyCells)  
- As mentioned in the *Glucose/Oxygen efficiency* section, unlike healthy cells, cancer cells recalculate the efficiency factors for glucose and oxygen consumption at each cycle (every hour) to reflect possible variations in nutrient absorption over time. 
- There is no quiescence phase. 
- Different glucose consumption value: `average_cancer_glucose_absorption`.

## Faster growth of cancer cells
In reality, cancerous cells reproduce faster than healthy ones. This behavior is also replicated in the simulation through various code features:
1. **Order in CellList**: Each voxel of the grid contains a `CellList` object that holds all the cells inside. In this list, cancerous cells (`CancerCells`) are placed before healthy cells (`HealthyCells`).
As a result, when iterating through all cells in the list, cancer cells consume available nutrients in the voxel first. This mechanism reduces the remaining resources for healthy cells, increasing the chance that oxygen and glucose levels fall below critical thresholds, triggering quiescence or cell death.

2. **Quiescence**: `HealthyCells` objects, when in the `G1` phase, may enter a quiescent state if any of the previously mentioned conditions are met.

    In this state, cells do not proceed with the cell cycle and therefore lose the chance to divide and create new cells. Their age, if not in repair, is still updated.

3. **Condition to transition to next phases**: The condition for a healthy cell to move to the next phase is stricter. Specifically, its age must be exactly equal to (`==`) a specific value. In contrast, cancer cells can proceed if their age is greater than or equal to (`>=`) that value.

4. **Higher nutrient consumption**: Cancer cells consume more glucose than healthy ones. Combined with their priority in the list, this leads to a significant reduction of available nutrients for healthy cells. Consequently, healthy cells are more likely to experience nutrient deficiency, leading to quiescence or death.

## Cell death
Cell death occurs if oxygen **or** glucose levels fall below a critical threshold. These levels are the same for both `HealthyCells` and `CancerCells`.

- **Glucose**: **`critical_glucose_level = 6.48`** ($\frac{mg}{cell}$. O'Neil)
- **Oxygen**: **`critical_oxygen_level = 360.0`** ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)

## Consumption process in cycle_cells (in `grid.cpp`)
The algorithm iterates through each voxel of the grid and, for each voxel, iterates through every cell inside it.

For each cell, the nutrient consumption is calculated. This value is then subtracted from the total available in the voxel.

This sequence ensures that cells progressively alter the availability of resources in their environment, thereby influencing the behavior and survival of other cells within the grid.

## Radiation
Each cell has a certain probability of surviving radiation. This varies depending on whether the cell is healthy or cancerous.

In both cases, the probability of survival after irradiation is calculated using a modified **LQ** (**Linear-Quadratic**) model.

### Healthy Cells
$$
P_{survival} = \exp\Big( \gamma \cdot \Big(-\alpha \cdot d - \beta \cdot d^2\Big) \Big)
$$

Where:
- **$d$** is the radiation dose (in grays).
- **$\alpha$** corresponds to the `alpha_norm_tissue` parameter in the code.
- **$\beta$** corresponds to the `beta_norm_tissue` parameter in the code.
- **$\gamma$** is a modifying factor depending on the **stage** of the cell:
  - If the stage is `'2'` or `'m'`: $\gamma = 1.$
  - If the stage is `'1'` (or by default): $\gamma = 1$
  - If the stage is `'q'` or `'s'`: $\gamma = 0.$

### Cancer Cells
$$
P_{survival} = \exp\Big( \gamma \cdot \big(-\alpha_{tumor} \cdot d - \beta_{tumor} \cdot d^2\big) \Big)
$$

Where:
- **$d$** is the radiation dose (in grays).
- **$\alpha_{tumor}$** represents the `alpha_tumor` parameter.
- **$\beta_{tumor}$** represents the `beta_tumor` parameter.
- **$\gamma$** is a modifying factor depending on the **stage** of the cell:
  - If the stage is `'2'` or `'m'`: $\gamma = 1.25$
  - If the stage is `'1'` or default: $\gamma = 1.0$
  - If the stage is `'s'`: $\gamma = 0.75$

### Parameters used:
- `alpha_tumor = 0.3` (Powathil)
- `beta_tumor = 0.03` (Powathil)
- `alpha_norm_tissue = 0.15`
- `beta_norm_tissue = 0.03`

### Death and repair
After calculating the survival probability, a random number is generated to determine whether the cell dies or not.

If the cell does not die and the dose is greater than `0.5`, a repair time is calculated and added with:

`repair += (int) round(2.0 * uni_distribution(generator) * (double) repair_time );`
