from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import numpy as np
import os


class Graphs:
    def __init__(self, env_dim, divisor, graph_types, paths, layers=1):

        self.graph_types = graph_types

        self.paths = paths

        # Dimensioni dell'ambiente cellulare
        self.xsize = env_dim
        self.ysize = env_dim
        self.zsize = env_dim

        self.divisor = divisor

        self.layers = layers
            
    def create_plot(self, tick_list, check_therapy):

        path = []
        if check_therapy: # Therapy
            path.append(self.paths[6]) # 3D therapy data
            path.append(self.paths[7]) # 2D therapy data
            path.append(self.paths[2]) # 3D therapy graph
            path.append(self.paths[3]) # 2D therapy graph                
            path.append(self.paths[9]) # General data (no distinction between growth and therapy)
            path.append(self.paths[8]) # General garaph (no distinction between growth and therapy)
        else: # Growth
            path.append(self.paths[4]) # 3D growth data
            path.append(self.paths[5]) # 2D growth data
            path.append(self.paths[0]) # 3D growth graph
            path.append(self.paths[1]) # 2D growth graph                
            path.append(self.paths[9]) # General data (no distinction between growth and therapy)
            path.append(self.paths[8]) # General garaph (no distinction between growth and therapy)
        
        if "3d" in self.graph_types: 

            for i, file_data_names in enumerate(os.listdir(path[0])):

                # Leggo il file
                data = np.loadtxt(os.path.join(path[0], file_data_names), comments='#') 
                # data = data.T

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

                #_ = [self.plot3d.bar3d(data[0][i], data[1][i], data[2][i], 1, 1, 1,
                #       color=(data[3][i], data[4][i], data[5][i]), alpha=data[6][i]) for i in range(len(data[0]))]

                _ = [self.plot3d.bar3d(data[i][0], data[i][1], data[i][2], 1, 1, 1,
                       color=(data[i][3], data[i][4], data[i][5]), alpha=data[i][6]) for i in range(len(data))]

                # Salvare il grafico come immagine nella cartella di output
                output_path = os.path.join(path[2], f'cell_proliferation_t{tick_list[i]}.png')
                plt.savefig(output_path)
                plt.close()

        # GRAFICO 2D
        if "2d" in self.graph_types and self.layers is not None:

            # Itero su tutti i file (diversi valori di tick_list)
            for i, file_data_names in enumerate(os.listdir(path[1])):
                # Leggo il file
                data = np.loadtxt(os.path.join(path[1], file_data_names), comments='#')

                for layer in self.layers:

                    # La prima colonna contiene il layer. Siccome ce ne possono sono diversi
                    # seleziono solo quelli corrispondente al layer delll'iterazuione
                    # Esegui lo slicing per mantenere solo le righe in cui il valore della terza colonna è uguale a layer
                    filtered_data = data[data[:, 2] == layer]

                    # Grafico della cell_proliferation:
                    fig, axs = plt.subplots(2, 2, constrained_layout=True)
                    fig.suptitle('Cell proliferation at t = ' + str(tick_list[i])
                    + ' for layer = ' + str(layer))

                    # Set titles
                    titles = ['Type of cells', 'Cell density', 'Glucose density', 'Oxygen density']
                    for ax, title in zip(axs.flat, titles):
                        ax.set(title=title)

                    # # Itero sui pixel della griglia
                    # cell_type_image = []
                    # cell_density_image = []
                    # for i in range(self.xsize):
                    #     row_cell_type = []
                    #     row_cell_density = []
                    #     for j in range(self.ysize):
                    #         row_cell_type.append(patch_type_color(self.grid.cells[layer, i, j]))
                    #         row_cell_density.append(len(self.grid.cells[layer, i, j]))
                    #     cell_type_image.append(row_cell_type)
                    #     cell_density_image.append(row_cell_density)

                    color_matrix, density_matrix, glucose_matrix, oxygen_matrix = self.create_matrix(filtered_data)
                    # density_matrix = self.create_matrix(data)
                    # color_matrix = self.create_matrix(data)

                    # Disegno le immagini
                    axs[0, 0].imshow(color_matrix)
                    axs[0, 1].imshow(density_matrix)
                    axs[1, 0].imshow(glucose_matrix)
                    axs[1, 1].imshow(oxygen_matrix)

                    # Salvo i grafici
                    output_path = os.path.join(path[3], 
                    f'cell_proliferation_t{tick_list[i]} layer{layer}.png')
                    plt.savefig(output_path)
                    plt.close()

        # GRAFICO SUM
        if "sum" in self.graph_types:
            for i, file_data_names in enumerate(os.listdir(path[5])):
            # self.tot_sum = HealthyCell.cell_count + CancerCell.cell_count + OARCell.cell_count
            # self.cancer_sum = CancerCell.cell_count
            # self.healthy_sum = HealthyCell.cell_count
            # self.oar_sum = OARCell.cell_count

            # self.sum_list.append([self.tot_sum, self.cancer_sum, self.healthy_sum, self.oar_sum])
            # if tick == max_tick:
            #     self.sum_plot(self.tick_list)
            
                # Leggo il file
                data = np.loadtxt(os.path.join(path[5], file_data_names), comments='#')
                data = data.T

                fig, ax = plt.subplots()

                # Disegno le somme. plt.plot(x, y)
                plt.plot(tick_list, data[0], "ko-", label="Total Cells", alpha=0.7)
                plt.plot(tick_list, data[1], "ro-", label="Cancer Cells", alpha=0.7)
                plt.plot(tick_list, data[2], "go-", label="Healthy Cells", alpha=0.7)
                plt.plot(tick_list, data[3], "yo-", label="OAR Cells", alpha=0.1)


                plt.yscale('log')

                plt.xlabel('Hours')
                plt.ylabel('Cell sum')
                plt.title('Cell count')
                plt.legend()
                plt.grid()

                # Salvo i grafici
                output_path = os.path.join(path[2], f'cell_sum.png')
                plt.savefig(output_path)
                plt.close()

        # NO GRAFICO
        if None in self.graph_types:  # VEDI
            print("No graphs generated")

    def create_matrix(self, data):

        # Correggiamo la creazione della matrice dei colori per essere tridimensionale
        color_matrix = np.zeros((self.xsize, self.ysize, 3), dtype=float)
        density_matrix = np.empty((self.xsize, self.ysize), dtype=float)
        glucose_matrix = np.zeros((self.xsize, self.ysize), dtype=float)
        oxygen_matrix = np.empty((self.xsize, self.ysize), dtype=float)


    # Riempie la matrice dei colori con i valori RGB per le coordinate corrispondenti
        for row in data:
            x, y = int(row[0]), int(row[1])
            r, g, b = row[3:6]
            color_matrix[x, y] = [r / 255.0, g / 255.0, b / 255.0]  # Normalizza i valori RGB da 0-255 a 0-1
            density_matrix[x,y] =  row[6]
            glucose_matrix[x,y] = row[7]
            oxygen_matrix[x,y] = row[8]

        # return color_matrix , density_matrix
        return color_matrix, density_matrix, glucose_matrix, oxygen_matrix
    