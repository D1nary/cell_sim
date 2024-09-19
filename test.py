import numpy as np

class Grid3D:
    def __init__(self, xsize, ysize, zsize):
        self.neigh_counts = np.zeros((xsize, ysize, zsize), dtype=int)
        
        # Aggiornamento per i bordi (superfici della griglia)
        for i in range(xsize):
            for j in range(ysize):
                # Strati superiori e inferiori (z = 0 e z = zsize-1)
                self.neigh_counts[i, j, 0] += 9  # Strato superiore
                self.neigh_counts[i, j, zsize - 1] += 9  # Strato inferiore

        for i in range(xsize):
            for k in range(zsize):
                # Bordi anteriori e posteriori (y = 0 e y = ysize-1)
                self.neigh_counts[i, 0, k] += 9  # Bordo anteriore
                self.neigh_counts[i, ysize - 1, k] += 9  # Bordo posteriore

        for j in range(ysize):
            for k in range(zsize):
                # Bordi laterali (x = 0 e x = xsize-1)
                self.neigh_counts[0, j, k] += 9  # Lato sinistro
                self.neigh_counts[xsize - 1, j, k] += 9  # Lato destro

        # Correzione per gli angoli (dove ci sono meno vicini)
        self.neigh_counts[0, 0, 0] -= 3
        self.neigh_counts[0, ysize - 1, 0] -= 3
        self.neigh_counts[xsize - 1, 0, 0] -= 3
        self.neigh_counts[xsize - 1, ysize - 1, 0] -= 3
        self.neigh_counts[0, 0, zsize - 1] -= 3
        self.neigh_counts[0, ysize - 1, zsize - 1] -= 3
        self.neigh_counts[xsize - 1, 0, zsize - 1] -= 3
        self.neigh_counts[xsize - 1, ysize - 1, zsize - 1] -= 3

    def display_layer(self,n):
        print(f"Layer numer {n}")
        print(self.neigh_counts[:, :, n])

# Imposta le dimensioni della matrice 3D
xsize, ysize, zsize = 5, 5, 5

# Crea un'istanza della griglia 3D
grid = Grid3D(xsize, ysize, zsize)

# Visualizza i valori del layer 0
grid.display_layer(1)