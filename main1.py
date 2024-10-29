import os
import random
import numpy as np

from model.cell_pack.cell import HealthyCell, CancerCell, OARCell
from model.controller3D import Controller

def tumor_creation():
    env_dim = 50
    tumor_grid = np.empty((env_dim, env_dim, env_dim))

    # Coordinate del centro della griglia
    center = tuple(np.array(tumor_grid.shape) // 2)

    # Raggio del cerchio
    tumor_radius = 3

    # Creazione delle coordinate per l'intera griglia
    x, y, z = np.indices((50, 50, 50))

    # Calcolo della distanza da ogni punto al centro
    distance = np.sqrt((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2)

    # Selezione dei voxel che si trovano all'interno del raggio
    tumor_grid[distance <= tumor_radius] = -1

    # Stampa di un piccolo esempio per verificare il risultato
    print(tumor_grid[x,y,z])




# Blocco principale del programma
if __name__ == "__main__":
    # Ottieni la directory corrente di lavoro
    # project_folder = os.getcwd()

    # Definisce il path delle cartelle da creare
    # paths = [
    #     os.path.join(project_folder, 'results', 'graphs', '3d'),
    #     os.path.join(project_folder, 'results', 'graphs', '2d')
    # ]

    # Crea le cartelle se non esistono già
    # for path in paths:
    #     os.makedirs(path, exist_ok=True)

    # layers = [25]
    # num_ore = 150
    # dose = 2

    # env_dimension = 50
    # random.seed(4775)
    # controller = Controller(1000, env_dimension, env_dimension, env_dimension, 100,
    #                         paths, "sum", num_ore, layers)

    tumor_creation()