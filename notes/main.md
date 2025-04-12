# `main.cpp` file
This is the master controller of the file. It performs the following operations:

```
Start
  |
  v
Initialize variables and parameters
  |
  v
Create necessary directories
  |
  v
Initialize Controller and grid
  |
  v
Create voxel-saving intervals (growth and treatment)
  |
  v
Create and fill grid with healthy and cancer cells
  |
  v
Tumor growth simulation loop
  |-- If current hour matches saving interval:
  |     |-- Save voxel data
  |     |-- Print tick and cell counters
  |-- If matches cell count interval:
  |     |-- Save cell count data
  |-- Advance grid state (controller->go())
  |
  v
Save growth data to files
  |
  v
Print "BEGIN RADIATION TREATMENT"
  |
  v
Set new number of hours and intervals for treatment
  |
  v
Reset tick counter
  |
  v
Execute treatment (controller->treatment)
  |
  v
Save treatment data to files
  |
  v
End
```