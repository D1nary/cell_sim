import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import time
import random

# Creare la figura e l'asse 3D
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': '3d'})

# Definire i vertici del cubo di dimensione 50x50x50
size = 50
vertices = np.array([[0, 0, 0], [size, 0, 0], [size, size, 0], [0, size, 0],
                     [0, 0, size], [size, 0, size], [size, size, size], [0, size, size]])

# Definire le facce del cubo
define_faces = lambda v: [[v[j] for j in [0, 1, 5, 4]],
                         [v[j] for j in [1, 2, 6, 5]],
                         [v[j] for j in [2, 3, 7, 6]],
                         [v[j] for j in [3, 0, 4, 7]],
                         [v[j] for j in [0, 1, 2, 3]],
                         [v[j] for j in [4, 5, 6, 7]]]
faces = define_faces(vertices)

# Funzione per generare un colore casuale
def random_color():
    return [random.random(), random.random(), random.random()]

# Attivare la modalità interattiva
plt.ion()

# Ciclo per aggiornare il colore del cubo al centro nel tempo
for _ in range(100):
    ax.clear()  # Pulisce l'asse per ridisegnare

    # Aggiungere le facce del cubo principale al grafico con colore fisso
    poly3d = Poly3DCollection(faces, alpha=0.5, linewidths=1, edgecolors='k', facecolors='lightblue')
    ax.add_collection3d(poly3d)

    # Definire il cubo al centro di dimensione 1x1x1 come voxel
    center_size = 1
    center_offset = (size - center_size) / 2
    center_color = random_color()
    ax.bar3d(center_offset, center_offset, center_offset, center_size, center_size, center_size, color=center_color, alpha=1.0, edgecolor='k')

    # Impostare le etichette degli assi
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Impostare i limiti degli assi
    ax.set_xlim([0, size])
    ax.set_ylim([0, size])
    ax.set_zlim([0, size])

    # Disegnare e fare una pausa per creare l'effetto animato
    plt.draw()
    plt.pause(0.1)

# Disattivare la modalità interattiva e mostrare il grafico finale
plt.ioff()
plt.show()