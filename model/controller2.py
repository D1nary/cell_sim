import os
from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
from model.grid2 import Grid
import random
import numpy as np



import random



class Controller:

    def __init__(self, env_size, num_hcells, num_ccells, sources, max_tick, real_tumor_grid, 
                 paths, graph_types, divisor, layers):
        
        # Inizializza la griglia 3D con le dimensioni zsize, xsize, ysize
        self.grid = Grid(env_size, sources, graph_types, paths, layers)
        self.tick = -1

        self.max_tick = max_tick

        self.num_hcells = num_hcells
        self.num_ccells = num_ccells

        self.zsize = env_size
        self.xsize = env_size
        self.ysize = env_size

        # Per la creazione della lista dei tick in cui salvare i dati
        self.divisor = divisor

        # Lista dei paths di output
        self.paths = paths

        # Lista con i tipi dei grafici da stampare
        self.graph_types = graph_types

        self.tick_list = []


        HealthyCell.cell_count = 0
        CancerCell.cell_count = 0

        # Probabilità di inserire una cellula sana in ogni voxel
        # prob = hcells / (zsize * xsize * ysize)

        for k in range(self.zsize):
            for i in range(self.xsize):
                for j in range(self.ysize):
                    # if random.random() < prob:
                        # new_cell = HealthyCell(random.randint(0, 4))
                        # self.grid.cells[k, i, j].append(new_cell)
                    # Aggiungo le cellule sane
                    if real_tumor_grid[k, i, j] == 1:
                        for _ in range(self.num_ccells):
                            new_cell = HealthyCell(random.randint(0, 4))
                            self.grid.cells[k, i, j].append(new_cell)
                    # Aggiungo le cellule tumorali
                    elif real_tumor_grid[k, i, j] == -1:
                        for _ in range(self.num_ccells):
                            new_cell = CancerCell(random.randint(0, 3))
                            self.grid.cells[k, i, j].append(new_cell)

        # Conta i vicini nella griglia tridimensionale
        self.grid.count_neighbors()

        # Inizializzo i gradici
        # if None is not self.graph_types:
        #     self.graphs = Graphs(self.grid, graph_types, self.paths, max_tick, layers)
        # else:
        #     print("Nessun grafico da creare")
        

    # steps = 1 simulates one hour on the grid : Nutrient diffusion and replenishment, cell cycle
    def go(self, steps=1):

        # Creo la lista di tick in cui voglio salvare i dati
        self.tick_list = self.spaced_list(self.divisor, steps)
        print(self.tick_list)

        # check_data[0]: Per i grafici 2d e 3d. check_data[1]: Per il grafico sum
        check_data = [True,True]

        for _ in range(steps):

            self.tick += 1
            print(self.tick)


            # Calcolo il centro del tumore
            if self.tick % 24 == 0:
                self.grid.compute_center()

            # Controllo se devo salvare i dati
            if self.tick in self.tick_list:
                check_data[0] = True
            else:
                check_data[0] = False

            # Checker per il grafico sum
            if self.tick == self.tick_list[-1] and "sum" in self.graph_types:
                check_data[1] = True
            else:
                check_data[1] = False

            self.grid.fill_source(130, 4500)
            self.grid.cycle_cells(check_data)
            self.grid.diffuse_glucose(0.2)
            self.grid.diffuse_oxygen(0.2)

            # Salva i dati
            if self.tick in self.tick_list and self.graph_types is not None:
                # SALVO I DATI
                self.save_data(self.tick, check_data[1])

    def save_data(self, tick, check_sum):
        if "3d" in self.graph_types:
            np.savetxt(os.path.join(self.paths[3], f'cell_proliferation_t{tick}.txt'), self.grid.pixel_info, fmt='%f',
                       header="i (x-axis) \n j (y-axis) \n k (z-axis) \n RGB (R) \n RGB (G) \n RGB (B) \n alpha")

        if "2d" in self.graph_types:
            np.savetxt(os.path.join(self.paths[4], f'cell_proliferation_t{tick}.txt'), self.grid.data_2d, fmt='%f',
                       header="layer \n RGB (R) \n RGB (G) \n RGB (B) \n number per voxel")

        if "sum" in self.graph_types and check_sum:
            np.savetxt(os.path.join(self.paths[5], f'total_cells.txt'), self.grid.sum_list, fmt='%f',
                       header="total sum \n cancer sum \n healthy sum \n oar sum")

            
    def irradiate(self, dose):
        """Irradiate the tumour"""
        self.grid.irradiate(dose)
           
    def observeSegmentation(self):
        """Produce observation of type segmentation"""
        seg = np.vectorize(lambda x:x.pixel_type())
        return seg(self.grid.cells)

    def observeDensity(self):
        """Produce observation of type densities"""
        dens = np.vectorize(lambda x: x.pixel_density())
        return dens(self.grid.cells)

    def spaced_list(self, divisor, max_tick):
        if divisor == 2:
            new_list = [0, max_tick-1]
        else:
            step = max_tick / (divisor - 1)
            new_list = [round(i * step) for i in range(divisor)]
            new_list[-1] = new_list[-1] - 1
        return new_list
    
    # tick_list mi serve anche nel file graph.py. Creando questo metodo evito di effettuare due volte i calcoli
    def get_spaced_list(self):
        return self.tick_list



def patch_type_color(patch):
    if len(patch) == 0:
        return 0, 0, 0 # Se non ci sono cellule lascio il voxel trasparente
    else:
        return patch[0].cell_color()

