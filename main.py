import os
import random

from model.controller3D import Controller


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

env_dimension = 50
random.seed(4775)
controller = Controller(1000, env_dimension, env_dimension, env_dimension , 100,
                        paths, "sum", layers)

controller.go(300) # Simulazione di 300 ore




# count = 0
# for i in range(5):

#     # Stampo il numero del ciclo.
#     # Potrebbe essere diverso dal numero di volte in cui il numero di cellule cancerose è 0
#     print(i)

#     # Inizializzazione dell'ambiente cellulare
#     controller = Controller(1000, 50, 50, 100, 1)

#     # Simulazione di 350 ore dell'ambiente cellulare
#     controller.go(350)

#     # Irradiazione e simulazione di 24 ore di ciclo cellulare per 35 volte
#     for j in range(35):
#         controller.irradiate(2)
#         controller.go(24)

#     # Aggiorno il numero di volte in cui il numero di cellule cancerose è 0
#     if CancerCell.cell_count == 0:
#         count += 1

# print(count)