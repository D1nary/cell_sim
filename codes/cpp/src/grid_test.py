import numpy as np

def tumor_creation(env_dim):
    tumor_grid = np.empty((env_dim, env_dim, env_dim), dtype=object)

    # Coordinate del centro della griglia
    center = tuple(np.array(tumor_grid.shape) // 2)

    # Raggio del cerchio
    tumor_radius = 2
    health_radius = 4

    # Creazione delle coordinate per l'intera griglia
    x, y, z = np.indices((env_dim, env_dim, env_dim))

    # Calcolo della distanza da ogni punto al centro
    distance = np.sqrt((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2)

    # Selezione dei voxel che si trovano all'interno del raggio del tumore e assegnazione del valore 5
    tumor_grid[distance <= tumor_radius] = -1

    # Selezione dei voxel che si trovano all'interno del raggio health_radius e assegnazione del valore 1 (mantenendo invariati i voxel con valore 5)
    tumor_grid[(distance <= health_radius) & (tumor_grid != -1)] = 1
    tumor_grid[(distance <= env_dim) & (tumor_grid != -1) & (tumor_grid != 1)] = 0
    
    for i in range(env_dim):
        print(tumor_grid[i, :, :])
    return tumor_grid

tumor_creation(10)