from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
from model.grid3D import Grid
import numpy as np
import os


class Graphs:
    def __init__(self, grid, type, paths, layers = None):

        self.type = type
        self.grid = grid

        # Lista dei paths di output
        self.paths = paths

        if self.type == "3d":
            # Lista per mantenere traccia delle posizioni dei cubi aggiunti e del colore del voxel
            self.pixel_info = []

        if self.type == "2d":
            self.layers = layers # 2D layer to be printed


    def update_plot(self, xsize, ysize, zsize, tick):
        print(tick)

        if self.type == "3d":

            for k in range(zsize):
                for i in range(xsize):
                    for j in range(ysize):
                        if len(self.grid.cells[k, i, j]) != 0:
                            # if isinstance(self.grid.cells[k, i, j][0], HealthyCell):
                            #     self.pixel_info.append([i, j, k,'green', 0.01]) # Coordinate, colore, alpha
                            if isinstance(self.grid.cells[k, i, j][0], CancerCell):
                                self.pixel_info.append([i, j, k,'red', 1.0])

            if tick == 10 or tick == 100:

                fig = plt.figure()
                self.plot3d = fig.add_subplot(111, projection='3d')

                self.plot3d.set_title('Cell proliferation at t = ' + str(tick))
                
                # Impostare le etichette degli assi
                self.plot3d.set_xlabel('X')
                self.plot3d.set_ylabel('Y')
                self.plot3d.set_zlabel('Z')

                # Impostare i limiti degli assi
                self.plot3d.set_xlim([0, xsize])
                self.plot3d.set_ylim([0, ysize])
                self.plot3d.set_zlim([0, zsize])


                for i in range(len(self.pixel_info)):
                    self.plot3d.bar3d(self.pixel_info[i][0], self.pixel_info[i][1], self.pixel_info[i][2], 1, 1, 1,
                                      color=self.pixel_info[i][3], alpha=self.pixel_info[i][4])
                # Salvare il grafico come immagine nella cartella di output
                output_path = os.path.join(self.paths[0], f'cell_proliferation_t{tick}.png')
                plt.savefig(output_path)
                plt.close()


        if self.type == "2d" and self.layers != None:
            if tick == 10 or tick == 100:

                for layer in self.layers:

                    # Grafico della cell_proliferation:
                    fig, axs = plt.subplots(2,2, constrained_layout=True)
                    fig.suptitle('Cell proliferation at t = '+str(tick))
                    # Cells position on the grid
                    self.grid.cells[layer, :, :] = axs[0][0]
                    axs[0][0].set_title('Cells Position')
                    plt.show()
                    plt.close()


            

        if self.type == None:
            print("No graphs generated")