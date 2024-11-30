import os
from model.cell_pack.cell import HealthyCell, CancerCell, OARCell, critical_oxygen_level, critical_glucose_level
from model.grid import Grid
import random
import numpy as np
import os


import random



class Controller:

    def __init__(self, env_size, num_hcells, num_ccells, sources, real_tumor_grid, 
                 paths, data_types, layers, tr_info):
        
        # Inizializza la griglia 3D con le dimensioni zsize, xsize, ysize
        self.grid = Grid(env_size, real_tumor_grid, num_hcells, num_ccells, 
                         sources, data_types, paths, layers)
        self.tick = 0
        self.tot_tick = 0

        self.zsize = env_size
        self.xsize = env_size
        self.ysize = env_size

        # Lista dei paths di output
        # indici: 0: path di base, 1: path tretment 3d, 2: path tretment 2d
        self.paths_tot = paths

        # Lista con i tipi dei grafici da stampare
        self.data_types = data_types

        self.tick_list = []

        # Probabilità di inserire una cellula sana in ogni voxel
        # prob = hcells / (zsize * xsize * ysize)

        #self.num_hcells = num_hcells
        #self.num_ccells = num_ccells
#
        #for k in range(self.zsize):
        #    for i in range(self.xsize):
        #        for j in range(self.ysize):
        #            # Aggiungo le cellule sane
        #            if real_tumor_grid[k, i, j] == 1:
        #                for _ in range(self.num_hcells):
        #                    new_cell = HealthyCell(random.randint(0, 4))
        #                    self.grid.cells[k, i, j].append(new_cell)
        #            # Aggiungo le cellule tumorali
        #            elif real_tumor_grid[k, i, j] == -1:
        #                for _ in range(self.num_ccells):
        #                    new_cell = CancerCell(random.randint(0, 3))
        #                    self.grid.cells[k, i, j].append(new_cell)
        
        self.tr_info = tr_info

        self.tot_tick_list = []

        # Conta i vicini nella griglia tridimensionale
        self.grid.count_neighbors()

    # steps = 1 simulates one hour on the grid : Nutrient diffusion and replenishment, cell cycle
    def go(self, steps, tick_list, checkers, tr_index = None):

        # checkers[0]: Therapy checker
        # checkers[1]: End therapy checker

        # tr_index: 

        self.tick = 0

        # check_data[0]: Per i grafici 2d e 3d. check_data[1]: Per il grafico sum
        check_data = True

        for _ in range(steps):

            # Calcolo il centro del tumore
            if self.tick % 24 == 0:
                self.grid.compute_center()

            # Controllo se devo salvare i dati
            if self.tick in tick_list:
                check_data = True
                # Lista per i dati "sum"
                self.tot_tick_list.append(self.tot_tick)
            else:
                check_data = False


            self.grid.fill_source(130, 4500)
            self.grid.cycle_cells(check_data)
            self.grid.diffuse_glucose(0.2)
            self.grid.diffuse_oxygen(0.2)

            # Salva i dati
            if self.tick in tick_list and self.data_types is not None:
                self.save_data(self.tick, checkers, tr_index)
          
            self.tick += 1
            self.tot_tick += 1
            print(self.tick)
                

    def save_data(self, tick, checkers, th_index):

        # checkers[0]: Therapy checker
        # checkers[1]: End therapy checker

        path = []
        if checkers[0]: # Therapy
            path.append(self.paths_tot[0][9]) # General (no distinction between growth and therapy)
                    
            for i in range(self.tr_info[0]): # self.tr_info[0]: numero di trattamenti
                if "3d" in self.data_types:
                    np.savetxt(os.path.join(self.paths_tot[1][0][th_index[0]], f'tr{th_index[0]}_ddp{th_index[1]}t{tick}.txt'), 
                               self.grid.pixel_info, fmt='%f', 
                               header="i (x-axis) \n j (y-axis) \n k (z-axis) \n RGB (R) \n RGB (G) \n RGB (B) \n alpha")
                if "2d" in self.data_types:
                    np.savetxt(os.path.join(self.paths_tot[2][0][th_index[0]], f'tr{th_index[0]}_ddp{th_index[1]}t{tick}.txt'), 
                               self.grid.data_2d, fmt='%f', 
                               header="i (x-axis) \n j (y-axis) \n k (z-axis) \n RGB (R) \n RGB (G) \n RGB (B) \n number per voxel \n glucose \n oxygen")

        else: # Growth
            # path index: 0 --> general, 1 --> 3D, 2 --> 2D
            path.append(self.paths_tot[0][9]) # General (no distinction between growth and therapy)
            path.append(self.paths_tot[0][4]) # 3D Growth
            path.append(self.paths_tot[0][5]) # 2D Growth

            if "3d" in self.data_types:
                np.savetxt(os.path.join(path[1], f't{tick}.txt'), 
                           self.grid.pixel_info, fmt='%f', 
                           header="i (x-axis) \n j (y-axis) \n k (z-axis) \n RGB (R) \n RGB (G) \n RGB (B) \n alpha")
            if "2d" in self.data_types:
                np.savetxt(os.path.join(path[2], f't{tick}.txt'), 
                           self.grid.data_2d, fmt='%f', 
                           header="i (x-axis) \n j (y-axis) \n k (z-axis) \n RGB (R) \n RGB (G) \n RGB (B) \n number per voxel \n glucose \n oxygen")
                
        if "sum" in self.data_types: # PROBLEMA CREA SEMPRE GROWTH
            if checkers[1]: # Therapy and end therapy
                matrix = np.column_stack((self.tot_tick_list, self.grid.sum_list))
                np.savetxt(os.path.join(self.paths_tot[0][9], f'total_cells_therapy.txt'), 
                       matrix, fmt='%f', 
                       header="tick \n total sum \n cancer sum \n healthy sum \n oar sum")
            #else: # Growth
            #    np.savetxt(os.path.join(self.paths_tot[0][9], f'total_cells_growth.txt'), 
            #           self.grid.sum_list, fmt='%f', 
            #           header="total sum \n cancer sum \n healthy sum \n oar sum")

        

            
    def irradiate(self, dose):
        """Irradiate the tumour"""
        self.grid.irradiate(dose)
           
    def observeSegmentation(self):
        """Produce observation of type segmentation"""
        seg = np.vectorize(lambda x:x.pixel_type())
        return seg(self.grid.cells)

    def observeDensity(self):
        """Produce observation of type densities"""
        dens = np.vectorize(lambda x: x.pixel_density())
        return dens(self.grid.cells)
    
    # tick_list mi serve anche nel file graph.py. Creando questo metodo evito di effettuare due volte i calcoli
    def get_spaced_list(self):
        return self.tick_list

    def spaced_list(self, divisor, max_tick):

        if divisor == 2:
            new_list = [0, max_tick-1]

        elif divisor == 1:
            new_list = [max_tick-1]
        else:
            step = max_tick / (divisor - 1)
            new_list = [round(i * step) for i in range(divisor)]
            new_list[-1] = new_list[-1] - 1
        return new_list

    def treatment(self, th_info, divisor):

        # n_ths: Number of treatments
        # n_dth: Number day per treatment
        # n_rd: Number of radiation days
        # ddose: Daily dose

        tick_list = self.spaced_list(divisor, 24)

        # checkers[0]: Therapy checker
        # checkers[1]: End therapy checker
        checkers = [True, False]

        for th in range(th_info[0]):
            for dth in range(th_info[1]):
                # Per numerare i file salvataggio dati durante la terapia
                th_index = [th, dth] # Per numerare i file salvataggio dati durante la terapia
                if dth < th_info[2]:
                    self.irradiate(2)
                if th == th_info[0] - 1:
                    checkers[1] = True
                self.go(24, tick_list, checkers, th_index)
        print(HealthyCell.cell_count, CancerCell.cell_count)

