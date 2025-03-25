import matplotlib.pyplot as plt
import numpy as np
import os

def get_intervals(num_hour, divisor):
    intervals = [(i * num_hour) // divisor for i in range(divisor + 1)]
    return intervals

def plot_3d(xsize, ysize, zsize, intervals, path_in, dir_out):
    for i in intervals:
    # for i, file_data_names in enumerate(os.listdir(path_in)):
        for file_data_name in os.listdir(path_in):
            if "t"+ str(i) + "_" in file_data_name: 
                print(file_data_name)
        
                # Leggo il file
                data = np.loadtxt(os.path.join(path_in, file_data_name), comments='#') 
            

        
                fig = plt.figure()
                plot3d = fig.add_subplot(111, projection='3d')

                plot3d.set_title('Cell proliferation at t = ' + str(i))
                plot3d.set_xlabel('X')
                plot3d.set_ylabel('Y')
                plot3d.set_zlabel('Z')
                plot3d.set_xlim([0, xsize])
                plot3d.set_ylim([0, ysize])
                plot3d.set_zlim([0, zsize])


                # Impostare i limiti degli assi
                plot3d.set_xlim([0, xsize])
                plot3d.set_ylim([0, ysize])
                plot3d.set_zlim([0, zsize])

                # Genera i valori dei tick a multipli di 5
                x_ticks = np.arange(0, xsize+1, 5)
                y_ticks = np.arange(0, ysize+1, 5)
                z_ticks = np.arange(0, zsize+1, 5)

                # Imposta i tick sugli assi
                plot3d.set_xticks(x_ticks)
                plot3d.set_yticks(y_ticks)
                plot3d.set_zticks(z_ticks)

                # Formatto i tick degli assi come interi
                plot3d.xaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                plot3d.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                plot3d.zaxis.set_major_formatter(plt.FormatStrFormatter('%d'))


                # STAMPO SIA HEALTHY CHE CANCER CELLS
                #_ = [
                #    plot3d.bar3d(
                #        data[j][0], data[j][1], data[j][2],
                #        1, 1, 1,
                #        color=(0, 1, 0) if data[j][9] == 1 else (1, 0, 0),
                #        alpha=0.05 if data[j][9] == 1 else 1
                #    )
                #    for j in range(len(data)) if data[j][9] in [1, -1]
                #]

                # STAMPO SOLO CANCER
                _ = [
                    plot3d.bar3d(
                        data[j][1], data[j][2], data[j][3],
                        1, 1, 1,
                        color=(1, 0, 0),  # rosso
                        alpha=1
                    )
                    for j in range(len(data)) if data[j][10] == -1
                ]
        
                # Salvare il grafico come immagine nella cartella di output
                output_path = os.path.join(dir_out, f't{i}_gd_3d.png')
                plt.savefig(output_path)
                plt.close()

#def plot_2d(xsize, ysize, zsize, layers, intervals, path_in, dir_out):
#    # Itero su tutti i file (diversi valori di tick_list)
#    for i, file_data_names in enumerate(os.listdir(path_in)):
#
#        # Leggo il file
#        data = np.loadtxt(os.path.join(path_in, file_data_names), comments='#')
#
#        for layer in layers:
#
#            # La prima colonna contiene il layer. Siccome ce ne possono sono diversi
#            # seleziono solo quelli corrispondente al layer delll'iterazuione
#            # Esegui lo slicing per mantenere solo le righe in cui il valore della terza colonna è uguale a layer
#            # filtered_data = data[data[:, 4] == layer]
#
#            # MODIFICA 1
#
#            # Grafico della cell_proliferation:
#            fig, axs = plt.subplots(2, 2, constrained_layout=True)
#            fig.suptitle('Cell proliferation at t = ' + str(intervals[i])
#            + ' for layer = ' + str(layer))
#
#            # Set titles
#            titles = ['Type of cells', 'Cell density', 'Glucose density', 'Oxygen density']
#            for ax, title in zip(axs.flat, titles):
#                ax.set(title=title)
#
#            # MODIFICA 2
#
#            # Salvo i grafici
#            output_path = os.path.join(dir_out, 
#            f't{intervals[i]}_l{layer}_gd_2d.png')
#            plt.savefig(output_path)
#            plt.close()


def plot_2d(xsize, ysize, zsize, layers, intervals, path_in, dir_out):

    # Itero su tutti i file (diversi valori di tick_list)
    for i in intervals:
    # for i, file_data_names in enumerate(os.listdir(path_in)):
        for file_data_name in os.listdir(path_in):
            if "t"+ str(i) + "_" in file_data_name: 
                print(file_data_name)
        

                # Leggo il file
                data = np.loadtxt(os.path.join(path_in, file_data_name), comments='#')

                for layer in layers:
                    # MODIFICA 1: Filtro dei dati per layer
                    # Seleziono solo le righe in cui il valore della quarta colonna (indice 3) è uguale a layer
                    filtered_data = data[data[:, 3] == layer]

                    # Preparazione delle matrici (immagini) per ciascun grafico.
                    # Le dimensioni delle matrici sono date da ysize (altezza) e xsize (larghezza)
                    img_tl = np.zeros((ysize, xsize))  # Top left: valori dalla quinta colonna (indice 4)
                    img_tr = np.zeros((ysize, xsize))  # Top right: valori dall'undicesima colonna (indice 10)
                    img_bl = np.zeros((ysize, xsize))  # Bottom left: valori dalla nona colonna (indice 8)
                    img_br = np.zeros((ysize, xsize))  # Bottom right: valori dalla decima colonna (indice 9)

                    if filtered_data.size > 0:
                        # Ottengo le coordinate dei pixel dalle colonne 2 e 3 (indici 1 e 2)
                        x_coords = filtered_data[:, 1].astype(int)
                        y_coords = filtered_data[:, 2].astype(int)

                        # Assegno i valori alle matrici:
                        # Ogni riga in filtered_data viene usata per posizionare il valore nel pixel corrispondente
                        img_tl[y_coords, x_coords] = filtered_data[:, 4]   # Gradiente per il subplot in alto a sinistra
                        img_tr[y_coords, x_coords] = filtered_data[:, 10]  # Gradiente per il subplot in alto a destra
                        img_bl[y_coords, x_coords] = filtered_data[:, 8]   # Gradiente per il subplot in basso a sinistra
                        img_br[y_coords, x_coords] = filtered_data[:, 9]   # Gradiente per il subplot in basso a destra

                    # MODIFICA 2: Creazione del layout con 4 subplot (2x2) usando imshow per visualizzare le immagini
                    fig, axs = plt.subplots(2, 2, constrained_layout=True)
                    fig.suptitle('Cell proliferation at t = ' + str(i) +
                         ' for layer = ' + str(layer))

                    # In alto a sinistra: immagine basata sui valori della quinta colonna (indice 4)
                    ax = axs[0, 0]
                    im = ax.imshow(img_tl, origin='lower', cmap='viridis')
                    ax.set_title('Cells number')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax, format='%d')

                    # In alto a destra: immagine basata sui valori dell’undicesima colonna (indice 10)
                    ax = axs[0, 1]
                    im = ax.imshow(img_tr, origin='lower', cmap='viridis')
                    ax.set_title('Cells type')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax, ticks=[-1, 0, 1], format='%d')



                    # In basso a sinistra: immagine basata sui valori della nona colonna (indice 8)
                    ax = axs[1, 0]
                    im = ax.imshow(img_bl, origin='lower', cmap='viridis')
                    ax.set_title('Glucose amount')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax)

                    # In basso a destra: immagine basata sui valori della decima colonna (indice 9)
                    ax = axs[1, 1]
                    im = ax.imshow(img_br, origin='lower', cmap='viridis')
                    ax.set_title('Oxygen amount')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax)

                    # Salvo i grafici
                    output_path = os.path.join(dir_out, f't{i}_l{layer}_gd_2d.png')
                    plt.savefig(output_path)
                    plt.close(fig)


            
def create_matrix(xsize, ysize, data):

    # Correggiamo la creazione della matrice dei colori per essere tridimensionale
    color_matrix = np.zeros((xsize, ysize, 3), dtype=float)
    density_matrix = np.empty((xsize, ysize), dtype=float)
    glucose_matrix = np.zeros((xsize, ysize), dtype=float)
    oxygen_matrix = np.empty((xsize, ysize), dtype=float)


# Riempie la matrice dei colori con i valori RGB per le coordinate corrispondenti
    for row in data:
        x, y = int(row[0]), int(row[1])
        r, g, b = row[3:6]
        color_matrix[x, y] = [r / 255.0, g / 255.0, b / 255.0]  # Normalizza i valori RGB da 0-255 a 0-1
        density_matrix[x,y] =  row[3]
        glucose_matrix[x,y] = row[7]
        oxygen_matrix[x,y] = row[8]

    # return color_matrix , density_matrix
    return color_matrix, density_matrix, glucose_matrix, oxygen_matrix

def cells_num(file_name, path_in, path_out):
    # Leggo il file
    data = np.loadtxt(os.path.join(path_in, file_name), comments='#')
    data = data.T

    fig, ax = plt.subplots()
    # Disegno le somme: Total, Healthy, Cancer e OAR Cells
    plt.plot(data[0], data[1] + data[2] + data[3], "k.-", label="Total Cells", alpha=0.7)
    plt.plot(data[0], data[1], "g.-", label="Healthy Cells", alpha=0.7)
    plt.plot(data[0], data[2], "r.-", label="Cancer Cells", alpha=0.7)
    plt.plot(data[0], data[3], "y.-", label="OAR Cells", alpha=0.1)

    plt.yscale('log')
    plt.xlabel('Hours')
    plt.ylabel('Cell sum')
    plt.title('Cell count')
    plt.legend()

    # Imposta la griglia:
    # Vengono disegnate sia le linee verticali che quelle orizzontali, 
    # corrispondenti rispettivamente ai tick degli assi x e y,
    # entrambe come linee continue.
    plt.grid(True, which='major', axis='both', linestyle='-', linewidth=0.5)

    # Salvo il grafico
    out_name = os.path.splitext(file_name)[0]
    output_path = os.path.join(path_out, out_name + '.png')

    plt.savefig(output_path)
    plt.close()





path_results = "/home/ale/Documenti/programming/proj_radio_rein/cpp/results/"
path_in_tab  = path_results + "data/tabs/"
path_in_tab_growth = path_in_tab + "growth/"
path_in_tab_treat = path_in_tab + "treatments/"
path_in_num  = path_results + "data/cell_num/"

dir_out = path_results + "graphs/"
dir_out_sum =  dir_out + "sum/"
dir_out_3d = dir_out + "3d/"
dir_out_3d_growth = dir_out_3d + "growth/"
dir_out_3d_therapy = dir_out_3d + "therapy/"
dir_out_2d = dir_out + "2d/"
dir_out_2d_growth = dir_out_2d + "growth/"
dir_out_2d_therapy = dir_out_2d + "therapy/"


# Creazione delle cartelle se non esistono
os.makedirs(dir_out, exist_ok=True)
os.makedirs(dir_out_sum, exist_ok=True)
os.makedirs(dir_out_3d, exist_ok=True)
os.makedirs(dir_out_3d_growth, exist_ok=True)
os.makedirs(dir_out_3d_therapy, exist_ok=True)
os.makedirs(dir_out_2d, exist_ok=True)
os.makedirs(dir_out_2d_growth, exist_ok=True)
os.makedirs(dir_out_2d_therapy, exist_ok=True)


xsize = 21
ysize = 21
zsize = 21 

layers = [10]

# --- GROWTH ---

num_hour_g = 400
divisor_g = 4
intervals_g = get_intervals(num_hour_g, divisor_g)

# Cells number graph
cells_num("cell_counts_gr.txt", path_in_num, dir_out_sum)

# 2D Graphs
plot_2d(xsize,ysize,zsize,layers, intervals_g, path_in_tab_growth, dir_out_2d_growth)

# 3D Graphs
plot_3d(xsize, ysize, zsize, intervals_g, path_in_tab_growth, dir_out_3d_growth) 

# --- THERAPHY ---

week = 2; # Weeks of tratments
rad_days = 5; # Number of days in which we send radiation
rest_days = 2; # Number of days without radiation
dose = 2.0; # Dose per day

num_hour_t = 24 * (rad_days + rest_days) * week
divisor_t = 2
intervals_t = get_intervals(num_hour_t, divisor_t)

# Cells number graph
cells_num("cell_counts_tr.txt", path_in_num, dir_out_sum)

# 2D Graphs
plot_2d(xsize,ysize,zsize,layers, intervals_g, path_in_tab_growth, dir_out_2d_therapy)

# 3D Graphs
plot_3d(xsize, ysize, zsize, intervals_t, path_in_tab_treat, dir_out_3d_therapy) 