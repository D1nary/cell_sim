import matplotlib.pyplot as plt
from model.controller3D import Controller
import random
from model.cell_pack.cell import HealthyCell, CancerCell, OARCell



random.seed(4775)
controller = Controller(1000, 50, 50, 50, 100, 1,"3d")
controller.go(350)




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