import os
import random
import numpy as np

from model.cell_pack.cell import HealthyCell, CancerCell, OARCell
from model.controller2 import Controller

from model.graphs import Graphs

import numpy as np

def tumor_creation(env_dim):
    tumor_grid = np.empty((env_dim, env_dim, env_dim), dtype=object)

    # Coordinate del centro della griglia
    center = tuple(np.array(tumor_grid.shape) // 2)

    # Raggio del cerchio
    tumor_radius = 3

    # Creazione delle coordinate per l'intera griglia
    x, y, z = np.indices((env_dim, env_dim, env_dim))

    # Calcolo della distanza da ogni punto al centro
    distance = np.sqrt((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2)

    # Selezione dei voxel che si trovano all'interno del raggio del tumore e assegnazione del valore 5
    tumor_grid[distance <= tumor_radius] = -1

    # Selezione dei voxel che si trovano all'interno del raggio 7 e assegnazione del valore 1 (mantenendo invariati i voxel con valore 5)
    tumor_grid[(distance <= 7) & (tumor_grid != -1)] = 1

    
    # print(tumor_grid[10, :, :])
    return tumor_grid





# Blocco principale del programma
if __name__ == "__main__":
    # Ottieni la directory corrente di lavoro
    project_folder = os.getcwd()

    # Definisce il path delle cartelle da creare
    paths = [
        os.path.join(project_folder, 'results', 'graphs', '3d'),
        os.path.join(project_folder, 'results', 'graphs', '2d'),
        os.path.join(project_folder, 'results', 'graphs', 'general'),
        os.path.join(project_folder, 'results', 'data', '3d'), 
        os.path.join(project_folder, 'results', 'data', '2d'),
        os.path.join(project_folder, 'results', 'data', 'general')

    ]

    # Crea le cartelle se non esistono già
    for path in paths:
        os.makedirs(path, exist_ok=True)


    cell_num = 10 # Numero di cellule sane e cancerose in ogni pixel del tumore
    env_size = 20 # Dimensioni dell'ambiente

    layers = [int(env_size//2)] # Layer dell'ambiente da analizzare
    num_ore = 150 # Ore di simulazione
    dose = 2


    # graph_types = ["3d", "sum"]
    # graph_types = ["3d", "sum", "2d"]
    # graph_types = [None]
    graph_types = ["2d"]


    random.seed(4775)    
    controller = Controller(env_size, cell_num, cell_num,  100, num_ore, tumor_creation(env_size), 
                            paths, graph_types, layers)
    

    # Numero di grafici per ogni ciclo go. 
    # Se divisor = 1 stampa solo l'inizio del ciclo go()
    divisor = 4
    if None is not graph_types:
        graphs = Graphs(controller.grid, graph_types, num_ore, paths, divisor, layers)
    else:
        print("Nessun grafico da creare")

    
    controller.go(divisor, num_ore) # Simulazione
    print(HealthyCell.cell_count, CancerCell.cell_count)
    controller.irradiate(dose)
    print(HealthyCell.cell_count, CancerCell.cell_count)
    # controller.tick = 0
    # controller.tick_list = controller.spaced_list(4, num_ore)
    # controller.go(10)





    

    




