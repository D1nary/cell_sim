from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os


class Graphs:
    def __init__(self, grid, graph_types, max_tick, paths, divisor, layers = None):

        self.graph_types = graph_types
        self.grid = grid

        self.tick_list = self.spaced_list(divisor, max_tick)



        # Lista dei paths di output
        self.paths = paths
        
        # # if "3d" in graph_types:
        #     # Lista per mantenere traccia delle posizioni dei cubi aggiunti e del colore del voxel
        #     self.pixel_info = []

        # if "2d" in graph_types:
        #     self.layers = layers # 2D layer to be printed

        # if "sum" in graph_types:
        #     self.tot_sum = 0
        #     self.cancer_sum = 0
        #     self.healthy_sum = 0
        #     self.oar_sum = 0

        #     self.sum_list = []
            
            
    def create_plot(self, xsize, ysize, zsize, tick, max_tick):

        # GRAFICO 3D ELIMINA
        if "3d" in self.graph_types:
            for k in range(zsize):
                for i in range(xsize):
                    for j in range(ysize):
                        if len(self.grid.cells[k, i, j]) != 0:
                            if isinstance(self.grid.cells[k, i, j][0], HealthyCell):
                                self.pixel_info.append([i, j, k, 'green', 0.01])  # Coordinate, colore, alpha
                            if isinstance(self.grid.cells[k, i, j][0], CancerCell):
                                self.pixel_info.append([i, j, k, 'red', 1.0])

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
        if "2d" in self.graph_types and self.layers is not None:
            for layer in self.layers:
                # Grafico della cell_proliferation:
                fig, axs = plt.subplots(2, 2, constrained_layout=True)
                fig.suptitle('Cell proliferation at t = ' + str(tick))

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

        # GRAFICO SUM
        if "sum" in self.graph_types:
            self.tot_sum = HealthyCell.cell_count + CancerCell.cell_count + OARCell.cell_count
            self.cancer_sum = CancerCell.cell_count
            self.healthy_sum = HealthyCell.cell_count
            self.oar_sum = OARCell.cell_count
            print("Ci sono al tick: ", tick)

            self.sum_list.append([self.tot_sum, self.cancer_sum, self.healthy_sum, self.oar_sum])
            if tick == max_tick:
                self.sum_plot(self.tick_list)

        # NO GRAFICO
        if None in self.graph_types:  # VEDI
            print("No graphs generated")


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
    
    # def spaced_list(self, divisor, max_tick):
    #     step = max_tick / (divisor - 1)
    #     new_list = [round(i * step) for i in range(divisor)]
    #     return new_list


    

def patch_type_color(patch):
        if len(patch) == 0:
            return 0, 0, 0
        else:
            return patch[0].cell_color()
