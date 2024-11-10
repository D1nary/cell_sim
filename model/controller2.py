import os

from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
from model.grid2 import Grid
import random
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # Per il cubo 3d 

from model.graphs import Graphs


import random



class Controller:

    def __init__(self, env_size, num_hcells, num_ccells, sources, max_tick, real_tumor_grid, 
                 paths, graph_types, divisor, layers):
        
        # Inizializza la griglia 3D con le dimensioni zsize, xsize, ysize
        self.grid = Grid(env_size, sources, graph_types, paths, layers)
        self.tick = 0

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

        # Istanze per i grafici
        # self.graph3d = None
        # self.graph2d = None
        # self.sum_graph = None


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
        tick_list = self.spaced_list(self.divisor, steps)
        print(tick_list)

        for _ in range(steps):

            # Controllo se devo salvare i dati
            if _ in tick_list:
                check_data = True
            else:
                check_data = False

            self.grid.fill_source(130, 4500)
            self.grid.cycle_cells(check_data)
            self.grid.diffuse_glucose(0.2)
            self.grid.diffuse_oxygen(0.2)

            self.tick += 1
            print(self.tick)

            # Calcolo il centro del tumore
            if self.tick % 24 == 0:
                self.grid.compute_center()

            # Creo i grafici
            # if self.tick in self.tick_list or self.tick == 1 and None not in self.tick_list:
            #     self.graphs.create_plot(self.xsize, self.ysize, self.zsize, 
            #                            self.tick, self.max_tick)
                
            # Salva i dati
            if self.tick in tick_list:
                # SALVO I DATI
                self.save_data(self.tick)



    def save_data(self, tick):
        if "3d" in self.graph_types:
            np.savetxt(os.path.join(self.paths[3], f'cell_proliferation_t{tick}.txt'), self.grid.pixel_info, fmt='%f')

        if "2d" in self.graph_types:
            print(self.grid.data_2d)
            np.savetxt(os.path.join(self.paths[4], f'cell_proliferation_t{tick}.txt'), self.grid.data_2d, fmt='%f')

        if "sum" in self.graph_types:
            np.savetxt(os.path.join(self.paths[5], f'cell_proliferation_t{tick}.txt'), self.grid.sum_list, fmt='%f')

            



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
        step = max_tick / (divisor - 1)
        new_list = [round(i * step) for i in range(divisor)]
        return new_list


def patch_type_color(patch):
    if len(patch) == 0:
        return 0, 0, 0 # Se non ci sono cellule lascio il voxel trasparente
    else:
        return patch[0].cell_color()

