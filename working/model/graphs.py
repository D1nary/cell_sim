from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
import matplotlib.pyplot as plt
import numpy as np
import os
import re

class Graphs:
    def __init__(self, env_dim, th_info, graph_types, paths, layers=1):

        self.graph_types = graph_types

        # self.paths_tot[0]: General paths
        # self.paths_tot[1]: 3d paths
        # self.paths_tot[2]: 2d paths

        # self.paths_tot[1][0]: therapy 3d paths data
        # self.paths_tot[1][1]: therapy 3d paths graph

        # self.paths_tot[2][0]: therapy 2d paths data
        # self.paths_tot[2][1]: therapy 2d paths graph

        self.paths_tot = paths

        # Dimensioni dell'ambiente cellulare
        self.xsize = env_dim
        self.ysize = env_dim
        self.zsize = env_dim

        self.layers = layers

        self.th_info = th_info
            
    def create_plot(self, divisor, max_tick, check_therapy):

        tick_list = self.spaced_list(divisor, max_tick)


        # Creazione del path da iterare:
        if "3d" in self.graph_types: 

            # Creazione del path da iterare:
            if check_therapy: # Therapy
                for i in range(self.th_info[0]): # Numero di trattamenti
                    path = []
                    path.append(self.paths_tot[1][0][i]) # data
                    path.append(self.paths_tot[1][1][i]) # graph

                    # path[0]: data - tr_i, path[0]: graph - tr_i
                    self.graph_3d(tick_list, path)

            else: # Growth
                path = []
                path.append(self.paths_tot[0][4]) # Data
                path.append(self.paths_tot[0][0]) # Graph
                self.graph_3d(tick_list, path)

        # GRAFICO 2D
        if "2d" in self.graph_types and self.layers is not None:

            # Creazione del path da iterare:
            if check_therapy: # Therapy
                for i in range(self.th_info[0]): # Numero di trattamenti
                    path = []
                    path.append(self.paths_tot[2][0][i]) # data
                    path.append(self.paths_tot[2][1][i]) # graph

                    # path[0]: data - tr_i, path[0]: graph - tr_i
                    self.graph_2d(tick_list, path)

            else: # Growth
                path = []
                path.append(self.paths_tot[0][5]) # Data
                path.append(self.paths_tot[0][1]) # Graph
                self.graph_2d(tick_list, path)
        
        # GRAFICO SUM
        if "sum" in self.graph_types:
            path = []
            path.append(self.paths_tot[0][9]) # Data
            path.append(self.paths_tot[0][8]) # Graph
            self.sum_graph(path)

        ## NO GRAFICO
        #if None in self.graph_types:  # VEDI
        #    print("No graphs generated")

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
    
    def graph_3d(self, tick_list, path):
        # path[0]: data path (input)
        # path[1]: graph path (output)

        for file_data_names in os.listdir(path[0]):

            # Leggo il file
            data_path = os.path.join(path[0],file_data_names)
            
            data = np.loadtxt(data_path, comments='#')

            fig = plt.figure()
            self.plot3d = fig.add_subplot(111, projection='3d')

            # Estraggo il numero del tick dal nome del file
            match = re.search(r't(\d+)\.txt$', file_data_names)
            number = match.group(1)

            # Impostare titolo e etichette degli assi
            self.plot3d.set_title('Cell proliferation at t = ' + str(number))
            self.plot3d.set_xlabel('X')
            self.plot3d.set_ylabel('Y')
            self.plot3d.set_zlabel('Z')

            # Impostare i limiti degli assi
            self.plot3d.set_xlim([0, self.xsize])
            self.plot3d.set_ylim([0, self.ysize])
            self.plot3d.set_zlim([0, self.zsize])

            # Creare il grafico 3D
            _ = [self.plot3d.bar3d(data[j][0], data[j][1], data[j][2], 1, 1, 1,
                                   color=(data[j][3], data[j][4], data[j][5]), alpha=data[j][6]) for j in range(len(data))]

            # Salvare il grafico come immagine nella cartella di output
            output_file_name = file_data_names.replace('.txt', '.png')
            output_path = os.path.join(path[1], output_file_name)
            plt.savefig(output_path)
            plt.close()

    def graph_2d(self, tick_list, path):
        # path[0]: data path (input)
        # path[1]: graph path (output)

        # Itero su tutti i file (diversi valori di tick_list)
        for file_data_names in os.listdir(path[0]):
            # Leggo il file
            data_path = os.path.join(path[0],file_data_names)
            data = np.loadtxt(data_path, comments='#')

            for layer in self.layers:
                # La prima colonna contiene il layer. Siccome ce ne possono sono diversi
                # seleziono solo quelli corrispondente al layer delll'iterazuione
                # Esegui lo slicing per mantenere solo le righe in cui il valore della terza colonna è uguale a layer
                filtered_data = data[data[:, 2] == layer]

                # Estraggo il numero del tick dal nome del file
                match = re.search(r't(\d+)\.txt$', file_data_names)
                number = match.group(1)

                # Grafico della cell_proliferation:
                fig, axs = plt.subplots(2, 2, constrained_layout=True)
                fig.suptitle('Cell proliferation at t = ' + str(number)
                             + ' for layer = ' + str(layer))

                # Set titles
                titles = ['Type of cells', 'Cell density', 'Glucose density', 'Oxygen density']
                for ax, title in zip(axs.flat, titles):
                    ax.set(title=title)

                color_matrix, density_matrix, glucose_matrix, oxygen_matrix = self.create_matrix(filtered_data)

                # Disegno le immagini
                axs[0, 0].imshow(color_matrix)
                axs[0, 1].imshow(density_matrix)
                axs[1, 0].imshow(glucose_matrix)
                axs[1, 1].imshow(oxygen_matrix)

                # Salvo i grafici
                output_file_name = file_data_names.replace('.txt', "l"+str(layer)+'.png')
                output_path = os.path.join(path[1], output_file_name)
                plt.savefig(output_path)
                plt.close()

    def sum_graph(self, path):
    
        # path[0]: input
        # path[1]: output
    
        # Leggo il file
        file_data_names = "total_cells_therapy.txt"
        data = np.loadtxt(os.path.join(path[0], file_data_names), comments='#')
        data = data.T
    
        # mi serve l'asse delle x. usa tick total
    
        fig, ax = plt.subplots()
    
        # Disegno le somme. plt.plot(x, y)
        plt.plot(data[0], data[1], "ko-", label="Total Cells", alpha=0.7)
        plt.plot(data[0], data[2], "ro-", label="Cancer Cells", alpha=0.7)
        plt.plot(data[0], data[3], "go-", label="Healthy Cells", alpha=0.7)
    
        # Imposta la scala dell'asse y su logaritmica
        plt.yscale('log')
    
        # Imposta l'etichetta degli assi
        plt.xlabel('Hours')
        plt.ylabel('Cell sum')
        plt.title('Cell count')
    
        # Imposta l'intervallo dei tick sull'asse x a multipli di 24
        x_max = max(data[0])  # Trova il massimo valore dell'asse x
        x_ticks = list(range(0, int(x_max) + 1, 24))  # Genera tick a intervalli di 24
        plt.xticks(x_ticks)
    
        # Abilita la griglia sull'asse x con intersezioni a multipli di 24
        ax.set_xticks(x_ticks, minor=True)
        ax.grid(True, which='both', axis='x', linestyle='--', alpha=0.5)
    
        # Aggiungi la legenda
        plt.legend()
    
        # Salva i grafici
        output_path = os.path.join(path[1], f'cell_sum.png')
        plt.savefig(output_path)
        plt.close()

    def spaced_list(self, divisor, max_tick):

        if divisor == 2:
            new_list = [0, max_tick-1]

        elif divisor == 1:
            new_list = [max_tick-1]
        else:
            step = max_tick / (divisor - 1)
            new_list = [round(i * step) for i in range(divisor)]
            new_list[-1] = new_list[-1] - 1
        return new_list
