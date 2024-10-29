import os
import random
import numpy as np

from model.cell_pack.cell import HealthyCell, CancerCell, OARCell
from model.controller3D import Controller

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
        os.path.join(project_folder, 'results', 'graphs', '2d')
    ]

    # Crea le cartelle se non esistono già
    for path in paths:
        os.makedirs(path, exist_ok=True)

    layers = [25]
    num_ore = 150
    dose = 2

    env_size = 20
    random.seed(4775)
    controller = Controller(1000, env_size, 100,
                            paths, "sum", num_ore, layers)

    tumor_creation()