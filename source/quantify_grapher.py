from source.imports import *
import source._process_exchange as _process_exchange



#up 10




_hdf5_deletion = True
def _close_procedure():
    if _hdf5_deletion:
        shutil.rmtree(dh.get_datadir())
    print("\n\n\n\nclosing")
    os.abort()
_plotmon = None
def _check_windows_closed():
    try:
        _plotmon._remote_plotmon.main_QtPlot.win.closed
    except:
        _close_procedure()

_proc_exchange_folder_name = "temporary_proc_exchange_folder"
_proc_exchange_txt_name = "temporary_proc_exchange.txt"
_done_reading_signal = "done_reading"

def _find_proc_exhanger(proc_exchange_folder_name, proc_exchange_txt_name, source_path = ""):
    if not source_path:
        source_path = os.path.dirname(os.path.abspath(__file__))
    proc_exchange_dir = f"{source_path}\\{_proc_exchange_folder_name}"
    proc_exchanger_path = proc_exchange_dir + f"\\{_proc_exchange_txt_name}"
    return (proc_exchange_dir, proc_exchanger_path)


def _make_proc_exchange_holder(meas_ctrl, source_path = ""):
    proc_exchange_dir, proc_exchanger_path = _find_proc_exhanger(_proc_exchange_folder_name, _proc_exchange_txt_name, source_path=source_path)

    if os.path.exists(proc_exchange_dir):
        shutil.rmtree(proc_exchange_dir)
    os.mkdir(proc_exchange_dir)
    with open(proc_exchanger_path, "w") as proc_exchanger:
        proc_exchanger.write(str(os.getpid()) + "\n")
        proc_exchanger.write(proc_exchange_dir + "\n")
        proc_exchanger.write(str(id([meas_ctrl])) + "\n")
    return proc_exchange_dir

def _wait_for_dir_close_signal(proc_exchange_dir):
    while not _done_reading_signal in os.listdir(proc_exchange_dir):
        pass
    shutil.rmtree(proc_exchange_dir)

def _spawn_daemon(meas_ctrl):
    source_path = os.path.dirname(os.path.abspath(__file__))
    stop_detector_daemon_path = source_path + "\\stop_detector_daemon.py"
    proc_exhange_dir = _make_proc_exchange_holder(meas_ctrl, source_path=source_path)



    stop_detector_daemon_process = subprocess.Popen("python " + stop_detector_daemon_path, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)

    _wait_for_dir_close_signal(proc_exhange_dir)
    





class plot_setup_configuration():
    def __init__(self, update_visual_on : Literal["after_step", "after_sweep"] = "after_step", update_hdf5_on : Literal["after_step", "after_sweep", "after_measurement"] = "after_sweep", show_measurement_legend : bool = True, bad_hdf5_deletion : bool = True):
        """
        A configuration object that stores different visual and data preferences that are used in the ``plot`` function. Pass into the ``plot`` to use your own configuration.

        Parameters
        -

        - .. update_visual_on:: At what point to update the main plot monitor's individual sweeps. ``after_sweep`` for after the sweep completes, and ``after_step`` for after a new data point is measured.
        - .. update_hdf5_on:: At what point to write newly measured data into the hdf5 file.  ``after_step`` for after a new data point is measured, ``after_sweep`` for after a sweep completes, and ``after_measurement`` for after the enire measurement completes.
        - .. show_measurement_legend:: Whether or not to show the legend of all measurements on the main plot monitor. This is useful when doing many sweeps to prevent visual clutter. ``True`` for legend, ``False`` for no legend.
        - .. bad_hdf5_deletion :: Whether or not to delete the automatically made and incorrectly structured hdf5 files quantify uses to render once the measurement is done. This is reccomended to be ``True`` to prevent file clutter."""
        self.update_visual_on = update_visual_on
        self.update_hdf5_on = update_hdf5_on
        self.show_measurement_legend = show_measurement_legend
        self.bad_hdf5_deletion = bad_hdf5_deletion

_default_setup_configuration = plot_setup_configuration()

class _function_wrapper():
    def blank():
        print("blank")
    def __init__(self, function = blank):
        self.func = function
    def __call__(self):
        self.func()
    def set_to(self, new_function):
        self.func = new_function



























def _prep_hdf5_dset(dataset : xarray.Dataset, measurement_control):
    rename_dict = {}
    for var in dataset.variables:
        rename_dict[var] = dataset[var].attrs.get("name", var)
    if len(measurement_control._setpoints_shape) > 1:
        dataset = dataset.assign_coords({"nD" : (xarray.DataArray(dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))})
    return dataset.rename_vars(rename_dict)


_update_visual_map = {"after_sweep" : False, "after_step" : True}
_update_hdf5_map = {"after_sweep" : 2, "after_step" : 1, "after_measurement": 3}








def plot(measurement_control : MeasurementControl, plotmon : PlotMonitor_pyqt, name : str, parameters : list[Parameter], data_store_path : str, plot_setup_configuration : plot_setup_configuration = _default_setup_configuration):
    global _plotmon, _hdf5_deletion
    plotmon.interrupt_procedure = _close_procedure
    _plotmon = plotmon
    data_store_path = str(data_store_path)
    dh.set_datadir(_process_exchange._get_source_path() + "/_do_not_use")

    plotmon._remote_plotmon.show_legend = plot_setup_configuration.show_measurement_legend
    _hdf5_deletion = plot_setup_configuration.bad_hdf5_deletion

    measurement_control._setpoints_shape = [len(i) for i in measurement_control._setpoints_input]
    measurement_control._settables_names = [settable.name for settable in measurement_control._settable_pars]


    plotmon.tuids_max_num(100)
    measurement_control._init(name)
    if len(measurement_control._setpoints_shape) > 1:
        measurement_control._dataset = measurement_control._dataset.assign_coords({"nD" : (xarray.DataArray(measurement_control._dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))})
        for i,settable_name in enumerate(measurement_control._settables_names):
            measurement_control._dataset = measurement_control._dataset.assign({f"isolated_{settable_name}" : (measurement_control._setpoints_input[i].tolist())})
    measurement_control.run(name, step_function=_build_step_function(measurement_control, plotmon, parameters, data_store_path, plot_setup_configuration))
    measurement_control._update(force_update=True)
    plotmon.update(measurement_control._dataset.attrs["tuid"])

    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs["name"]}_dataset_{measurement_control._dataset.attrs["tuid"]}.hdf5"
    dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))




    _process_exchange._del_exchange_dir()
    while True:
        _check_windows_closed()

    



def _nan_empty_dataset(dataset):
    y0_len = len(dataset.y0.data)
    dataset.y0.data = numpy.array([numpy.nan for i in range(y0_len)])


def _blank_get():
    return -1
_blank_get_parameter = Parameter("blank_get", get_cmd=_blank_get)
def _blank_set(set_to):
    return
_blank_set_parameter = Parameter("blank_set", set_cmd=_blank_set)

def _build_step_function(measurement_control : MeasurementControl, plotmon : PlotMonitor_pyqt, parameters : list[Parameter], data_store_path : str, plot_setup_configuration : plot_setup_configuration):

    highlight_measurement = MeasurementControl("Sweep_1")
    highlight_measurement.update_interval(measurement_control.update_interval())
    highlight_measurement.settables(parameters[:-1])
    highlight_measurement.gettables(parameters[-1])
    highlight_measurement.setpoints_grid(measurement_control._setpoints_input)




    sweep_length = len(measurement_control._setpoints_input[0])
    step_counter = [0]
    sweep_count = [1]

    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs["name"]}_dataset_{measurement_control._dataset.attrs["tuid"]}.hdf5"
    meas_chunk_updater = _function_wrapper()

    if _update_hdf5_map[plot_setup_configuration.update_hdf5_on] == 1:
        def step_function():
            if step_counter[0] == 0:
                meas_chunk_updater.set_to(_start_new_measurement(highlight_measurement, plotmon, measurement_control, sweep_count, sweep_length, plot_setup_configuration))
            meas_chunk_updater()
            if step_counter[0] == sweep_length-1:
                highlight_measurement._update(force_update=True)
                #before = time.time()
                plotmon.update(highlight_measurement._dataset.attrs["tuid"])
                #after = time.time()
                #print(f"delay dif is {after-before}")

                

                highlight_measurement._dataset.close()
                highlight_measurement._reset()
                step_counter[0] = 0
                sweep_count[0] += 1
                parameters[0].label = "QDAC Output Voltage"
                parameters[1].label = "Sweep Number"
                parameters[2].label = "DMM Measured Voltage"
            else:
                step_counter[0] += 1
            dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
    elif _update_hdf5_map[plot_setup_configuration.update_hdf5_on] == 2:
        def step_function():
            if step_counter[0] == 0:
                meas_chunk_updater.set_to(_start_new_measurement(highlight_measurement, plotmon, measurement_control, sweep_count, sweep_length, plot_setup_configuration))
            meas_chunk_updater()
            if step_counter[0] == sweep_length-1:
                highlight_measurement._update(force_update=True)
                #before = time.time()
                plotmon.update(highlight_measurement._dataset.attrs["tuid"])
                #after = time.time()
                #print(f"delay dif is {after-before}")

                dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))

                highlight_measurement._dataset.close()
                highlight_measurement._reset()
                step_counter[0] = 0
                sweep_count[0] += 1
            else:
                step_counter[0] += 1
    else:
        def step_function():
            if step_counter[0] == 0:
                meas_chunk_updater.set_to(_start_new_measurement(highlight_measurement, plotmon, measurement_control, sweep_count, sweep_length, plot_setup_configuration))
            meas_chunk_updater()
            if step_counter[0] == sweep_length-1:
                highlight_measurement._update(force_update=True)
                #before = time.time()
                plotmon.update(highlight_measurement._dataset.attrs["tuid"])
                #after = time.time()
                #print(f"delay dif is {after-before}")


                highlight_measurement._dataset.close()
                highlight_measurement._reset()
                step_counter[0] = 0
                sweep_count[0] += 1
            else:
                step_counter[0] += 1
    return step_function


def _start_new_measurement(highlight_measurement : MeasurementControl, plotmon : PlotMonitor_pyqt, measurement_control: MeasurementControl, sweep_count, sweep_length, plot_setup_configuration : plot_setup_configuration):
    after_step = _update_visual_map[plot_setup_configuration.update_visual_on]



    highlight_measurement.run(f"Sweep_{sweep_count[0]}", multi_measurement=True, empty_run=True, save_data=False)
    
    if after_step:
        def update_measurement_chunk():
            _nan_empty_dataset(highlight_measurement._dataset)
            current_dset_y0 = measurement_control._dataset.y0.data
            start_selection_index = ((sweep_count[0]-1) * sweep_length)
            end_selection_index = ((sweep_count[0]) * sweep_length)-1
            for i in range(len(current_dset_y0)):
                if i >= start_selection_index and i <= end_selection_index:
                    highlight_measurement._dataset.y0.data[i] = current_dset_y0[i]
            highlight_measurement._update(force_update=True)
            plotmon.update(highlight_measurement._dataset.attrs["tuid"])

    else:
        def update_measurement_chunk():
            _nan_empty_dataset(highlight_measurement._dataset)
            current_dset_y0 = measurement_control._dataset.y0.data
            start_selection_index = ((sweep_count[0]-1) * sweep_length)
            end_selection_index = ((sweep_count[0]) * sweep_length)-1
            for i in range(len(current_dset_y0)):
                if i >= start_selection_index and i <= end_selection_index:
                    highlight_measurement._dataset.y0.data[i] = current_dset_y0[i]









    plotmon.tuids_append(highlight_measurement._dataset.attrs["tuid"], append_right=True)
    return update_measurement_chunk
