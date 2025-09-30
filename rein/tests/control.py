import time
import pathlib
import random

from rein import cell_sim

# --- Create the directories ---
def create_directories(paths):
    for p in paths:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)


# --- Tumor simulation functions ---
def tumor_growth(ctrl, data_tab_growth):
    """
    Simulates tumor growth over specified hours and saves voxel and cell count data.
    """
    # --- Growth simulation parameters ---
    num_hour = 150
    divisor1 = 4
    divisor2 = 100
    intervals1 = ctrl.get_intervals(num_hour, divisor1)
    intervals2 = ctrl.get_intervals(num_hour, divisor2)

    print("\nPERFORM TUMOR GROWTH SIMULATION")
    file_names = [f"t{t}_gd.txt" for t in intervals1]
    for hour in range(num_hour + 1):
        if hour in intervals1:
            ctrl.temp_data_tab()
        if hour in intervals2:
            ctrl.temp_cell_counts()
        ctrl.go()

    # Save growth results
    ctrl.save_data_tab(str(data_tab_growth), file_names, intervals1, len(intervals1))
    ctrl.save_cell_counts(str(data_tab_growth.parent.parent / "cell_num"), "cell_counts_gr.txt")


def TestTreatment(ctrl, data_tab_tr):
    """
    Applies radiation treatment schedule and saves voxel and cell count data.
    """
    # --- Treatment simulation parameters ---
    week = 2
    rad_days = 5
    rest_days = 2
    dose = 2.0
    num_hour = 24 * (rad_days + rest_days) * week
    divisor2 = 2
    intervals2 = ctrl.get_intervals(num_hour, divisor2)

    print("\nPERFORM RADIATION SIMULATION")
    file_names = [f"t{t}_gd.txt" for t in intervals2]

    # Perform treatment and save results
    ctrl.test_treatment(week, rad_days, rest_days, dose)
    ctrl.save_data_tab(str(data_tab_tr), file_names, intervals2, len(intervals2))
    ctrl.save_cell_counts(str(data_tab_tr.parent.parent / "cell_num"), "cell_counts_tr.txt")


if __name__ == "__main__":
    # Seed random for reproducibility
    cell_sim.seed(int(time.time()))

    # --- Grid variables ---
    xsize = 21
    ysize = 21
    zsize = 21
    sources_num = 20
    cradius = 2.0
    hradius = 4.0
    hcells = 1
    ccells = 1

    # Initialize controller
    ctrl = cell_sim.Controller(xsize, ysize, zsize, sources_num,
                               cradius, hradius, hcells, ccells)

    # Setup directories
    script_dir = pathlib.Path(__file__).resolve().parent
    # This file lives in rein/tests, so the project root sits two levels above.
    project_root = script_dir.parents[1]
    res_path = project_root / "results"
    data_path = res_path / "data"
    data_tab = data_path / "tabs"
    data_tab_growth = data_tab / "growth"
    data_tab_tr = data_tab / "therapy"
    paths = [str(res_path), str(data_path), str(data_tab),
             str(data_tab_growth), str(data_tab_tr),
             str(data_path / "cell_num")]
    create_directories(paths)

    # TUMOR GROWTH
    tumor_growth(ctrl, data_tab_growth)

    # Clear temporary buffers and reset clock
    ctrl.clear_tempDataTab()
    ctrl.clear_tempCellCounts()
    ctrl.tick = 0

    # TRATMENT SIMULATION
    TestTreatment(ctrl, data_tab_tr)
