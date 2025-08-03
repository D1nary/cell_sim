# General info
To be tested, each code must be pasted into the main.cpp file in the src folder.

# neigh_counts (`neigh_counts.cpp`)
Test of the behavior of the extreme values in the neigh_counts matrix. The matrix is initialized to 0, and a specific layer is printed. 

This allows observation of the correct application of a bias at the boundary values.

## Code
[neigh_counts.cpp](../cpp/tested/neigh_counts.cpp)

## Output
```
Layer z = 0 e z = 3 

19 15 15 19
15  9  9 15
15  9  9 15
19 15 15 19

Layer z = 1 e z = 2

15  9  9 15
 9  0  0  9
 9  0  0  9
15  9  9 15
```

# change_neigh_counts (`change_neigh_counts.cpp`)
Given the initial state of the `neigh_counts` matrix and the coordinates of a voxel within it, this program updates the neighbor count of the voxels adjacent to the selected voxel using the `change_neigh_counts()` function.

For example, we want to update the neighors of x = 2, y = 2 and z = 1

## Code
[change_neigh_counts.cpp](../cpp/tested/change_neigh_counts.cpp)

## `neigh_counts` initial state

```
Layer z = 0 e z = 3 

19 15 15 19
15  9  9 15
15  9  9 15
19 15 15 19

Layer z = 1 e z = 2

15  9  9 15
 9  0  0  9
 9  0  0  9
15  9  9 15
```

## Output

```
Layer z = 0:
19      15      15      19
15      10      10      16
15      10      10      16
19      16      16      20

Layer z = 1:
15      9       9       15
9       1       1       10
9       1       0       10
15      10      10      16

Layer z = 2:
15      9       9       15
9       1       1       10
9       1       1       10
15      10      10      16

Layer z = 3:
19      15      15      19
15      9       9       15
15      9       9       15
19      15      15      19
```

# sources (`sources.cpp`)
Check che right creation of the source list.

Print on screen the specified number (`size`) of Source objects contained in `SourceList`, along with their randomly generated x, y, and z coordinates.

## Code
[souces.cpp](../cpp/tested/sources.cpp)

## Output

```
size = 4
Source at:
z  = 2, x =  0, y = 2
Source at:
z  = 0, x =  3, y = 0
Source at:
z  = 3, x =  3, y = 2
Source at:
z  = 1, x =  0, y = 2
```

# fill_sources and sourceMove (`source_move.cpp`)
The goal is to verify the correct functioning of the movement of a nutrient source and the proper filling of glucose (the same applies to oxygen).
A single source is considered (`SourceList` with only one node) to be able to track its movement within the glucose or oxygen grid.
The test algorithm is as follows:

```
Flowchart of the program:

Start
  |
  v
Print initial position (added to SourceList)
  |
  v
Compute tumor center
  |
  v
Execute fill_sources()
  |
  |-- Fill the glucose matrix
  |-- Move the source
  |-- Movement is either random or directed toward the tumor center
  |-- Calculate new positions
  |
  v
Print updated matrix values
  |
  v
Print new source positions
  |
  v
End
```

**NOTE**: Since I first fill the matrix and then compute the new positions, in the output matrix I display the previous movement (or the initial position, since `fill_source()` is the first to be executed).

## Code
[souces.cpp](../cpp/tested/source_move.cpp)

## Code changes
- Replacement of `if ((rand() % 24) < 1)` with `if (true)` in `fill_sources()`. Since the source movement occurs once every 24 hours, setting the condition to `true` ensures that the movement occurs every time the program is run and not with a probability of 1/7.

- Replacement of the probability condition `if (rand() % 50000 < CancerCell::count)` with `if (rand() % 2 == 0)` so that there is a 50% probability for movement toward the center and a 50% probability for random movement.

- Addition of the following lines of code in `SourceList::add` to print the initial source position:
    ```cpp
    cout << "Initial position" << endl;
    cout << "x = " << x << endl;
    cout << "y = " << y << endl;
    cout << "z = " << z << endl;
    ```

# Growth test (`growth.cpp`)
This test verifies the correct functioning of the simulation regarding tumor growth. The simulation starts from an initial grid and runs for a few hours, checking the correct growth of the tumor.
For an explanation of the functioning and data saving, see [sim_cell.cpp](../cpp/tested/sim_cell.cpp) and [grid_contr.cpp](../cpp/tested/grid_contr.cpp).

## Code
[growth.cpp](../cpp/tested/growth.cpp)

