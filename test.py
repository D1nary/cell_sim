import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Creare la figura e l'asse 3D
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

# Definire i vertici del cubo di dimensione 50x50x50
size = 50
vertices = np.array([[0, 0, 0], [size, 0, 0], [size, size, 0], [0, size, 0],
                     [0, 0, size], [size, 0, size], [size, size, size], [0, size, size]])

# Definire le facce del cubo
faces = [[vertices[j] for j in [0, 1, 5, 4]],
         [vertices[j] for j in [1, 2, 6, 5]],
         [vertices[j] for j in [2, 3, 7, 6]],
         [vertices[j] for j in [3, 0, 4, 7]],
         [vertices[j] for j in [0, 1, 2, 3]],
         [vertices[j] for j in [4, 5, 6, 7]]]

# Aggiungere le facce al grafico
ax.add_collection3d(Poly3DCollection(faces, alpha=.25, linewidths=1, edgecolors='r'))

# Colorare il voxel al centro di rosso
center = size / 2
ax.bar3d(center - 1, center - 1, center - 1, 2, 2, 2, color='red', alpha=1.0)

# Impostare le etichette degli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Impostare i limiti degli assi
ax.set_xlim([0, size])
ax.set_ylim([0, size])
ax.set_zlim([0, size])

# Visualizzare il cubo
plt.show()