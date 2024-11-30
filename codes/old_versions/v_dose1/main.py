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

def spaced_list(divisor, max_tick):
    if divisor == 2:
        new_list = [0, max_tick-1]
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


    cell_num = 5 # Numero di cellule sane e cancerose in ogni pixel del tumore
    env_size = 20 # Dimensioni dell'ambiente

    layers = [10] # Layer dell'ambiente da analizzare
    num_ore = 150 # Ore di simulazione
    dose = 2


    graph_types = ["2d", "3d"]

    divisor = 4

    # --------------------------- Growing of the tumor ---------------------------------------

    random.seed(4775)    
    controller = Controller(env_size, cell_num, cell_num,  100, tumor_creation(env_size), 
                            paths, graph_types, layers)
    
    tick_list = spaced_list(divisor,num_ore)
    print(tick_list)

    controller.go(num_ore, tick_list, False) # Simulazione
    print(HealthyCell.cell_count, CancerCell.cell_count)

    if graph_types is not None:
        graphs = Graphs(env_size, divisor, graph_types, paths, layers)

    # Creo i grafici
    graphs.create_plot(tick_list, False)

    # --------------------------- Radiating the tumor ---------------------------------------

    # sending dose
    divisor = 2
    tick_list = spaced_list(divisor, 24)
    print(tick_list)

    controller.irradiate(2)
    print(HealthyCell.cell_count, CancerCell.cell_count)
    controller.go(24, tick_list, True)

    # Creo i grafici
    graphs.create_plot(tick_list, True)

