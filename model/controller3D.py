from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
from model.grid3D import Grid
import random
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # Per il cubo 3d 


import random



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

        if self.graph_type == "2d":
            self.fig, axs = plt.subplots(1,1, constrained_layout=True)
            self.cell_plot = axs
            self.cell_plot.set_title('Types of cells')
        
            if self.hcells > 0:
                self.cell_plot.imshow(
                    [[patch_type_color(self.grid.cells[self.z_slice, i, j]) for j in range(self.grid.ysize)] for i in range(self.grid.xsize)])
                
        else:
            # Creare la figura e l'asse 3D
            fig, self.plot3d = plt.subplots(figsize=(8, 8), subplot_kw={'projection': '3d'})
            self.plot3d.set_title('Cell proliferation')

            vertices = np.array([[0, 0, 0], [self.xsize, 0, 0], [self.xsize, self.ysize, 0], [0, self.ysize, 0],
                                 [0, 0, self.zsize], [self.xsize, 0, self.zsize], [self.xsize, self.ysize, self.zsize], [0, self.ysize, self.zsize]])
            
           # Definire le facce del cubo
            define_faces = lambda v: [[v[j] for j in [0, 1, 5, 4]],
                                     [v[j] for j in [1, 2, 6, 5]],
                                     [v[j] for j in [2, 3, 7, 6]],
                                     [v[j] for j in [3, 0, 4, 7]],
                                     [v[j] for j in [0, 1, 2, 3]],
                                     [v[j] for j in [4, 5, 6, 7]]]
            global faces
            faces = define_faces(vertices)
            
            # Attivare la modalità interattiva
            plt.ion()

            # Lista per mantenere traccia delle posizioni dei cubi aggiunti
            global cubes_coord
            cubes_coord = []

            global cubes_color
            cubes_color = []


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
                self.plot3d.clear()  # Pulisce l'asse per ridisegnare

                # Aggiungere le facce del cubo principale al grafico con colore fisso
                poly3d = Poly3DCollection(faces, alpha=0, linewidths=1, edgecolors='k', facecolors='lightblue')
                self.plot3d.add_collection3d(poly3d)


                # Aggiungere un nuovo cubo in una posizione casuale
                # new_cube_position = (random.uniform(0, 50 - 1), random.uniform(0, 50 - 1), random.uniform(0, 50 - 1))
                # cubes_coord.append(new_cube_position)

                # # Disegnare tutti i cubi aggiunti finora
                # for cube in cubes_coord:
                #     self.plot3d.bar3d(cube[0], cube[1], cube[2], 1, 1, 1, color="red", alpha=1.0, edgecolor='k')

                # # Impostare le etichette degli assi
                # self.plot3d.set_xlabel('X')
                # self.plot3d.set_ylabel('Y')
                # self.plot3d.set_zlabel('Z')

                # # Impostare i limiti degli assi
                # self.plot3d.set_xlim([0, self.xsize])
                # self.plot3d.set_ylim([0, self.ysize])
                # self.plot3d.set_zlim([0, self.zsize])

                # Disegnare e fare una pausa per creare l'effetto animato
                # plt.draw()
                # plt.pause(0.5)
                print(type)
                if self.hcells > 0:
                    for k in range(self.zsize):
                        for i in range(self.xsize):
                            for j in range(self.ysize):
                                # self.cells[k, i, j] = CellList()
                                if len(self.grid.cells[k, i, j]) != 0:
                                    # if isinstance(self.grid.cells[k, i, j][0], HealthyCell):
                                    #     cubes_coord.append([i, j, k,'green'])
                                    if isinstance(self.grid.cells[k, i, j][0], CancerCell):
                                        cubes_coord.append([i, j, k,'red'])

                                # a = len(self.grid.cells[k, i, j])
                                # b = self.grid.cells[k, i, j]
                                # if len(self.cells[k, i, j]) > 0 and isinstance(self.cells[k, i, j][0], HealthyCell):
                                #     cubes_coord = [i, j, k]
                                #     cubes_color = 'green'
                                # if len(self.cells[k, i, j]) > 0 and isinstance(self.cells[k, i, j][0], CancerCell):
                                #     cubes_coord = [i, j, k]
                                #     cubes_color = 'red'
                # for cube in cubes_coord:
                #     self.plot3d.bar3d(cube[0], cube[1], cube[2], 1, 1, 1, color=cube[3], alpha=1.0, edgecolor='k')
                for i in range(len(cubes_coord)):
                    self.plot3d.bar3d(cubes_coord[i][0], cubes_coord[i][1], cubes_coord[i][2], 1, 1, 1, color=cubes_coord[i][3], alpha=1.0, edgecolor='k')

                # Impostare le etichette degli assi
                self.plot3d.set_xlabel('X')
                self.plot3d.set_ylabel('Y')
                self.plot3d.set_zlabel('Z')

                # Impostare i limiti degli assi
                self.plot3d.set_xlim([0, self.xsize])
                self.plot3d.set_ylim([0, self.ysize])
                self.plot3d.set_zlim([0, self.zsize])

                self.plot3d.set_title('Cell proliferation at t = ' + str(self.tick))

                # Disegnare e fare una pausa per creare l'effetto animato
                plt.draw()
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
        return 0, (255, 0, 0) # Rosso
    else:
        return 0.25, voxel[0].cell_color()# Opacità e colore
