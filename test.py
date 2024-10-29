import numpy as np

def tumor_creation():
    env_dim = 50
    tumor_grid = np.empty((env_dim, env_dim, env_dim))

    # Coordinate del centro della griglia
    center = tuple(np.array(tumor_grid.shape) // 2)

    # Raggio del cerchio
    tumor_radius = 3

    # Creazione delle coordinate per l'intera griglia
    x, y, z = np.indices((50, 50, 50))


    # Stampa un esempio delle coordinate x, y, e z
    print("Esempio di coordinate x:")
    print(x[22:28, 22:28, 22:28])

    print("Esempio di coordinate y:")
    print(y[22:28, 22:28, 22:28])

    print("Esempio di coordinate z:")
    print(z[22:28, 22:28, 22:28])

tumor_creation()
