from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os


class Graphs:
    def __init__(self, grid, type, paths, layers = None):

        self.type = type
        self.grid = grid
        self.tick_list = [10, 100, 200, 300]

        # Lista dei paths di output
        self.paths = paths

        if self.type == "3d":
            # Lista per mantenere traccia delle posizioni dei cubi aggiunti e del colore del voxel
            self.pixel_info = []

        if self.type == "2d":
            self.layers = layers # 2D layer to be printed

        if self.type == "sum":
            self.tot_sum = 0
            self.cancer_sum = 0
            self.healthy_sum = 0
            self.oar_sum = 0

            self.sum_list = []
            self.divisor_list = []
        
        


    def update_plot(self, xsize, ysize, zsize, tick, max_tick = 1):

        # GRAFICO 3D
        if self.type == "3d":

            for k in range(zsize):
                for i in range(xsize):
                    for j in range(ysize):
                        if len(self.grid.cells[k, i, j]) != 0:
                            if isinstance(self.grid.cells[k, i, j][0], HealthyCell):
                                self.pixel_info.append([i, j, k,'green', 0.01]) # Coordinate, colore, alpha
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

        # GRAFICO 2D    
        if self.type == "2d" and self.layers != None:
            if tick == 10 or tick == 100 or tick == 200:

                for layer in self.layers:
                    # Grafico della cell_proliferation:
                    fig, axs = plt.subplots(2,2, constrained_layout=True)
                    fig.suptitle('Cell proliferation at t = '+str(tick))

                    # Set titles
                    titles = ['Type of cells', 'Cell density', 'Glucose density', 'Oxygen density']
                    for ax, title in zip(axs.flat, titles):
                        ax.set(title=title)

                    # Itero sui pixel della griglia
                    cell_type_image = []
                    cell_density_image = []
                    for i in range(xsize):
                        row_cell_type = []
                        row_cell_density = []
                        for j in range(ysize):
                            row_cell_type.append(patch_type_color(self.grid.cells[layer, i, j]))
                            row_cell_density.append(len(self.grid.cells[layer, i, j]))
                        cell_type_image.append(row_cell_type)
                        cell_density_image.append(row_cell_density)

                    # Disegno le immagini
                    axs[0, 0].imshow(cell_type_image)
                    axs[0, 1].imshow(cell_density_image)
                    axs[1, 0].imshow(self.grid.glucose[layer, :, :])
                    axs[1, 1].imshow(self.grid.oxygen[layer, :, :])

                    # Salvo i grafici
                    output_path = os.path.join(self.paths[1], f'cell_proliferation_t{tick}.png')
                    plt.savefig(output_path)
                    plt.close()

        if self.type == "sum":

            
            if tick in self.tick_list:
                # divisor = 4
                # divisor_list = [i for i in range(divisor, max_tick + 1, divisor)]

                for k in range(zsize):
                    for i in range(xsize):
                        for j in range(ysize):
                            if len(self.grid.cells[k, i, j]) != 0:

                                print("Conto numero cellule")
                                self.self.grid.cells[k, i, j]

                                #self.tot_sum += len(self.grid.cells[k, i, j])
                                #for n in range(len(self.grid.cells[k, i, j])):
                                #    if isinstance(self.grid.cells[k, i, j][n], HealthyCell):
                                #        self.healthy_sum += 1
                                #    if isinstance(self.grid.cells[k, i, j][n], CancerCell):
                                #        self.cancer_sum += 1
                                #    if isinstance(self.grid.cells[k, i, j][n], OARCell):
                                #        self.oar_sum += 1

                self.sum_list.append(self.tot_sum)
                self.sum_list.append(self.healthy_sum)
                self.sum_list.append(self.cancer_sum)
                self.sum_list.append(self.oar_sum)

        if self.type == None: # VEDI
            print("No graphs generated")

    def sum_plot(self):

        fig, ax = plt.subplots()

        self.sum_list = np.transpose(self.sum_list)

        # Disegno le somme
        plt.plot(self.divisor_list, self.sum_list[0], "ko-", label = "Total Cells")
        plt.plot(self.divisor_list, self.sum_list[1], "ro-", label = "Cancer Cells")
        plt.plot(self.divisor_list, self.sum_list[2], "go-", label = "Healthy Cells")
        plt.plot(self.divisor_list, self.sum_list[3], "yo-", label = "OAR Cells")

        plt.xlabel('Hours')
        plt.ylabel('Cell sum')
        plt.title('Cell count')
        plt.legend()

        # Salvo i grafici
        output_path = os.path.join(self.paths[1], f'cell_sum.png')
        plt.savefig(output_path)
        plt.close()




def patch_type_color(patch):
        if len(patch) == 0:
            return 0, 0, 0
        else:
            return patch[0].cell_color()
