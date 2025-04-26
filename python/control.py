import time
import pathlib
import random

# Pylance ti segnala l’errore perché, pur essendo il .so (o .cpython-312-…so) 
# correttamente importabile a runtime, l’analizzatore statico non “vede” la 
# cartella python/ del tuo workspace come parte del PYTHONPATH e non la tratta come package.

# Soluzione:
# Creato un file vuoto cell_sim/python/__init__.py
# Aggiunto a .vscode/settings.json
# {
#   "python.analysis.extraPaths": [
#     "${workspaceFolder}/cell_sim/python"
#   ]
# }

import cell_sim
cell_sim.seed(int(time.time()))
# random.seed(time.time())

# --- Grid variables ---
xsize = 21
ysize = 21
zsize = 21
double_cradius = 2.0
hradius = 4.0
hcells = 1
ccells = 1
sources_num = 20

# --- Radiation variables (not used in this script) ---
week = 2        # Weeks of treatments
rad_days = 5    # Days with radiation
rest_days = 2   # Days without radiation
dose = 2.0      # Dose per day

# --- Hours for tumor growth ---
num_hour = 150

divisor1 = 4
# Initialize controller with an empty intervals list
intervals1 = []
ctrl = cell_sim.Controller(xsize, ysize, zsize, sources_num,
                           double_cradius, hradius,
                           hcells, ccells,
                           intervals1)

# Compute intervals used for voxel data saving
divisor1 = 4
intervals1 = ctrl.get_intervals(num_hour, divisor1)

# Compute intervals used for cell count saving
divisor2 = 100
intervals2 = ctrl.get_intervals(num_hour, divisor2)

# --- Create output directories ---
script_dir = pathlib.Path(__file__).resolve().parent
parent_dir = script_dir.parent
res_path = parent_dir / "results"
data_path = res_path / "data"
data_tab_growth = data_path / "tabs" / "growth"
data_cell_num = data_path / "cell_num"

paths = [str(res_path), str(data_path), str(data_tab_growth), str(data_cell_num)]
ctrl.create_directories(paths)

# --- Prepare filenames ---
file_names_g = [f"t{t}_gd.txt" for t in intervals1]

# --- Tumor growth simulation ---
for hour in range(num_hour + 1):
    if hour in intervals1:
        ctrl.temp_data_tab()
        # print(f"Tick: {hour} | Healthy cells: {ctrl.pixel_density(0,0,0)}")
    if hour in intervals2:
        ctrl.temp_cell_counts()
    ctrl.go()

# --- Save results ---
ctrl.save_data_tab(str(data_tab_growth), file_names_g, intervals1, len(intervals1))
ctrl.save_cell_counts(str(data_cell_num), "cell_counts_gr.txt")
