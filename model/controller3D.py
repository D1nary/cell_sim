from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
from model.grid3D import Grid
import random
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # Per il cubo 3d 

from model.graphs import Graphs


import random



class Controller:

    def __init__(self, hcells, zsize, xsize, ysize, sources, graph_type="3d"):
        # Inizializza la griglia 3D con le dimensioni zsize, xsize, ysize
        self.grid = Grid(zsize, xsize, ysize, sources)
        self.tick = 0
        self.hcells = hcells
        self.zsize = zsize
        self.xsize = xsize
        self.ysize = ysize

        # Istanze per i grafici
        self.graph3d = None
        self.graph2d = None


        HealthyCell.cell_count = 0
        CancerCell.cell_count = 0

        # Probabilità di inserire una cellula sana in ogni voxel
        prob = hcells / (zsize * xsize * ysize)

        for k in range(zsize):
            for i in range(xsize):
                for j in range(ysize):
                    if random.random() < prob:
                        new_cell = HealthyCell(random.randint(0, 4))
                        self.grid.cells[k, i, j].append(new_cell)

        # Inizializza una cellula cancerosa al centro della griglia 3D
        new_cell = CancerCell(random.randint(0, 3))
        self.grid.cells[self.zsize // 2, self.xsize // 2, self.ysize // 2].append(new_cell)

        # Conta i vicini nella griglia tridimensionale
        self.grid.count_neighbors()

        # Inizializzo il grafico 3d
        if graph_type == "3d":
            self.graph3d = Graphs(xsize, ysize, zsize, self.grid, graph_type)



    # steps = 1 simulates one hour on the grid : Nutrient diffusion and replenishment, cell cycle
    def go(self, steps=1):
        for _ in range(steps):
            self.grid.fill_source(130, 4500)
            self.grid.cycle_cells()
            self.grid.diffuse_glucose(0.2)
            self.grid.diffuse_oxygen(0.2)
            self.tick += 1

            # Update grafico
            if self.graph3d != None:
                self.graph3d.update_plot(self.xsize, self.ysize, self.zsize, self.tick)


            if self.tick % 24 == 0:
                self.grid.compute_center()

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


def patch_type_color(patch):
    if len(patch) == 0:
        return 0, 0, 0 # Se non ci sono cellule lascio il voxel trasparente
    else:
        return patch[0].cell_color()

