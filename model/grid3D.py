from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import numpy as np
import random
import math
import scipy.special
import matplotlib.pyplot as plt


class CellList:
    """Used to hold lists of cells on each pixel while keeping cancer cells and healthy cells sorted
    """

    def __init__(self):
        self.size = 0
        self.num_c_cells = 0
        self.cancer_cells = []
        self.healthy_cells = []

    def __iter__(self):
        """Needed to iterate on the list object"""
        self._iter_count = -1
        return self

    def __next__(self):
        """Needed to iterate on the list object"""
        self._iter_count += 1
        if self._iter_count < self.num_c_cells:
            return self.cancer_cells[self._iter_count] # Return one element (one cell)
        elif self._iter_count < self.size:
            return self.healthy_cells[self._iter_count - self.num_c_cells]
        else:
            raise StopIteration

    def append(self, cell):
        """Add a cell to the list, keep the API of a Python list"""
        if cell.cell_type() < 0: # cell.cell_type() < 0 is a cancer cell
            self.cancer_cells.append(cell)
            self.num_c_cells += 1
        else:
            self.healthy_cells.append(cell)
        self.size += 1

    def __len__(self):
        """Return the size of the list, keep the API of a Python list"""
        return self.size

    def __getitem__(self, key):
        if key < self.size:
            if key < self.num_c_cells:
                return self.cancer_cells[key]
            else:
                return self.healthy_cells[key - self.num_c_cells]
        else:
            raise IndexError

    def delete_dead(self):
        """Delete dead cells from the list"""
        self.cancer_cells = [cell for cell in self.cancer_cells if cell.alive]
        self.healthy_cells = [cell for cell in self.healthy_cells if cell.alive]
        self.num_c_cells = len(self.cancer_cells)
        self.size = self.num_c_cells + len(self.healthy_cells)

    def pixel_type(self):
        """Used for observation of types on the grid"""
        if self.size == 0:
            return 0
        elif self.num_c_cells:
            return -1
        else:
            return 1

    def pixel_density(self):
        """Used for observation of densities on the grid"""
        if self.num_c_cells: # if num_c_cells !=0
            return - self.num_c_cells
        else:
            return self.size




class Grid:
    """The grid is the base of the simulation.

    It is made out of 3 superimposed 2D layers : one contains the CellLists foreach pixel,
    one contains the glucose amount on each pixel and one contains the oxygen amount on each pixel.
    """

    def __init__(self, xsize, ysize, zsize,  sources, oar=None):
        """Constructor of the Grid.

        Parameters :
        xsize : Number of rows of the grid
        ysize : Number of cclumns of the grid
        sources : Number of nutrient sources on the grid
        oar : Optional description of an OAR zone on the grid
        """
        self.zsize = zsize
        self.xsize = xsize
        self.ysize = ysize

        self.glucose = np.full((zsize, xsize, ysize), 100.0) # Return a new array of given shape and type, filled with 100.0 of glucose.
        self.oxygen = np.full((zsize, xsize, ysize), 1000.0)
        # Helpers are useful because diffusion cannot be done efficiently in place.
        # With a helper array of same shape, we can simply compute the result inside the other and alternate between
        # the arrays.

        self.cells = np.empty((zsize, xsize, ysize), dtype=object)
        for k in range(zsize):
            for i in range(xsize):
                for j in range(ysize):
                    self.cells[k, i, j] = CellList()

        self.num_sources = sources
        # List of random positions in the grid where the sources of nutrients will be
        self.sources = random_sources(zsize, xsize, ysize, sources)

        # Neigbor counts contain, for each pixel on the grid, the number of cells on neigboring pixels. They are useful
        # as HealthyCells only reproduce in case of low density. As these counts seldom change after a few hundred
        # simulated hours, it is more efficient to store them than simply recompute them for each pixel while cycling.
        self.neigh_counts = np.zeros((zsize, xsize, ysize), dtype=int)


        #Pixels at the limits of the grid have fewer neighbours
        for i in range(xsize):
            for j in range(ysize):
                # Strati superiori e inferiori (z = 0 e z = zsize-1)
                self.neigh_counts[0, i, j] += 9  # Strato superiore
                self.neigh_counts[zsize - 1, i, j] += 9  # Strato inferiore
        for k in range(zsize):
            for i in range(xsize):
                # Bordi anteriori e posteriori (y = 0 e y = ysize-1)
                self.neigh_counts[k, i, 0] += 9  # Bordo anteriore
                self.neigh_counts[k, i, ysize - 1] += 9  # Bordo posteriore
        for k in range(zsize):
            for j in range(ysize):
                # Bordi laterali (x = 0 e x = xsize-1)
                self.neigh_counts[k, 0, j] += 9  # Lato sinistro
                self.neigh_counts[k, xsize - 1, j] += 9  # Lato destro

        # Correzione per gli angoli (dove ci sono meno vicini)
        self.neigh_counts[0, 0, 0] -= 3
        self.neigh_counts[0, 0, ysize - 1] -= 3
        self.neigh_counts[0, xsize - 1, 0] -= 3
        self.neigh_counts[0, xsize - 1, ysize - 1] -= 3
        self.neigh_counts[zsize - 1, 0, 0] -= 3
        self.neigh_counts[zsize - 1, 0, ysize - 1] -= 3
        self.neigh_counts[zsize - 1, xsize - 1, 0] -= 3
        self.neigh_counts[zsize - 1, xsize - 1, ysize - 1] -= 3


        self.oar = oar # Dovrebbe contenere le coordinate della oar zone

        self.center_z = self.zsize // 2
        self.center_x = self.xsize // 2
        self.center_y = self.ysize // 2

    def count_neighbors(self):
        """Compute the neighbor counts (the number of cells on neighbouring pixels) for each pixel"""
        for k in range(self.zsize):
            for i in range(self.xsize):
                for j in range(self.ysize):
                    self.neigh_counts[k, i, j] = sum(v for _, _, _, v in self.neighbors(k, i, j))


    def fill_source(self, glucose=0, oxygen=0):
        """Sources of nutrients are refilled in a 3D grid."""
        for i in range(len(self.sources)):
            z, x, y = self.sources[i]  # Estrai le coordinate 3D della sorgente nell'ordine (z, x, y)
            self.glucose[z, x, y] += glucose  # Aggiungi glucosio nella posizione 3D specificata
            self.oxygen[z, x, y] += oxygen  # Aggiungi ossigeno nella posizione 3D specificata

            if random.randint(0, 23) == 0:
                self.sources[i] = self.source_move(z, x, y)  # Passa le coordinate nell'ordine (z, x, y)


    def source_move(self, z, x, y):
        """"Random walk of sources for angiogenesis in a 3D grid"""
        if random.randint(0, 50000) < CancerCell.cell_count:  # Move towards tumour center
            # Movimento lungo l'asse z verso il centro
            if z < self.center_z:
                z += 1
            elif z > self.center_z:
                z -= 1

            # Movimento lungo l'asse x verso il centro
            if x < self.center_x:
                x += 1
            elif x > self.center_x:
                x -= 1

            # Movimento lungo l'asse y verso il centro
            if y < self.center_y:
                y += 1
            elif y > self.center_y:
                y -= 1

            return z, x, y
        else:
            # Movimento casuale tra i vicini tridimensionali
            return self.rand_neigh(z, x, y)


    def diffuse_glucose(self, drate):
        self.glucose = (1 - drate) * self.glucose + (0.125 * drate) * self.neighbors_glucose()

    def diffuse_oxygen(self, drate):
        self.oxygen = (1 - drate) * self.oxygen + (0.125 * drate) * self.neighbors_oxygen()

    def neighbors_glucose(self):
        #Roll array in every direction to diffuse at fixed z
        down = np.roll(self.glucose, shift=1, axis=1)
        up = np.roll(self.glucose, shift=-1, axis=1)
        right = np.roll(self.glucose, shift=1, axis=2)
        left = np.roll(self.glucose, shift=-1, axis=2)
        down_right = np.roll(down, shift=1, axis=2)
        down_left = np.roll(down, shift=-1, axis=2)
        up_right = np.roll(up, shift=1, axis=2)
        up_left = np.roll(up, shift=-1, axis=2)

        # Se il punto considerato si trova in z:
        # Movimenti nel piano z+1 (foward)
        forward = np.roll(self.glucose, 1, axis=0)  # Moving forward along the third axis (z-axis)

        down_left_forward = np.roll(forward, shift=(1, -1), axis=(1, 2))
        left_forward = np.roll(forward, -1, axis=2)
        up_left_forward = np.roll(forward, shift=(-1, -1), axis=(1, 2))

        up_right_forward = np.roll(forward, shift=(-1, 1), axis=(1, 2))
        right_forward = np.roll(forward, 1, axis=2)
        down_right_forward = np.roll(forward, shift=(1, 1), axis=(1, 2))
        
        # Movimenti nel piano z-1 (backward)
        backward = np.roll(self.glucose, -1, axis=0)

        down_left_backward = np.roll(backward, shift=(1, -1), axis=(1, 2))
        left_backward = np.roll(backward, -1, axis=2)
        up_left_backward = np.roll(backward, shift=(-1, -1), axis=(1, 2))

        up_right_backward = np.roll(backward, shift=(-1, 1), axis=(1, 2))
        right_backward = np.roll(backward, 1, axis=2)
        down_right_backward = np.roll(backward, shift=(1, 1), axis=(1, 2))


        # Annullo alcuni estremi delle matrici 3D perchè agli estremi non si ha contributo di glucosio

        # A z fisso
        down[:,0,:] = 0
        up[:, self.xsize-1, :] = 0
        right[:, :, 0] = 0
        left[:, :, self.ysize-1] = 0
        down_right[:,0,:] = 0 # Down
        down_right[:, :, 0] = 0 # Right
        down_left[:,0,:] = 0 # Down 
        down_left[:, :, self.ysize-1] = 0 # Left
        up_right[:, self.xsize-1, :] = 0 #Up
        up_right[:, :, 0] = 0 # Right
        up_left[:, self.xsize-1, :] = 0 # Up
        up_left[:, :, self.ysize-1] = 0 # Left

        # Verso z+1
        forward[0,:,:] = 0
        down_left_forward[:,0,:] = 0 # Down
        down_left_forward[:, :, self.ysize-1] = 0 # Left
        down_left_forward[0,:,:] = 0 # Forward
        left_forward[:, :, self.ysize-1] = 0 # Left
        left_forward[0,:,:] = 0 # Forward
        up_left_forward[:, self.xsize-1, :] = 0 # Up
        up_left_forward[:, :, self.ysize-1] = 0 # Left
        up_left_forward[0,:,:] = 0 # Forward
        up_right_forward[:, self.xsize-1, :] = 0 # Up
        up_right_forward[:, :, 0] = 0 # Right
        up_right_forward[0,:,:] = 0 # Forward
        right_forward[:, :, 0] = 0 # Right
        right_forward[0,:,:] = 0 # Forward
        down_right_forward[:,0,:] = 0 # Down
        down_right_forward[:, :, 0] = 0 # Right
        down_right_forward[0,:,:] = 0 # Forward


        # Verso z-1
        backward[self.zsize-1, :, :] = 0
        down_left_backward[:, 0, :] = 0 # Down
        down_left_backward[:, :, self.ysize-1] = 0 # Left
        down_left_backward[self.zsize-1, :, :] = 0 # Backward
        left_backward[:, :, self.ysize-1] = 0 # Left
        left_backward[self.zsize-1, :, :] = 0 # Backward
        up_left_backward[:, self.xsize-1, :] = 0 # Up
        up_left_backward[:, :, self.ysize-1] = 0 # Left
        up_left_backward[self.zsize-1, :, :] = 0 # Backward
        up_right_backward[:, self.xsize-1, :] = 0 # Up
        up_right_backward[:, :, 0] = 0 # Right
        up_right_backward[self.zsize-1, :, :] = 0 # Backward
        right_backward[:, :, 0] = 0 # Right
        right_backward[self.zsize-1, :, :] = 0 # Backward
        down_right_backward[:, 0, :] = 0 # Down
        down_right_backward[:, :, 0] = 0 # Right
        down_right_backward[self.zsize-1, :,:] = 0 # Backward



        return (down + up + right + left + forward + backward +
            down_left + down_right + up_left + up_right +
            right_forward + left_forward + down_right_forward + down_left_forward + 
            up_right_forward + up_left_forward +
            right_backward + left_backward + down_right_backward + down_left_backward + 
            up_right_backward + up_left_backward)


    def neighbors_oxygen(self):
        #Roll array in every direction to diffuse at fixed z
        down = np.roll(self.oxygen, shift=1, axis=1)
        up = np.roll(self.oxygen, shift=-1, axis=1)
        right = np.roll(self.oxygen, shift=1, axis=2)
        left = np.roll(self.oxygen, shift=-1, axis=2)
        down_right = np.roll(down, shift=1, axis=2)
        down_left = np.roll(down, shift=-1, axis=2)
        up_right = np.roll(up, shift=1, axis=2)
        up_left = np.roll(up, shift=-1, axis=2)

        # Se il punto considerato si trova in z:
        # Movimenti nel piano z+1 (foward)
        forward = np.roll(self.oxygen, 1, axis=0)  # Moving forward along the third axis (z-axis)

        down_left_forward = np.roll(forward, shift=(1, -1), axis=(1, 2))
        left_forward = np.roll(forward, -1, axis=2)
        up_left_forward = np.roll(forward, shift=(-1, -1), axis=(1, 2))

        up_right_forward = np.roll(forward, shift=(-1, 1), axis=(1, 2))
        right_forward = np.roll(forward, 1, axis=2)
        down_right_forward = np.roll(forward, shift=(1, 1), axis=(1, 2))
        
        # Movimenti nel piano z-1 (backward)
        backward = np.roll(self.oxygen, -1, axis=0)

        down_left_backward = np.roll(backward, shift=(1, -1), axis=(1, 2))
        left_backward = np.roll(backward, -1, axis=2)
        up_left_backward = np.roll(backward, shift=(-1, -1), axis=(1, 2))

        up_right_backward = np.roll(backward, shift=(-1, 1), axis=(1, 2))
        right_backward = np.roll(backward, 1, axis=2)
        down_right_backward = np.roll(backward, shift=(1, 1), axis=(1, 2))


        # Annullo alcuni estremi delle matrici 3D perchè agli estremi non si ha contributo di glucosio

        # A z fisso
        down[:,0,:] = 0
        up[:, self.xsize-1, :] = 0
        right[:, :, 0] = 0
        left[:, :, self.ysize-1] = 0
        down_right[:,0,:] = 0 # Down
        down_right[:, :, 0] = 0 # Right
        down_left[:,0,:] = 0 # Down 
        down_left[:, :, self.ysize-1] = 0 # Left
        up_right[:, self.xsize-1, :] = 0 #Up
        up_right[:, :, 0] = 0 # Right
        up_left[:, self.xsize-1, :] = 0 # Up
        up_left[:, :, self.ysize-1] = 0 # Left

        # Verso z+1
        forward[0,:,:] = 0
        down_left_forward[:,0,:] = 0 # Down
        down_left_forward[:, :, self.ysize-1] = 0 # Left
        down_left_forward[0,:,:] = 0 # Forward
        left_forward[:, :, self.ysize-1] = 0 # Left
        left_forward[0,:,:] = 0 # Forward
        up_left_forward[:, self.xsize-1, :] = 0 # Up
        up_left_forward[:, :, self.ysize-1] = 0 # Left
        up_left_forward[0,:,:] = 0 # Forward
        up_right_forward[:, self.xsize-1, :] = 0 # Up
        up_right_forward[:, :, 0] = 0 # Right
        up_right_forward[0,:,:] = 0 # Forward
        right_forward[:, :, 0] = 0 # Right
        right_forward[0,:,:] = 0 # Forward
        down_right_forward[:,0,:] = 0 # Down
        down_right_forward[:, :, 0] = 0 # Right
        down_right_forward[0,:,:] = 0 # Forward


        # Verso z-1
        backward[self.zsize-1, :, :] = 0
        down_left_backward[:, 0, :] = 0 # Down
        down_left_backward[:, :, self.ysize-1] = 0 # Left
        down_left_backward[self.zsize-1, :, :] = 0 # Backward
        left_backward[:, :, self.ysize-1] = 0 # Left
        left_backward[self.zsize-1, :, :] = 0 # Backward
        up_left_backward[:, self.xsize-1, :] = 0 # Up
        up_left_backward[:, :, self.ysize-1] = 0 # Left
        up_left_backward[self.zsize-1, :, :] = 0 # Backward
        up_right_backward[:, self.xsize-1, :] = 0 # Up
        up_right_backward[:, :, 0] = 0 # Right
        up_right_backward[self.zsize-1, :, :] = 0 # Backward
        right_backward[:, :, 0] = 0 # Right
        right_backward[self.zsize-1, :, :] = 0 # Backward
        down_right_backward[:, 0, :] = 0 # Down
        down_right_backward[:, :, 0] = 0 # Right
        down_right_backward[self.zsize-1, :,:] = 0 # Backward



        return (down + up + right + left + forward + backward +
            down_left + down_right + up_left + up_right +
            right_forward + left_forward + down_right_forward + down_left_forward + 
            up_right_forward + up_left_forward +
            right_backward + left_backward + down_right_backward + down_left_backward + 
            up_right_backward + up_left_backward)

    def cycle_cells(self):
        """Feed every cell, handle mitosis in 3D"""
        to_add = []  # Cells to add
        tot_count = 0  # Number of cell cycles
        for k in range(self.zsize):
            for i in range(self.xsize):
                for j in range(self.ysize):  # Itera su ogni voxel nella griglia 3D
                    for cell in self.cells[k, i, j]:
                        # cycle() simula un'ora del ciclo della cellula
                        res = cell.cycle(self.glucose[k, i, j], self.neigh_counts[k, i, j], self.oxygen[k, i, j])
                        tot_count += 1
                        if len(res) > 2:  # Se ci sono più di due argomenti, deve essere creata una nuova cellula
                            if res[2] == 0:  # Mitosi di una cellula sana
                                # downhill: posizione del voxel a bassa densità
                                downhill = self.rand_min(k, i, j, 5)  # Controlla il voxel a bassa densità
                                if downhill is not None:
                                    to_add.append((downhill[0], downhill[1], downhill[2], HealthyCell(4)))
                                else:
                                    cell.stage = 4
                            elif res[2] == 1:  # Mitosi di una cellula cancerosa
                                # downhill: posizione casuale per la cellula cancerosa
                                downhill = self.rand_neigh(k, i, j)
                                if downhill is not None:
                                    to_add.append((downhill[0], downhill[1], downhill[2], CancerCell(0)))
                            elif res[2] == 2:  # Risveglio delle cellule OAR circostanti
                                self.wake_surrounding_oar(k, i, j)
                            elif res[2] == 3:
                                downhill = self.find_hole(k, i, j)
                                if downhill:
                                    to_add.append((downhill[0], downhill[1], downhill[2], OARCell(0, 5)))
                                else:
                                    cell.stage = 4
                                    cell.age = 0
                        # Le variabili locali vengono aggiornate in base al consumo della cellula
                        self.glucose[k, i, j] -= res[0]
                        self.oxygen[k, i, j] -= res[1]
                    count = len(self.cells[k, i, j])
                    self.cells[k, i, j].delete_dead()  # Elimina le cellule morte
                    if len(self.cells[k, i, j]) < count:
                        self.add_neigh_count(k, i, j, len(self.cells[k, i, j]) - count)
        # Aggiungi nuove cellule
        for k, i, j, cell in to_add:
            self.cells[k, i, j].append(cell)
            self.add_neigh_count(k, i, j, 1)
        return tot_count

    def wake_surrounding_oar(self, z, x, y):
        # Lista dei vicini in 3D (26 vicini)
        for (k, i, j) in [
            (z - 1, x - 1, y - 1), (z - 1, x - 1, y), (z - 1, x - 1, y + 1),
            (z - 1, x, y - 1), (z - 1, x, y), (z - 1, x, y + 1),
            (z - 1, x + 1, y - 1), (z - 1, x + 1, y), (z - 1, x + 1, y + 1),
            (z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1),
            (z, x, y - 1), (z, x, y + 1),
            (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1),
            (z + 1, x - 1, y - 1), (z + 1, x - 1, y), (z + 1, x - 1, y + 1),
            (z + 1, x, y - 1), (z + 1, x, y), (z + 1, x, y + 1),
            (z + 1, x + 1, y - 1), (z + 1, x + 1, y), (z + 1, x + 1, y + 1)]:
        
            # Verifica che i vicini siano all'interno dei limiti della griglia
            if (k >= 0 and k < self.zsize and i >= 0 and i < self.xsize and j >= 0 and j < self.ysize 
            and k + i + j <= self.oar[0] + self.oar[1] + self.oar[2]):
            
                # Controlla se c'è una cellula OAR nelle coordinate specificate
                for oarcell in [c for c in self.cells[k, i, j] if isinstance(c, OARCell)]:
                    # Resetta lo stato e l'età delle celle OAR vicine
                    oarcell.stage = 0
                    oarcell.age = 0



    def find_hole(self, z, x, y):
        l = []
        # Lista dei vicini in 3D (26 vicini)
        for (k, i, j) in [
            (z - 1, x - 1, y - 1), (z - 1, x - 1, y), (z - 1, x - 1, y + 1),
            (z - 1, x, y - 1), (z - 1, x, y), (z - 1, x, y + 1),
            (z - 1, x + 1, y - 1), (z - 1, x + 1, y), (z - 1, x + 1, y + 1),
            (z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1),
            (z, x, y - 1), (z, x, y + 1),
            (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1),
            (z + 1, x - 1, y - 1), (z + 1, x - 1, y), (z + 1, x - 1, y + 1),
            (z + 1, x, y - 1), (z + 1, x, y), (z + 1, x, y + 1),
            (z + 1, x + 1, y - 1), (z + 1, x + 1, y), (z + 1, x + 1, y + 1)]:
        
            # Verifica che i vicini siano all'interno dei limiti della griglia
            if (k >= 0 and k < self.zsize and i >= 0 and i < self.xsize and j >= 0 and j < self.ysize 
                and k + i + j <= self.oar[0] + self.oar[1] + self.oar[2]):
            
                # Verifica se ci sono celle OAR nella posizione attuale
                if len([c for c in self.cells[k, i, j] if isinstance(c, OARCell)]) == 0:
                    # Se non ci sono OARCell, aggiungi l'indice e il numero di celle
                    l.append((k, i, j, len(self.cells[k, i, j])))

        # Se non ci sono vicini senza celle OAR, restituisci None
        if len(l) == 0:
            return None
        else:
            # Trova il vicino con il numero minimo di celle
            minimum = 1000
            ind = -1
            for i in range(len(l)):
                if l[i][3] < minimum:
                    minimum = l[i][3]
                    ind = i
            # Restituisce il vicino con il numero di celle minimo
            return l[ind]

    def neighbors(self, z, x, y):
        """Return the positions of every valid pixel in the patch containing z, x, y and its neighbors, and their length"""
        neigh = []
        # Lista delle possibili posizioni dei vicini in 3D (incluso il pixel stesso)
        for (k, i, j) in [
            (z, x, y), (z - 1, x - 1, y - 1), (z - 1, x, y - 1), (z - 1, x + 1, y - 1),
            (z - 1, x, y - 1), (z - 1, x, y), (z - 1, x, y + 1), (z - 1, x + 1, y - 1), 
            (z - 1, x + 1, y), (z - 1, x + 1, y + 1), (z, x - 1, y - 1), (z, x - 1, y),
            (z, x - 1, y + 1), (z, x, y - 1), (z, x, y + 1), (z, x + 1, y - 1), 
            (z, x + 1, y), (z, x + 1, y + 1), (z + 1, x - 1, y - 1), (z + 1, x - 1, y), 
            (z + 1, x - 1, y + 1), (z + 1, x, y - 1), (z + 1, x, y), (z + 1, x, y + 1), 
            (z + 1, x + 1, y - 1), (z + 1, x + 1, y), (z + 1, x + 1, y + 1)]:
    
            # Controlliamo se le coordinate (k, i, j) sono valide all'interno della griglia
            if (k >= 0 and k < self.zsize and i >= 0 and i < self.xsize and j >= 0 and j < self.ysize):
                # Aggiungi le coordinate e la lunghezza delle cellule nel punto (k, i, j)
                neigh.append([k, i, j, len(self.cells[k, i, j])])
    
        return neigh

    def irradiate(self, dose, center=None, rad=-1):
        if center is None:
            self.compute_center()
            z, x, y = self.center_z, self.center_x, self.center_y
        else:
            z, x, y = center
        radius = self.tumor_radius(z, x, y) if rad == -1 else rad
        if radius == 0:
            return  # Terminate the function irradiate()

        multiplicator = get_multiplicator(dose, radius)
        oer_m = 3.0
        k_m = 3.0

        for k in range(self.zsize):
            for i in range(self.xsize):
                for j in range(self.ysize):
                    dist = math.sqrt((z - k) ** 2 + (x - i) ** 2 + (y - j) ** 2)
                    if dist < 3 * radius:
                        omf = (self.oxygen[k, i, j] / 100.0 * oer_m + k_m) / (self.oxygen[k, i, j] / 100.0 + k_m) / oer_m
                        for cell in self.cells[k, i, j]:
                            cell.radiate(scale(radius, dist, multiplicator) * omf)
                        count = len(self.cells[k, i, j])
                        self.cells[k, i, j].delete_dead()
                        if len(self.cells[k, i, j]) < count:
                            self.add_neigh_count(k, i, j, len(self.cells[k, i, j]) - count)
        return radius


    def tumor_radius(self, z, x, y):
        if CancerCell.cell_count > 0:
            max_dist = -1
            for k in range(self.zsize):
                for i in range(self.xsize):
                    for j in range(self.ysize):
                        # Verifica se la cella contiene una cellula cancerosa
                        if len(self.cells[k, i, j]) > 0 and isinstance(self.cells[k, i, j][0], CancerCell):
                            # Calcola la distanza con l'ordine (z, x, y)
                            v = self.dist(k, i, j, z, x, y)
                            if v > max_dist:
                                max_dist = v
            return max_dist if max_dist >= 3 else 3
        else:
            return 0
    
    def dist(self, z, x, y, z_center, x_center, y_center):
        return math.sqrt((z - z_center)**2 + (x - x_center)**2 + (y - y_center)**2)

    # Returns the index of one of the neighboring patches with the lowest density of cells
    def rand_min(self, z, x, y, max):
        v = 1000000
        ind = []
        # Lista dei vicini in 3D (consideriamo i 26 vicini di una cella)
        for (k, i, j) in [
            (z - 1, x - 1, y - 1), (z - 1, x - 1, y), (z - 1, x - 1, y + 1),
            (z - 1, x, y - 1), (z - 1, x, y), (z - 1, x, y + 1),
            (z - 1, x + 1, y - 1), (z - 1, x + 1, y), (z - 1, x + 1, y + 1),
            (z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1),
            (z, x, y - 1), (z, x, y + 1),
            (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1),
            (z + 1, x - 1, y - 1), (z + 1, x - 1, y), (z + 1, x - 1, y + 1),
            (z + 1, x, y - 1), (z + 1, x, y), (z + 1, x, y + 1),
            (z + 1, x + 1, y - 1), (z + 1, x + 1, y), (z + 1, x + 1, y + 1)]:
        
            # Verifica che i vicini siano all'interno dei limiti della griglia
            if (k >= 0 and k < self.zsize and i >= 0 and i < self.xsize and j >= 0 and j < self.ysize):
                if len(self.cells[k, i, j]) < v:
                    v = len(self.cells[k, i, j])
                    ind = [(k, i, j)]
                elif len(self.cells[k, i, j]) == v:
                    ind.append((k, i, j))
                
        # Restituisce un vicino casuale tra quelli con la densità più bassa
        return random.choice(ind) if v < max else None

    def rand_neigh(self, z, x, y):
        ind = []
        # Ciclo su tutti i vicini nelle tre dimensioni (inclusi i livelli sopra e sotto)
        for (k, i, j) in [
            (z - 1, x - 1, y - 1), (z - 1, x - 1, y), (z - 1, x - 1, y + 1),
            (z - 1, x, y - 1), (z - 1, x, y), (z - 1, x, y + 1),
            (z - 1, x + 1, y - 1), (z - 1, x + 1, y), (z - 1, x + 1, y + 1),
            (z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1),
            (z, x, y - 1), (z, x, y + 1),
            (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1),
            (z + 1, x - 1, y - 1), (z + 1, x - 1, y), (z + 1, x - 1, y + 1),
            (z + 1, x, y - 1), (z + 1, x, y), (z + 1, x, y + 1),
            (z + 1, x + 1, y - 1), (z + 1, x + 1, y), (z + 1, x + 1, y + 1)
        ]:
            # Controlla se il vicino è dentro i limiti della griglia
            if (k >= 0 and k < self.zsize and i >= 0 and i < self.xsize and j >= 0 and j < self.ysize):
                ind.append((k, i, j))

        # Restituisce una posizione casuale tra i vicini validi
        return random.choice(ind)



    def add_neigh_count(self, z, x, y, v):
        # Lista dei vicini in 3D (26 vicini)
        for (k, i, j) in [
            (z - 1, x - 1, y - 1), (z - 1, x - 1, y), (z - 1, x - 1, y + 1),
            (z - 1, x, y - 1), (z - 1, x, y), (z - 1, x, y + 1),
            (z - 1, x + 1, y - 1), (z - 1, x + 1, y), (z - 1, x + 1, y + 1),
            (z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1),
            (z, x, y - 1), (z, x, y + 1),
            (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1),
            (z + 1, x - 1, y - 1), (z + 1, x - 1, y), (z + 1, x - 1, y + 1),
            (z + 1, x, y - 1), (z + 1, x, y), (z + 1, x, y + 1),
            (z + 1, x + 1, y - 1), (z + 1, x + 1, y), (z + 1, x + 1, y + 1)]:
        
            # Verifica che i vicini siano all'interno dei limiti della griglia
            if (k >= 0 and k < self.zsize and i >= 0 and i < self.xsize and j >= 0 and j < self.ysize):
                # Aggiungi il valore v al contatore dei vicini
                self.neigh_counts[k, i, j] += v


    def compute_center(self):
        if CancerCell.cell_count == 0:
            return -1, -1, -1
        sum_x = 0
        sum_y = 0
        sum_z = 0
        count = 0
        for k in range(self.zsize):
            for i in range(self.xsize):
                for j in range(self.ysize):
                    ccell_count = self.cells[k, i, j].num_c_cells
                    sum_x += i * ccell_count
                    sum_y += j * ccell_count
                    sum_z += k * ccell_count
                    count += ccell_count
        self.center_x = sum_x / count
        self.center_y = sum_y / count
        self.center_z = sum_z / count


def conv(rad, x):
    denom = 3.8 # //sqrt(2) * 2.7
    return math.erf((rad - x)/denom) - math.erf((-rad - x) / denom)

def get_multiplicator(dose, radius):
    return dose / conv(14, 0)

def scale(radius, x, multiplicator):
    return multiplicator * conv(14, x * 10 / radius)


# Creates a list of random positions in the grid where the sources of nutrients (blood vessels) will be
def random_sources(zsize, xsize, ysize, number):
    src = []
    for _ in range(number):
        z = random.randint(0, zsize - 1)
        x = random.randint(0, xsize - 1)
        y = random.randint(0, ysize - 1)
        if (z, x, y) not in src:
            src.append((z, x, y))
    return src