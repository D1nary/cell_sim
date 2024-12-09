import os
import random
import numpy as np

from model.cell_pack.cell import HealthyCell, CancerCell, OARCell
from model.controller import Controller

from model.graphs import Graphs

def tumor_creation(env_dim):
    tumor_grid = np.empty((env_dim, env_dim, env_dim), dtype=object)

    # Coordinate del centro della griglia
    center = tuple(np.array(tumor_grid.shape) // 2)

    # Raggio del cerchio
    tumor_radius = 5

    # Creazione delle coordinate per l'intera griglia
    x, y, z = np.indices((env_dim, env_dim, env_dim))

    # Calcolo della distanza da ogni punto al centro
    distance = np.sqrt((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2)

    # Selezione dei voxel che si trovano all'interno del raggio del tumore e assegnazione del valore -1
    tumor_grid[distance <= tumor_radius] = -1

    # Selezione dei voxel che si trovano all'interno del raggio 7 e assegnazione del valore 1 (mantenendo invariati i voxel con valore 5)
    tumor_grid[(distance <= 7) & (tumor_grid != -1)] = 1

    
    # print(tumor_grid[10, :, :])
    return tumor_grid

def spaced_list(divisor, max_tick):
    if divisor == 2:
        new_list = [0, max_tick-1]

    elif divisor == 1:
        new_list = [max_tick-1]
    else:
        step = max_tick / (divisor - 1)
        new_list = [round(i * step) for i in range(divisor)]
        new_list[-1] = new_list[-1] - 1
    return new_list


# Blocco principale del programma
if __name__ == "__main__":
    # Ottieni la directory corrente di lavoro
    project_folder = os.getcwd()

    # Definisce il path delle cartelle da creare
    paths = [
        os.path.join(project_folder, 'results', 'graphs', '3d', 'growth'), # 0
        os.path.join(project_folder, 'results', 'graphs', '2d', 'growth'), # 1
        os.path.join(project_folder, 'results', 'graphs', '3d', 'therapy'), # 2
        os.path.join(project_folder, 'results', 'graphs', '2d', 'therapy'), # 3
        os.path.join(project_folder, 'results', 'data', '3d', 'growth'), # 4
        os.path.join(project_folder, 'results', 'data', '2d', 'growth'), # 5
        os.path.join(project_folder, 'results', 'data', '3d', 'therapy'), # 6
        os.path.join(project_folder, 'results', 'data', '2d', 'therapy'), # 7
        os.path.join(project_folder, 'results', 'graphs', 'general'), # 8
        os.path.join(project_folder, 'results', 'data', 'general') # 9
    ]

    # Crea le cartelle se non esistono già
    for path in paths:
        os.makedirs(path, exist_ok=True)


    cell_num = 100 # Numero di cellule sane e cancerose in ogni pixel del tumore
    env_size = 20 # Dimensioni dell'ambiente

    layers = [10, 15] # Layer dell'ambiente da analizzare
    num_ore = 50 # Ore di simulazione
    dose = 2

    data_types = ["2d", "3d", "sum"]
    graph_types = ["2d", "3d", "sum"]


    divisor = 4

    # Treatment parameters
    n_ths = 2 # Number of treatments
    n_dth = 7 # Number day per treatment
    n_rd = 5 # Number of radiation days
    ddose = 2 # Daily dose

    th_info = [n_ths, n_dth, n_rd, ddose]

    # Creazione cartelle per il trattamento
    # path_th_3d[0]: data, path_th_3d[1]: graph
    path_th_3d = [[],[]]
    for th in range(n_ths):
         path_th_3d[0].append(os.path.join(paths[6], f'tr{th + 1}'))
         path_th_3d[1].append(os.path.join(paths[2], f'tr{th + 1}'))
    for i in range(th_info[0]): # Numero di trattamenti
        os.makedirs(path_th_3d[0][i], exist_ok=True)
        os.makedirs(path_th_3d[1][i], exist_ok=True)


    # path_tr_3d[0]: data, path_tr_3d[1]: graph
    path_th_2d = [[],[]]
    for th in range(n_ths):
         path_th_2d[0].append(os.path.join(paths[7], f'tr{th + 1}'))
         path_th_2d[1].append(os.path.join(paths[3], f'tr{th + 1}'))
    for i in range(th_info[0]): # Numero di trattamenti
        os.makedirs(path_th_2d[0][i], exist_ok=True)
        os.makedirs(path_th_2d[1][i], exist_ok=True)

    # Unisco tutti i paths in un array in modo da passare una sola variabile alle funzioni
    # indici: 0: path di base, 1: path tretment 3d, 2: path tretment 2d
    path_tot = [paths, path_th_3d, path_th_2d]
    
    # --------------------------- Growing of the tumor ---------------------------------------

    random.seed(4775)    
    controller = Controller(env_size, cell_num, cell_num,  100, tumor_creation(env_size), 
                            path_tot, data_types, layers, th_info)
    
    tick_list = spaced_list(divisor, num_ore)
    print(tick_list)

    #controller.go(num_ore, tick_list, [False , False]) # Simulazione

    ## --------------------------- Radiating the tumor ---------------------------------------

    controller.treatment(th_info, 1)

    if graph_types != []:
        graphs = Graphs(env_size, th_info, graph_types, path_tot, layers)
        # Disegno i grafici
        #graphs.create_plot(4, 50, False)
        graphs.create_plot(1, 24, True)


