from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
from model.grid3D import Grid
import random
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # Per il cubo 3d 


class Graphs:
    def __init__(self, xsize, ysize, zsize, grid, type):

        self.type = type
        self.grid = grid

        if self.type == "3d":
            fig, self.plot3d = plt.subplots(figsize=(8, 8), subplot_kw={'projection': '3d'})
            self.plot3d.set_title('Cell proliferation')

            vertices = np.array([[0, 0, 0], [xsize, 0, 0], [xsize, ysize, 0], [0, ysize, 0],
                                     [0, 0, zsize], [xsize, 0, zsize], [xsize, ysize, zsize], [0, ysize, zsize]])
            
            # Definire le facce del cubo
            define_faces = lambda v: [[v[j] for j in [0, 1, 5, 4]],
                                     [v[j] for j in [1, 2, 6, 5]],
                                     [v[j] for j in [2, 3, 7, 6]],
                                     [v[j] for j in [3, 0, 4, 7]],
                                     [v[j] for j in [0, 1, 2, 3]],
                                     [v[j] for j in [4, 5, 6, 7]]]
        
            self.faces = define_faces(vertices)
            # Attivare la modalità interattiva
            plt.ion()

            # Lista per mantenere traccia delle posizioni dei cubi aggiunti e del colore del voxel
            self.cubes_info = []

        # else: # Caso 2d
        #     self.fig, axs = plt.subplots(1,1, constrained_layout=True)
        #     self.cell_plot = axs
        #     self.cell_plot.set_title('Types of cells')
        
        #     if self.hcells > 0:
        #         self.cell_plot.imshow(
        #             [[patch_type_color(self.grid.cells[self.z_slice, i, j]) for j in range(self.grid.ysize)] for i in range(self.grid.xsize)])



    def update_plot(self, xsize, ysize, zsize, tick):
        if self.type == "3d":
            self.plot3d.clear()  # Pulisce l'asse per ridisegnare

            # Aggiungere le facce del cubo principale al grafico con colore fisso
            poly3d = Poly3DCollection(self.faces, alpha=0, linewidths=1, edgecolors='k', facecolors='lightblue')
            self.plot3d.add_collection3d(poly3d)

            for k in range(zsize):
                for i in range(xsize):
                    for j in range(ysize):
                        if len(self.grid[k, i, j]) != 0:
                            # if isinstance(self.grid[k, i, j][0], HealthyCell):
                            #     cubes_info.append([i, j, k,'green'])
                            if isinstance(self.grid[k, i, j][0], CancerCell):
                                self.cubes_info.append([i, j, k,'red'])

            
            for i in range(len(self.cubes_info)):
                self.plot3d.bar3d(self.cubes_info[i][0], self.cubes_info[i][1], self.cubes_info[i][2], 1, 1, 1, color=self.cubes_info[i][3], alpha=1.0, edgecolor='k')

            # Impostare le etichette degli assi
            self.plot3d.set_xlabel('X')
            self.plot3d.set_ylabel('Y')
            self.plot3d.set_zlabel('Z')

            # Impostare i limiti degli assi
            self.plot3d.set_xlim([0, xsize])
            self.plot3d.set_ylim([0, ysize])
            self.plot3d.set_zlim([0, zsize])

            self.plot3d.set_title('Cell proliferation at t = ' + str(tick))

            # Disegnare e fare una pausa per creare l'effetto animato
            plt.draw()
            plt.pause(0.02)