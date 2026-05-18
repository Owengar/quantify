import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time

import numpy as np
import xarray as xr

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MEAS_DIRS = [
    os.path.join(os.environ.get("USERPROFILE", ""), "Box", "Quantum Device Lab", "Quantify", "Measurements"),
    os.path.join(os.environ.get("USERPROFILE", ""), "Quantify", "local_measurements"),
]
OTHER_DATA_FILE = "other_data.json"
JSON_DATA_FILE = "json_dataset.json"
EXCHANGER_FILE = os.path.join(ROOT_DIR, "source", "exchanger0.txt")


def find_saved_measurements():
    paths = []
    for base in DEFAULT_MEAS_DIRS:
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            if OTHER_DATA_FILE in files and JSON_DATA_FILE in files:
                paths.append(root)
    return sorted(paths)


def choose_saved_measurement(path_arg=None):
    if path_arg:
        if os.path.isdir(path_arg):
            return os.path.abspath(path_arg)
        raise FileNotFoundError(f"Measurement folder does not exist: {path_arg}")
    saved = find_saved_measurements()
    if not saved:
        raise FileNotFoundError("No saved measurement folders found in standard locations.")
    print("Found saved measurement folders:")
    for idx, folder in enumerate(saved, start=1):
        print(f"  {idx}: {folder}")
    while True:
        choice = input("Choose a folder number or paste a folder path: ").strip()
        if not choice:
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(saved):
            return saved[int(choice) - 1]
        if os.path.isdir(choice):
            return os.path.abspath(choice)
        print("Invalid choice. Try again.")


def load_saved_data(folder):
    other_path = os.path.join(folder, OTHER_DATA_FILE)
    json_path = os.path.join(folder, JSON_DATA_FILE)
    if not os.path.isfile(other_path) or not os.path.isfile(json_path):
        raise FileNotFoundError("Saved measurement JSON files not found in folder.")
    with open(other_path, "r", encoding="utf-8") as f:
        other_data = json.load(f)
    with open(json_path, "r", encoding="utf-8") as f:
        json_dataset = json.load(f)
    return other_data, json_dataset


def infer_labels(other_data):
    parameters = other_data.get("parameters", [])
    settables = []
    gettables = []
    if len(parameters) >= 1 and isinstance(parameters[0], dict):
        settables = [list(item.keys())[0] for item in parameters[0].get("settables", []) if isinstance(item, dict) and item]
    if len(parameters) >= 2 and isinstance(parameters[1], dict):
        gettables = list(parameters[1].get("recorded", []))
    return settables, gettables


def build_xarray_dataset(json_dataset, settables, gettables):
    coords = {label: ("dim_0", np.asarray(json_dataset[label], dtype=np.float32)) for label in settables}
    data_vars = {label: ("dim_0", np.asarray(json_dataset[label], dtype=np.float32)) for label in gettables}
    return xr.Dataset(data_vars=data_vars, coords=coords)


def load_transfer_module(child_folder):
    transfer_path = os.path.join(child_folder, "cpp_interface", "transfer.py")
    spec = importlib.util.spec_from_file_location("transfer", transfer_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_initial_writes(proc_id, my_oned_id, gettable_id, settables_labels, gettables_labels, dataset, name, data_store_path, parent_pid, mem_addresses):
    # compress dataset similar to quantify_measurement.compress_dset_json_for_initial_transfer
    dset_json = dataset.to_dict()
    # replace each data_var's data with its length to match the child ingester expectation
    for data_var_key, var_container in dset_json.get("data_vars", {}).items():
        data_list = var_container.get("data", [])
        try:
            data_len = len(data_list)
        except Exception:
            data_len = 0
        var_container["data"] = [data_len]

    # keep coords as-is (we did not clear them) so the child can consume them directly
    initial_writes = {
        "proc_id": str(proc_id),
        "my_oned_id": str(my_oned_id),
        "gettable_id": str(gettable_id),
        "settables_labels": json.dumps(settables_labels),
        "gettables_labels": json.dumps(gettables_labels),
        "dataset": json.dumps(dset_json),
        "name": name,
        "data_store_path": data_store_path,
        "parent_pid": str(parent_pid),
        "mem_addresses": json.dumps(mem_addresses),
    }
    return json.dumps(initial_writes) + "\n"


def create_exchanger_file():
    os.makedirs(os.path.dirname(EXCHANGER_FILE), exist_ok=True)
    with open(EXCHANGER_FILE, "w", encoding="utf-8") as f:
        pass


def respond_to_plotter(child_proc, transfer_module, json_dataset, settables, gettables):
    setp_index = len(json_dataset[settables[0]]) if settables else len(json_dataset[gettables[0]])
    while child_proc.poll() is None:
        time.sleep(0.01)
        with open(EXCHANGER_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content == "0":
            transfer_module.handle.set_transfer_semaphore(True)
            for idx, label in enumerate(gettables):
                transfer_module.write_array(idx, json_dataset[label])
            transfer_module.handle.set_setp_index(setp_index)
            transfer_module.handle.set_transfer_semaphore(False)
            with open(EXCHANGER_FILE, "w", encoding="utf-8") as f:
                f.write("01")
        elif content.endswith("2"):
            with open(EXCHANGER_FILE, "w", encoding="utf-8") as f:
                f.write("")


def run(folder):
    other_data, json_dataset = load_saved_data(folder)
    settables, gettables = infer_labels(other_data)
    if not settables or not gettables:
        raise ValueError("Saved data does not contain usable settables/gettables labels.")

    dimension = other_data.get("dimension")
    if dimension not in (1, 2):
        dimension = 2 if len(settables) >= 2 else 1

    if dimension == 1:
        child_dir = os.path.join(ROOT_DIR, "source", "custom1D")
        child_script = "mainv2.py"
        my_oned_id = 0
        gettable_id = 0
    else:
        child_dir = os.path.join(ROOT_DIR, "source", "custom2D")
        child_script = "mainv2D.py"
        my_oned_id = 0
        gettable_id = 0

    dataset = build_xarray_dataset(json_dataset, settables, gettables)
    transfer_module = load_transfer_module(child_dir)

    try:
        transfer_module.main(recompile=False)
    except Exception:
        transfer_module.main(recompile=True)

    transfer_module.handle.set_setp_index(0)
    transfer_module.handle.set_transfer_semaphore(False)

    create_exchanger_file()
    initial_writes = make_initial_writes(
        proc_id=0,
        my_oned_id=my_oned_id,
        gettable_id=gettable_id,
        settables_labels=settables,
        gettables_labels=gettables,
        dataset=dataset,
        name=other_data.get("measurement_name", "Reopened Measurement"),
        data_store_path=folder,
        parent_pid=os.getpid(),
        mem_addresses={
            "setp_index_address": transfer_module.handle.get_setp_pointer(),
            "transfer_semaphore_address": transfer_module.handle.get_transfer_semaphore_pointer(),
        },
    )

    child_args = transfer_module.get_child_args().split(" ")
    child_proc = subprocess.Popen(
        [sys.executable, child_script] + child_args,
        cwd=child_dir,
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        bufsize=0,
    )
    child_proc.stdin.writelines(initial_writes)
    child_proc.stdin.flush()

    respond_to_plotter(child_proc, transfer_module, json_dataset, settables, gettables)
    child_proc.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reopen a saved measurement into the existing custom plotter programs.")
    parser.add_argument("folder", nargs="?", help="Path to saved measurement folder")
    args = parser.parse_args()

    try:
        folder = choose_saved_measurement(args.folder)
        run(folder)
    except Exception as exc:
        print(f"Error reopening plotter: {exc}")
        sys.exit(1)
