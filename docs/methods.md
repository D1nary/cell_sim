# List of Analyzed Methods

- `neigh_count` Matrix
- `change_neigh_counts()`
- `fill_sources()`
- `sourceMove()`
- `rand_adj()`
- `adj_helper()`
- `cycle_cells()`
- `rand_min()`
- `min_helper()`
- `diffuse()`
- `diffuse_helper()`
- `deleteDeadAndSort()`

# `neigh_count` Matrix
The `neigh_counts` matrix is an array that stores, for each voxel in the grid, the number of cells present in adjacent voxels, excluding those in the voxel itself. It is used to evaluate the local density around each voxel (number of neighboring cells).

## Border Voxels
Voxels at the center of the grid can potentially have 26 adjacent voxels, while those on the edges or corners have fewer. The code adds fixed offsets at the borders. This way, it simulates that each voxel "virtually" has 26 neighbors, making density values comparable regardless of position in the grid.

**Note**: The correction does not aim to add virtual cells but to normalize the neighbor count value.

### Voxel Count on Edges and Corners
```
Layer 1             Layer 2
19 15 15 19         15  9  9 15
15  9  9 15          9  0  0  9
15  9  9 15          9  0  0  9
19 15 15 19         15  9  9 15

Layer 3             Layer 4
15  9  9 15         19 15 15 19
 9  0  0  9         15  9  9 15
 9  0  0  9         15  9  9 15
15  9  9 15         19 15 15 19
```

### Code for Edge Offset
The following lines of code add the offset to the edges of the 3D grid.
```cpp
// Add offset to borders of the matrix
for (int k = 0; k < zsize; k++) {         // Iterate over layers (z-axis)
    for (int i = 0; i < xsize; i++) {     // Iterate over rows (x-axis)
        for (int j = 0; j < ysize; j++) { // Iterate over columns (y-axis)
            // Determine possibilities based on position
            int poss_z = (k == 0 || k == zsize - 1) ? 2 : 3;
            int poss_x = (i == 0 || i == xsize - 1) ? 2 : 3;
            int poss_y = (j == 0 || j == ysize - 1) ? 2 : 3;

            // Calculate product of possibilities:
            int prod = poss_z * poss_x * poss_y;
            // Calculate value: value = n_max - neighbors = 27 - prod
            int valore = 27 - prod;

            // Since each element is initialized to 0, we can simply assign:
            neigh_counts[k][i][j] = valore;
        }
    }
}
```

## Updating `neigh_count` when Adding a Cell with `change_neigh_counts()`
When adding a cell at (x, y, z) using the `addCell` method, `neigh_count` must be updated. This update reflects that placing a new cell increases the neighbor count for all adjacent voxels by 1. The `change_neigh_counts()` method handles this.

### Code
```cpp
/**
 * Add a cell to a position on the grid
 *
 * @param x The x coordinate where we want to add the cell
 * @param y The y coordinate where we want to add the cell
 * @param z The z (layer) coordinate where we want to add the cell
 * @param cell The cell that we want to add to the CellList
 * @param type The type of the Cell
 */
void Grid::addCell(int x, int y, int z, Cell *cell, char type) {
    cells[z][x][y].add(cell, type,x, y, z);
    // Why change_neigh_counts? See notes
    change_neigh_counts(x, y, z, 1);
}
```

# Sources: **`fill_sources()`**, **`sourceMove()`**, **`rand_adj()`**, **`adj_helper()`**
These methods handle the addition of glucose and oxygen to the voxels where sources are located and move the sources to other voxels.

The idea is that, on average, a source moves once every 24 calls to the method, which in the simulation context corresponds to approximately one movement per day (24 hours).

## Code
```cpp
void Grid::fill_sources(double glu, double oxy) {
    Source * current = sources -> head;
    while(current){ // We go through all sources
        glucose[current->z][current->x][current->y] += glu;
        oxygen[current->z][current->x][current->y] += oxy;
        if ((rand() % 24) < 1){ // The source moves on average once a day
            int newPos = sourceMove(current->x, current->y);
            current -> x = newPos / ysize;
            current -> y = newPos % ysize;
        }
        current = current -> next;
    }
}

int Grid::sourceMove(int x, int y, int z) {
    if (rand() % 50000 < CancerCell::count) { // Move towards the tumor center

        // Code lines
        ...

        // Encode new position as a single integer:
        // (z * xsize * ysize) + (x * ysize) + y
        return z * xsize * ysize + x * ysize + y;
    } else {
        // Move in a random direction (make sure to have 3D version of rand_adj)
        return rand_adj(x, y, z); // SEE
    }
}
```
Where:
- `rand() % 24`: Generates an integer between 0 and 23.
- The condition `(rand() % 24) < 1` is true only if the generated number is `0`.
    - This happens with a probability of $\frac{1}{24}$ (about 4.17% of the time).
- The **coordinate extraction** follows.

## Coordinate Extraction
A source can move either toward the tumor center or in a random direction. The probability of moving toward the tumor center is given by:
```cpp
if (rand() % 50000 < CancerCell::count)
```
For example:
- If `CancerCell::count` is 1, the probability is $\frac{1}{50000} = 0.002\%$
- If `CancerCell::count` is 25000, the probability is $\frac{25000}{50000} = 0.5 = 50\%$

### Movement Toward the Center
If this condition is met, the new position (x, y, z) is calculated as follows:
```cpp
int newPos = sourceMove(current->x, current->y, current->z);
```
The coordinates are packed into a single integer `newPos` returned by the function `sourceMove()`, which is in the form:
```
(z * xsize * ysize) + (x * ysize) + y
```
The new x, y, and z coordinates are then extracted with:
```cpp
int newZ = newPos / (xsize * ysize);
int rem = newPos % (xsize * ysize);
int newX = rem / ysize;
int newY = rem % ysize;
```

- **Extraction of z**:
```cpp
int newZ = newPos / (xsize * ysize);
```
$$
\text{newPos} = (z \cdot x_{\text{size}} \cdot y_{\text{size}}) + (x \cdot y_{\text{size}}) + y
$$
$$
\text{newZ} = \frac{z \cdot x_{\text{size}} \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} + \frac{x \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} + \frac{y}{x_{\text{size}} \cdot y_{\text{size}}}
$$
Since the second and third terms are both < 1 and we are performing integer division:
$$
\text{newZ} = z
$$

- **Extraction of x**:
```cpp
int rem = newPos % (xsize * ysize);
int newX = rem / ysize;
```
Let:
$$
M = xsize \times ysize
$$
The formula becomes:
$$
\text{newPos} = z \times M + (x \times ysize + y)
$$
Using modular arithmetic:
$$
(a + b) \mod M = ((a \mod M) + (b \mod M)) \mod M
$$
Where:
- $a = z \times M \Rightarrow a \mod M = 0$
- $b = x \times ysize + y < M \Rightarrow b \mod M = b$
So:
$$
\text{rem} = newPos \mod M = b = x \cdot ysize + y
$$
Then:
$$
\text{newX} = \frac{rem}{ysize} = x + \frac{y}{ysize}
$$
Again, since $\frac{y}{ysize} < 1$ and integer division is used:
$$
\text{newX} = x
$$

- **Extraction of y**:
```cpp
int newY = rem % ysize;
```
Similar reasoning gives:
$$
\text{newY} = y
$$

### Random Movement
If the condition is not met, the source moves randomly using the function `rand_adj()`.

The `rand_adj()` function searches for an adjacent voxel by exploring all 26 surrounding voxels (excluding the center voxel). For each possible offset along the z, x, and y axes, the helper function `adj_helper()` checks whether the candidate coordinates fall within the grid limits (0 ≤ x < xsize, 0 ≤ y < ysize, 0 ≤ z < zsize). If the coordinates are valid, they are encoded into a single integer using the same formula:
```cpp
index = z * (xsize * ysize) + x * ysize + y
```
and added to a list of candidate positions. Finally, `rand_adj()` randomly selects one of the valid positions, thus ensuring a random movement of the source.

# `cycle_cells()`

The `cycle_cells()` function advances the life cycle of all cells in the 3D grid by one hour.

## Functionality

- A temporary list `toAdd` is created to store new cells generated during the cycle:
```cpp
void Grid::cycle_cells() {
    CellList *toAdd = new CellList();
```
- The function iterates through all voxels in the grid in three dimensions `(z, x, y)`.
- The `current` pointer is initialized to the head of the cell list in the current voxel:
```cpp
    for (int k = 0; k < zsize; k++) {
        for (int i = 0; i < xsize; i++) {
            for (int j = 0; j < ysize; j++) {
                CellNode *current = cells[k][i][j].head;
```
- Each cell executes its cycle with the `cycle()` method, which returns the nutrients consumed and the possible new cell type:
```cpp
                while (current) {
                    cell_cycle_res result = current->cell->cycle(
                        glucose[k][i][j],
                        oxygen[k][i][j],
                        neigh_counts[k][i][j] + cells[k][i][j].size
                    );
```
- Glucose and oxygen values in the voxel are updated by subtracting the consumed amounts:
```cpp
                    glucose[k][i][j] -= result.glucose;
                    oxygen[k][i][j] -= result.oxygen;
```
- If the cycle generates a new healthy cell (`'h'`), a suitable position is determined with `rand_min()`, and the new cell is added to the `toAdd` list. If no space is available, the cell enters a sleep state (`sleep()`):
```cpp
                    if (result.new_cell == 'h') {
                        int downhill = rand_min(i, j, k, 5);
                        if (downhill >= 0) {
                            int newZ = downhill / (xsize * ysize);
                            int rem = downhill % (xsize * ysize);
                            int newX = rem / ysize;
                            int newY = rem % ysize;
                            toAdd->add(new HealthyCell('q'), 'h', newX, newY, newZ);
                        } else {
                            current->cell->sleep();
                        }
                    }
```
- If the generated cell is cancerous (`'c'`), it is placed in an adjacent voxel using `rand_adj()`:
```cpp
                    if (result.new_cell == 'c') {
                        int downhill = rand_adj(i, j, k);
                        if (downhill >= 0) {
                            int newZ = downhill / (xsize * ysize);
                            int rem = downhill % (xsize * ysize);
                            int newX = rem / ysize;
                            int newY = rem % ysize;
                            toAdd->add(new CancerCell('1'), 'c', newX, newY, newZ);
                        }
                    }
```
- The pointer moves to the next cell in the voxel's list:
```cpp
                    current = current->next;
                }
```
- After processing all cells in the voxel:
  - Dead cells are removed with `deleteDeadAndSort()`.
  - Neighbor counts are updated with `change_neigh_counts()`:
```cpp
                int init_count = cells[k][i][j].size;
                cells[k][i][j].deleteDeadAndSort();
                change_neigh_counts(i, j, k, cells[k][i][j].size - init_count);
            }
        }
    }
```
- Finally, all new cells are added to the grid using `addToGrid(toAdd)`:
```cpp
    addToGrid(toAdd);
}
```

## `rand_min()` and `min_helper()`
When a cell divides or needs to move, a new voxel must be found in the 3D grid for placement. The idea is to choose a nearby voxel with the fewest cells, giving the new cell room to grow.

This is done in two steps:

- `rand_min()` scans the 26 neighboring voxels to find those with the fewest cells.
- `min_helper()` checks if a voxel is a valid candidate and updates the candidate list.

**All positions are encoded using the formula `z * xsize * ysize + x * ysize + y`.** `pos[]` will contain the voxel positions with the fewest cells.

### `rand_min()`
Given a single voxel, the function analyzes all its neighbors (excluding itself). For each neighbor, `min_helper()` is executed. At the end, a vector `pos` contains all possible candidates. If `curr_min < max` (i.e., if the cell density is below a threshold), one position from `pos` is randomly selected; otherwise, the function returns `-1`.

### Variables
- `max`: Maximum density threshold to consider for selecting a position.
- `counter`: Counts the number of valid positions found by `min_helper()`, allowing `rand_min()` to select one randomly.
- `pos`: Stores the positions of voxels with the lowest density. Declared in `rand_min()` and passed as a pointer to `min_helper()`.

### `min_helper()`
- Checks if the neighboring voxel considered by `rand_min()` is within grid boundaries.
- If the voxel has lower density than the current minimum `curr_min`, `counter` is reset to 1 as the voxel becomes the new best candidate.
- If the voxel has the same density as `curr_min`, it is added to the `pos[]` array and `counter` is incremented.

# `diffuse()` and `diffuse_helper()`

## `diffuse()`
Simulates the diffusion of oxygen and glucose within the grid by executing two calls to the `diffuse_helper()` function—one for each substance. Afterwards, the matrices `glucose` and `glucose_helper` (and similarly `oxygen` with `oxygen_helper`) are swapped. This is necessary because the helper matrices contain the updated values at the end of the diffusion process. Swapping ensures that the main matrices (`glucose` and `oxygen`) reflect the new data.

## `diffuse_helper()`
Performs the actual simulation of the diffusion of a substance, updating the values of glucose and oxygen in each voxel. Each voxel contains a quantity of the substance, and in each iteration, a fraction of that quantity is transferred to adjacent voxels, simulating the diffusion process.

The method takes the following parameters:
- `diff_factor`: diffusion coefficient that determines the fraction of the substance to distribute to neighboring voxels;
- `src`: matrix containing the initial substance values for each voxel;
- `dest`: matrix where the new values after diffusion will be stored.

### Diffusion Process
The function iterates over every voxel in the grid, and for each voxel:
1. A fraction of the initial quantity is retained locally:
```cpp
dest[k][i][j] = (1.0 - diff_factor) * src[k][i][j];
```
   For example, if `diff_factor` is `0.4`, the voxel retains 60% of its original value.

2. The remainder is equally distributed among the 26 neighboring voxels:
```cpp
(dest += (diff_factor / 26.0) * src[neighbor])
```

3. The final value in each voxel `dest[k][i][j]` is the sum of:
   - The residual from the voxel itself: $(1 - \text{diff_factor}) \cdot \text{src[k][i][j]}$
   - The contributions from all 26 neighbors: $\sum \frac{\text{diff_factor}}{26} \cdot \text{src}_{\text{neighbor}}$

# `deleteDeadAndSort()`

The `deleteDeadAndSort()` method "cleans up" the cell list by removing nodes containing dead cells and reorganizing the list so that only nodes with living cells remain properly linked. The `while(current)` loop analyzes each node and performs operations based on the cell's state.

## Operations in the `while(current)` Loop

1. **Node with dead cell:**  
   - If `current->cell->alive` is false, the cell is dead.  
   - The cell and its node are deleted, and counters (e.g., for 'o' or 'c' cell types) are updated.  
   - The pointer `current` is moved to the next node.

2. **First living node (head not yet set):**  
   - Upon encountering the first node with a living cell, it becomes the **head** and **tail** of the list.  
   - `previous_next_pointer` is set to point to the `next` field of this node to facilitate linking upcoming live nodes.  
   - `found_head = true` is set, and the loop moves to the next node.

3. **Subsequent living nodes:**  
   - Each additional live node is linked to the previous one: `*previous_next_pointer = current`.  
   - The `tail` is updated, and `previous_next_pointer` is redirected to `current->next`.  
   - The loop proceeds to the next node.

At the end of the loop:
- If no live node was found (i.e., the list is empty), both `head` and `tail` are set to `nullptr` and the `size` is verified as 0.
- If at least one live node exists, `tail->next` is set to `nullptr` to properly terminate the list.

## Practical Example
Suppose a list with 4 nodes containing:
- **Node A:** Live cell  
- **Node B:** Dead cell  
- **Node C:** Live cell  
- **Node D:** Dead cell

### Iteration 1:
- **Node A (live):**
  - Becomes the new head and tail.
  - `previous_next_pointer` points to `A->next`.
  - `found_head = true` is set.

### Iteration 2:
- **Node B (dead):**
  - Deleted. `current` moves to **C**.

### Iteration 3:
- **Node C (live):**
  - Linked to A using `A->next = C`.
  - `tail = C`, `previous_next_pointer` updated to `C->next`.
  - `current` moves to **D**.

### Iteration 4:
- **Node D (dead):**
  - Deleted. End of list.

**Final Result:**
The list contains only live nodes, connected as **A → C**. Pointer updates ensure correctness and no memory leaks. The use of `previous_next_pointer` allows efficient in-place restructuring without needing a second pass through the list.

