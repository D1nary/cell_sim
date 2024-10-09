import matplotlib.pyplot as plt
import matplotlib
from model.grid3D import Grid
from model.cell_pack.cell import HealthyCell, CancerCell, OARCell
import random
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # Per il cubo 3d 


class Controller:

    def __init__(self, hcells, zsize, xsize, ysize, sources, draw_step=0, graph_type="2d"):
        # Inizializza la griglia 3D con le dimensioni zsize, xsize, ysize
        self.grid = Grid(zsize, xsize, ysize, sources)
        self.tick = 0
        self.hcells = hcells
        self.draw_step = draw_step
        self.zsize = zsize
        self.xsize = xsize
        self.ysize = ysize

        self.z_slice = self.zsize//2
        # self.z_slice = 0

        self.graph_type = graph_type

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

        # Se è richiesto il disegno grafico, inizializza i plot
        if draw_step > 0:
            self.cell_density_plot = None
            self.glucose_plot = None
            self.oxygen_plot = None
            self.cell_plot = None
            self.fig = None
            self.plot3d = None
            self.plot_init()


    def plot_init(self):

        matplotlib.use("TkAgg")
        plt.ion()

        if self.graph_type == "2d":
            self.fig, axs = plt.subplots(1,1, constrained_layout=True)
            self.fig.suptitle('Cell proliferation at t = '+str(self.tick))
            self.cell_plot = axs
            self.cell_plot.set_title('Types of cells')
        
            if self.hcells > 0:
                self.cell_plot.imshow(
                    [[patch_type_color(self.grid.cells[self.z_slice, i, j]) for j in range(self.grid.ysize)] for i in range(self.grid.xsize)])
                
        else:
            self.fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': '3d'})
            self.fig.suptitle('Cell proliferation at t = '+str(self.tick))
            self.plot3d = ax

            # Definire i vertici del cubo di dimensione 50x50x50
            # Ordine indici delle sotto liste: [x, y, z]
            vertices = np.array([[0, 0, 0], [self.xsize, 0, 0], [self.xsize, self.ysize, 0], [0, self.ysize, 0],
                                 [0, 0, self.zsize], [self.xsize, 0, self.zsize], [self.xsize, self.ysize, self.zsize], [0, self.ysize, self.zsize]])

            # Definire le facce del cubo
            faces = [[vertices[j] for j in [0, 1, 5, 4]],
                     [vertices[j] for j in [1, 2, 6, 5]],
                     [vertices[j] for j in [2, 3, 7, 6]],
                     [vertices[j] for j in [3, 0, 4, 7]],
                     [vertices[j] for j in [0, 1, 2, 3]],
                     [vertices[j] for j in [4, 5, 6, 7]]]
            
            # Aggiungere le facce al grafico
            self.plot3d.add_collection3d(Poly3DCollection(faces, alpha=0, linewidths=1, edgecolors='r'))

            # Impostare le etichette degli assi
            self.plot3d.set_xlabel('X')
            self.plot3d.set_ylabel('Y')
            self.plot3d.set_zlabel('Z')

            # Impostare i limiti degli assi
            self.plot3d.set_xlim([0, self.xsize])
            self.plot3d.set_ylim([0, self.ysize])
            self.plot3d.set_zlim([0, self.zsize])

            if self.hcells > 0:
                for k in range(self.zsize):
                    for i in range(self.xsize):
                        for j in range(self.ysize):
                            alpha_color = voxel_color(self.grid.cells[k, i, j])
                            color = tuple(val / 255 for val in alpha_color[1])
                            self.plot3d.bar3d(i, j, k, 1, 1, 1,color = color, alpha=alpha_color[0])
            


    # steps = 1 simulates one hour on the grid : Nutrient diffusion and replenishment, cell cycle
    def go(self, steps=1):
        for _ in range(steps):
            self.grid.fill_source(130, 4500)
            self.grid.cycle_cells()
            self.grid.diffuse_glucose(0.2)
            self.grid.diffuse_oxygen(0.2)
            self.tick += 1
            if self.draw_step > 0 and self.tick % self.draw_step == 0:
                self.update_plots()
            if self.tick % 24 == 0:
                self.grid.compute_center()

    def irradiate(self, dose):
        """Irradiate the tumour"""
        self.grid.irradiate(dose)

    def update_plots(self):

        if self.graph_type == "2d":
            self.fig.suptitle('Cell proliferation at t = ' + str(self.tick))
            # self.glucose_plot.imshow(self.grid.glucose)
            # self.oxygen_plot.imshow(self.grid.oxygen)
            if self.hcells > 0:
                self.cell_plot.imshow(
                    [[patch_type_color(self.grid.cells[self.z_slice, i, j]) for j in range(self.grid.ysize)] for i in
                    range(self.grid.xsize)])
            #     self.cell_density_plot.imshow(
            #         [[len(self.grid.cells[i][j]) for j in range(self.grid.ysize)] for i in range(self.grid.xsize)])
            plt.pause(0.02)
        else:
            if self.hcells > 0:
                for k in range(self.zsize):
                    for i in range(self.xsize):
                        for j in range(self.ysize):
                            alpha_color = voxel_color(self.grid.cells[k, i, j])
                            color = tuple(val / 255 for val in alpha_color[1])
                            self.plot3d.bar3d(i, j, k, 1, 1, 1,color = color, alpha=alpha_color[0])

            plt.pause(0.02)
            

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

# Funzione per il colore e la trasparenza nel grafico 3d
def voxel_color(voxel): # Color and trasparency
    if len(voxel) == 0:
        return 0, "red" # Opacità e colore
    else:
        return 0.25, voxel[0].cell_color()
