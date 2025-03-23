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
                        data[j][0], data[j][1], data[j][2],
                        1, 1, 1,
                        color=(1, 0, 0),  # rosso
                        alpha=1
                    )
                    for j in range(len(data)) if data[j][9] == -1
                ]
        
                # Salvare il grafico come immagine nella cartella di output
                output_path = os.path.join(dir_out, f't{i}_gd_3d.png')
                plt.savefig(output_path)
                plt.close()

def plot_2d(xsize, ysize, zsize, layers, intervals, path_in, dir_out):
    # Itero su tutti i file (diversi valori di tick_list)
    for i, file_data_names in enumerate(os.listdir(path_in)):

        # Leggo il file
        data = np.loadtxt(os.path.join(path_in, file_data_names), comments='#')

        for layer in layers:

            # La prima colonna contiene il layer. Siccome ce ne possono sono diversi
            # seleziono solo quelli corrispondente al layer delll'iterazuione
            # Esegui lo slicing per mantenere solo le righe in cui il valore della terza colonna è uguale a layer
            filtered_data = data[data[:, 2] == layer]

            # Grafico della cell_proliferation:
            fig, axs = plt.subplots(2, 2, constrained_layout=True)
            fig.suptitle('Cell proliferation at t = ' + str(intervals[i])
            + ' for layer = ' + str(layer))

            # Set titles
            titles = ['Type of cells', 'Cell density', 'Glucose density', 'Oxygen density']
            for ax, title in zip(axs.flat, titles):
                ax.set(title=title)

            # MODIFICA

            # Salvo i grafici
            output_path = os.path.join(dir_out, 
            f't{intervals[i]}_gd_2d.png')
            plt.savefig(output_path)
            plt.close()

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





path_in_tab  = "/home/ale/Documenti/programming/proj_radio_rein/cpp/results/data/tabs/"
path_in_num  = "/home/ale/Documenti/programming/proj_radio_rein/cpp/results/data/cell_num/"
dir_out = "/home/ale/Documenti/programming/proj_radio_rein/cpp/results/graphs/"
dir_out_sum = "/home/ale/Documenti/programming/proj_radio_rein/cpp/results/graphs/sum"
dir_out_3d = "/home/ale/Documenti/programming/proj_radio_rein/cpp/results/graphs/3d"
dir_out_2d = "/home/ale/Documenti/programming/proj_radio_rein/cpp/results/graphs/2d"
xsize = 21
ysize = 21
zsize = 21 


# Creazione delle cartelle se non esistono
os.makedirs(dir_out, exist_ok=True)
os.makedirs(dir_out_sum, exist_ok=True)
os.makedirs(dir_out_3d, exist_ok=True)
os.makedirs(dir_out_2d, exist_ok=True)

# --- GROWTH ---

num_hour_g = 400
divisor_g = 100
intervals_g = get_intervals(num_hour_g, divisor_g)
# print(intervals)
# plot_3d(xsize, ysize, zsize, intervals, path_in_tab, dir_out_3d) 
cells_num("cell_counts_gr.txt", path_in_num, dir_out_sum)


# --- THERAPHY ---

week = 2; # Weeks of tratments
rad_days = 5; # Number of days in which we send radiation
rest_days = 2; # Number of days without radiation
dose = 2.0; # Dose per day

num_hour_t = 24 * (rad_days + rest_days) * week
divisor_t = (rad_days + rest_days) * week
intervals_t = get_intervals(num_hour_g, divisor_g)

cells_num("cell_counts_tr.txt", path_in_num, dir_out_sum)

print(os.getcwd())