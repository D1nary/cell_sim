from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from model.controller2 import Controller


class Graphs:
    def __init__(self, env_dim, divisor, graph_types, paths):

        self.graph_types = graph_types

        # Lista dei paths di output
        # paths[0]: 3d (GRAPHS)
        # paths[1]: 2d (GRAPHS)
        # paths[2]: sum (general folder) (GRAPHS)
        # paths[3]: 3d (DATA)
        # paths[4]: 2d (DATA)
        # paths[5]: sum (general folder) (DATA)
        self.paths = paths

        # Dimensioni dell'ambiente cellulare
        self.xsize = env_dim
        self.ysize = env_dim
        self.zsize = env_dim

        self.divisor = divisor
            
    def create_plot(self, tick_list):
        
        if "3d" in self.graph_types: 
            for i, file_data_names in enumerate(os.listdir(self.paths[3])):
                # Leggo il file
                data = np.loadtxt(os.path.join(self.paths[3], file_data_names), comments='#') 
                data = data.T

                fig = plt.figure()
                self.plot3d = fig.add_subplot(111, projection='3d')

                self.plot3d.set_title('Cell proliferation at t = ' + str(tick_list[i]))

                # Impostare le etichette degli assi
                self.plot3d.set_xlabel('X')
                self.plot3d.set_ylabel('Y')
                self.plot3d.set_zlabel('Z')

                # Impostare i limiti degli assi
                self.plot3d.set_xlim([0, self.xsize])
                self.plot3d.set_ylim([0, self.ysize])
                self.plot3d.set_zlim([0, self.zsize])

                # for i in range(len(data[0])):
                #     self.plot3d.bar3d(data[0], data[1], data[2], 1, 1, 1,
                #                       color=(data[3],data[4],data[5]), alpha=data[6])
                    
                # self.plot3d.bar3d(data[0], data[1], data[2], 1, 1, 1,
                #                   color=(data[3],data[4],data[5]), alpha=data[6])

                _ = [self.plot3d.bar3d(data[0][i], data[1][i], data[2][i], 1, 1, 1,
                       color=(data[3][i], data[4][i], data[5][i]), alpha=data[6][i]) for i in range(len(data[0]))]

                # Salvare il grafico come immagine nella cartella di output
                output_path = os.path.join(self.paths[0], f'cell_proliferation_t{tick_list[i]}.png')
                plt.savefig(output_path)
                plt.close()

        # GRAFICO 2D
        #if "2d" in self.graph_types and self.layers is not None:
        #    for layer in self.layers:
        #        # Grafico della cell_proliferation:
        #        fig, axs = plt.subplots(2, 2, constrained_layout=True)
        #        fig.suptitle('Cell proliferation at t = ' + str(tick))

        #        # Set titles
        #        titles = ['Type of cells', 'Cell density', 'Glucose density', 'Oxygen density']
        #        for ax, title in zip(axs.flat, titles):
        #            ax.set(title=title)

        #        # Itero sui pixel della griglia
        #        cell_type_image = []
        #        cell_density_image = []
        #        for i in range(self.xsize):
        #            row_cell_type = []
        #            row_cell_density = []
        #            for j in range(self.ysize):
        #                row_cell_type.append(patch_type_color(self.grid.cells[layer, i, j]))
        #                row_cell_density.append(len(self.grid.cells[layer, i, j]))
        #            cell_type_image.append(row_cell_type)
        #            cell_density_image.append(row_cell_density)

        #        # Disegno le immagini
        #        axs[0, 0].imshow(cell_type_image)
        #        axs[0, 1].imshow(cell_density_image)
        #        axs[1, 0].imshow(self.grid.glucose[layer, :, :])
        #        axs[1, 1].imshow(self.grid.oxygen[layer, :, :])

        #        # Salvo i grafici
        #        output_path = os.path.join(self.paths[1], f'cell_proliferation_t{tick}.png')
        #        plt.savefig(output_path)
        #        plt.close()

        # GRAFICO SUM
        # if "sum" in self.graph_types:
        #     self.tot_sum = HealthyCell.cell_count + CancerCell.cell_count + OARCell.cell_count
        #     self.cancer_sum = CancerCell.cell_count
        #     self.healthy_sum = HealthyCell.cell_count
        #     self.oar_sum = OARCell.cell_count
        #     print("Ci sono al tick: ", tick)

        #     self.sum_list.append([self.tot_sum, self.cancer_sum, self.healthy_sum, self.oar_sum])
        #     if tick == max_tick:
        #         self.sum_plot(self.tick_list)

        # # NO GRAFICO
        # if None in self.graph_types:  # VEDI
        #     print("No graphs generated")


    def sum_plot(self, tick_list):


        # Ogni sottolista deve contenere un solo tipo di cellule
        self.sum_list = np.transpose(self.sum_list)

        fig, ax = plt.subplots()

        # print("self.tick_list: ", self.tick_list)
        # print("self.sum_list: \n", self.sum_list)

        # Disegno le somme. plt.plot(x, y)
        plt.plot(tick_list, self.sum_list[0], "ko-", label="Total Cells", alpha=0.7)
        plt.plot(tick_list, self.sum_list[1], "ro-", label="Cancer Cells", alpha=0.7)
        plt.plot(tick_list, self.sum_list[2], "go-", label="Healthy Cells", alpha=0.7)
        plt.plot(tick_list, self.sum_list[3], "yo-", label="OAR Cells", alpha=0.1)


        plt.yscale('log')

        plt.xlabel('Hours')
        plt.ylabel('Cell sum')
        plt.title('Cell count')
        plt.legend()
        plt.grid()

        # Salvo i grafici
        output_path = os.path.join(self.paths[1], f'cell_sum.png')
        plt.savefig(output_path)
        plt.close()
    