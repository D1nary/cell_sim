import matplotlib.pyplot as plt
import numpy as np
import os

def get_intervals(num_hour, divisor):
    intervals = [(i * num_hour) // divisor for i in range(divisor + 1)]
    return intervals

def plot_3d(xsize, ysize, zsize, intervals, path_in, dir_out):
    for i in intervals:
        for file_data_name in os.listdir(path_in):
            if "t"+ str(i) + "_" in file_data_name: 
                print("Creating graph from ",file_data_name, " file")
        
                # Read file
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

                # Set grid limits  
                plot3d.set_xlim([0, xsize])
                plot3d.set_ylim([0, ysize])
                plot3d.set_zlim([0, zsize])

                # Generate tick values as multiples of 5  
                x_ticks = np.arange(0, xsize+1, 5)
                y_ticks = np.arange(0, ysize+1, 5)
                z_ticks = np.arange(0, zsize+1, 5)

                # Set ticks on the axes  
                plot3d.set_xticks(x_ticks)
                plot3d.set_yticks(y_ticks)
                plot3d.set_zticks(z_ticks)

                # Format axis ticks as integers  
                plot3d.xaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                plot3d.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                plot3d.zaxis.set_major_formatter(plt.FormatStrFormatter('%d'))


                # PLOT ONLY HEALTHY
                #_ = [
                #    plot3d.bar3d(
                #        data[j][0], data[j][1], data[j][2],
                #        1, 1, 1,
                #        color=(0, 1, 0) if data[j][9] == 1 else (1, 0, 0),
                #        alpha=0.05 if data[j][9] == 1 else 1
                #    )
                #    for j in range(len(data)) if data[j][9] in [1, -1]
                #]

                # PLOT ONLY CANCER
                _ = [
                    plot3d.bar3d(
                        data[j][1], data[j][2], data[j][3],
                        1, 1, 1,
                        color=(1, 0, 0),  # rosso
                        alpha=1
                    )
                    for j in range(len(data)) if data[j][10] == -1
                ]
        
                # Save the plot as an image in the output folder  
                output_path = os.path.join(dir_out, f't{i}_gd_3d.png')
                plt.savefig(output_path)
                plt.close()


def plot_2d(xsize, ysize, zsize, layers, intervals, path_in, dir_out):
    # Iterate over all files (different tick_list values)
    for i in intervals:
        for file_data_name in os.listdir(path_in):
            if "t" + str(i) + "_" in file_data_name: 
                print("Creating graph from ",file_data_name, " file")

                # Read the file
                data = np.loadtxt(os.path.join(path_in, file_data_name), comments='#')

                for layer in layers:
                    
                    # Data filtering by layer
                    # Select only rows where the value in the fourth column (index 3) equals layer
                    filtered_data = data[data[:, 3] == layer]

                    # Prepare matrices (images) for each plot
                    # The dimensions of the matrices are defined by ysize (height) and xsize (width)
                    img_tl = np.zeros((ysize, xsize))  # Top left: values from the fifth column (index 4)
                    img_tr = np.zeros((ysize, xsize))  # Top right: values from the eleventh column (index 10)
                    img_bl = np.zeros((ysize, xsize))  # Bottom left: values from the ninth column (index 8)
                    img_br = np.zeros((ysize, xsize))  # Bottom right: values from the tenth column (index 9)

                    if filtered_data.size > 0:
                        # Get pixel coordinates from columns 2 and 3 (indices 1 and 2)
                        x_coords = filtered_data[:, 1].astype(int)
                        y_coords = filtered_data[:, 2].astype(int)

                        # Assign values to the matrices
                        # Each row in filtered_data is used to place the value in the corresponding pixel
                        img_tl[y_coords, x_coords] = filtered_data[:, 4]   # Gradient for top-left subplot
                        img_tr[y_coords, x_coords] = filtered_data[:, 10]  # Gradient for top-right subplot
                        img_bl[y_coords, x_coords] = filtered_data[:, 8]   # Gradient for bottom-left subplot
                        img_br[y_coords, x_coords] = filtered_data[:, 9]   # Gradient for bottom-right subplot

                    # Create a layout with 4 subplots (2x2) using imshow to display the images
                    fig, axs = plt.subplots(2, 2, constrained_layout=True)
                    fig.suptitle('Cell proliferation at t = ' + str(i) +
                         ' for layer = ' + str(layer))

                    # Top-left: image based on values from the fifth column (index 4)
                    ax = axs[0, 0]
                    im = ax.imshow(img_tl, origin='lower', cmap='viridis')
                    ax.set_title('Cells number')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax, format='%d')

                    # Top-right: image based on values from the eleventh column (index 10)
                    ax = axs[0, 1]
                    im = ax.imshow(img_tr, origin='lower', cmap='viridis')
                    ax.set_title('Cells type')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax, ticks=[-1, 0, 1], format='%d')

                    # Bottom-left: image based on values from the ninth column (index 8)
                    ax = axs[1, 0]
                    im = ax.imshow(img_bl, origin='lower', cmap='viridis')
                    ax.set_title('Glucose amount')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax)

                    # Bottom-right: image based on values from the tenth column (index 9)
                    ax = axs[1, 1]
                    im = ax.imshow(img_br, origin='lower', cmap='viridis')
                    ax.set_title('Oxygen amount')
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    fig.colorbar(im, ax=ax)

                    # Save the plots
                    output_path = os.path.join(dir_out, f't{i}_l{layer}_gd_2d.png')
                    plt.savefig(output_path)
                    plt.close(fig)


def cells_num(file_name, path_in, path_out):

    # Read the file
    data = np.loadtxt(os.path.join(path_in, file_name), comments='#')
    data = data.T

    print("Creating graph from ",file_name, " file")

    fig, ax = plt.subplots()
    # Plot the sums: Total, Healthy, Cancer, and OAR Cells
    plt.plot(data[0], data[1] + data[2] + data[3], "k.-", label="Total Cells", alpha=0.7)
    plt.plot(data[0], data[1], "g.-", label="Healthy Cells", alpha=0.7)
    plt.plot(data[0], data[2], "r.-", label="Cancer Cells", alpha=0.7)
    # plt.plot(data[0], data[3], "y.-", label="OAR Cells", alpha=0.1)

    plt.yscale('log')
    plt.xlabel('Hours')
    plt.ylabel('Cell sum')
    plt.title('Cell count')
    plt.legend()

    # Set the grid:
    # Both vertical and horizontal lines are drawn, 
    # corresponding to the x and y axis ticks, respectively,
    # both as solid lines.
    plt.grid(True, which='major', axis='both', linestyle='-', linewidth=0.5)

    # Save the plot
    out_name = os.path.splitext(file_name)[0]
    output_path = os.path.join(path_out, out_name + '.png')

    plt.savefig(output_path)
    plt.close()





current_file_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.dirname(current_file_dir)
parent_dir = os.path.dirname(python_dir)
path_results = os.path.join(parent_dir, "results") + "/"
path_in_tab  = path_results + "data/tabs/"
path_in_tab_growth = path_in_tab + "growth/"
path_in_tab_treat = path_in_tab + "therapy/"
path_in_num  = path_results + "data/cell_num/"

dir_out = path_results + "graphs/"
dir_out_sum =  dir_out + "sum/"
dir_out_3d = dir_out + "3d/"
dir_out_3d_growth = dir_out_3d + "growth/"
dir_out_3d_therapy = dir_out_3d + "therapy/"
dir_out_2d = dir_out + "2d/"
dir_out_2d_growth = dir_out_2d + "growth/"
dir_out_2d_therapy = dir_out_2d + "therapy/"

# Create ditectories if they don't exists
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

num_hour_g = 150
divisor_g = 4
intervals_g = get_intervals(num_hour_g, divisor_g)

# print("GROWTH GRAPHS")
# 
# Cells number graph
print ("Plotting cell counter graphs:")
cells_num("cell_counts_gr.txt", path_in_num, dir_out_sum)
print("\n")

# 2D Graphs
print ("Plotting 2D graphs:")
plot_2d(xsize,ysize,zsize,layers, intervals_g, path_in_tab_growth, dir_out_2d_growth)
print("\n")
# 
# 3D Graphs
print ("Plotting 3D graphs:")
plot_3d(xsize, ysize, zsize, intervals_g, path_in_tab_growth, dir_out_3d_growth) 
print("\n")

# --- THERAPHY ---

week = 2; # Weeks of tratments
rad_days = 5; # Number of days in which we send radiation
rest_days = 2; # Number of days without radiation
dose = 2.0; # Dose per day

num_hour_t = 24 * (rad_days + rest_days) * week
divisor_t = 2
intervals_t = get_intervals(num_hour_t, divisor_t)

print("THERAPHY GRAPHS")

# Cells number graph
print ("Plotting cell counter graphs:")
cells_num("cell_counts_tr.txt", path_in_num, dir_out_sum)
print("\n")

# 2D Graphs
print ("Plotting 2D graphs:")
plot_2d(xsize, ysize, zsize, layers, intervals_t, path_in_tab_treat, dir_out_2d_therapy)
print("\n")
# 
# # 3D Graphs
print ("Plotting 3D graphs:")
plot_3d(xsize, ysize, zsize, intervals_t, path_in_tab_treat, dir_out_3d_therapy)
print("\n")