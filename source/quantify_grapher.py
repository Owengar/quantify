from source.imports import *
import source._process_exchange as _process_exchange







def _check_runner_signal():
    start_time = time.time()
    time_with_no_signal = [0]
    def _no_signal():
        time_with_no_signal[0] = time.time() - start_time
        if time_with_no_signal[0] > 2:
            return True
        else:
            return False
    
    if _process_exchange._wait_for_signal("ran_from_meas_runner", break_condition=_no_signal):
        stdout = open(_process_exchange._find_signal_path("stdout.txt"), "a")
        sys.stdout = stdout
        sys.stderr = stdout
        return

    direct_run = input("\n\nYou are running a measurement script directly, please run measurement scripts from the \"measurement_runner\" file. Running from the measurement script directly can cause the measurement shutdown procedure to not execute if an interruption occurs. Do you want to continue? y/n : ").lower()
    while True:
        if direct_run == "y":
            break
        elif direct_run == "n":
            print("\n\n")
            sys.exit()
        else:
            direct_run = input("Please enter only \"y\" or \"n\" : ")

_check_runner_signal()






_hdf5_deletion = True
def _close_procedure():
    if _hdf5_deletion:
        shutil.rmtree(dh.get_datadir())
    print("\n\n\n\nclosing...", flush=True)
    sys.stdout.flush()
    sys.stdout.close()
    _process_exchange._del_exchange_dir()
    os.abort()

    
_plotmon = None
def _check_windows_closed():
    
    windows = Desktop(backend="uia").windows()
    for window in windows:
        window = str(window)
        if _plotmon.name.lower() in window.lower():
            return
    else:
        _close_procedure()

    """ try:
        _plotmon._remote_plotmon.main_QtPlot.win.closed
    except:
        _close_procedure() """
























class measurement_configuration():
    def __init__(self, plot_visuals : Literal["matplotlib", "plot_monitor"] = "matplotlib", update_visual_on : Literal["after_step", "after_sweep"] = "after_step", update_hdf5_on : Literal["after_step", "after_sweep", "after_measurement"] = "after_sweep", show_measurement_legend : bool = True, bad_hdf5_deletion : bool = True):
        """
        A configuration object that stores different visual and data preferences that are used in the ``plot`` function. Pass into the ``plot`` to use your own configuration.

        Parameters
        -

        - .. plot_visuals:: Choose what graphing system to use when plotting the visuals.
        - .. update_visual_on:: At what point to update the main plot monitor's individual sweeps. ``after_sweep`` for after the sweep completes, and ``after_step`` for after a new data point is measured.
        - .. update_hdf5_on:: At what point to write newly measured data into the hdf5 file.  ``after_step`` for after a new data point is measured, ``after_sweep`` for after a sweep completes, and ``after_measurement`` for after the enire measurement completes.
        - .. show_measurement_legend:: Whether or not to show the legend of all measurements on the main plot monitor. This is useful when doing many sweeps to prevent visual clutter. ``True`` for legend, ``False`` for no legend.
        - .. bad_hdf5_deletion :: Whether or not to delete the automatically made and incorrectly structured hdf5 files quantify uses to render once the measurement is done. This is reccomended to be ``True`` to prevent file clutter."""
        self.plot_visuals = plot_visuals
        self.update_visual_on = update_visual_on
        self.update_hdf5_on = update_hdf5_on
        self.show_measurement_legend = show_measurement_legend
        self.bad_hdf5_deletion = bad_hdf5_deletion

    def plot(self, name : str, measurement_control : MeasurementControl, parameters : list[Parameter], data_store_path : str, comments : str = None):
        """Please do not include spaces in the name parameter."""
        if comments:
            measurement_control.comments = comments
        else:
            measurement_control.comments = "No comments written."
        if self.plot_visuals == "matplotlib":
            _matplotlib_plot(name, measurement_control, parameters, data_store_path, self)

        elif self.plot_visuals == "plot_monitor":
            plotmon = PlotMonitor_pyqt(name.replace(" ", ""))
            measurement_control.instr_plotmon(plotmon.name)
            _plot_plotmonitor(measurement_control, plotmon, name, parameters, data_store_path, self)

_default_setup_configuration = measurement_configuration()

class _function_wrapper():
    def blank():
        print("blank", flush=True)
    def __init__(self, function = blank):
        self.func = function
    def __call__(self):
        self.func()
    def set_to(self, new_function):
        self.func = new_function

















































class oned_trace():
    def __init__(self, settable, ax1d, shape, height):
        self.settable = settable
        self.ax1d = ax1d
        self.shape = shape
        self.height = height
        self.trace_limiter = 0

    def recalculate_limiter(self, measurement_control, step_counts):
        if self.trace_limiter != self.shape:
            self.trace_limiter = step_counts[self.height]+1
            self.x_list = measurement_control._setpoints_input[self.height][:self.trace_limiter]
    
    def relabel(self, measurement_control):
        self.ax1d.set_xticks(numpy.arange(len(measurement_control._setpoints_input[self.height]) + self.offset), labels=[round(i,2) for i in list(numpy.arange(self.offset))+(measurement_control._setpoints_input[self.height].tolist())])
        labels=[round(i,2) for i in numpy.unique(measurement_control._dataset.y0.data)]
        self.ax1d.set_yticks(numpy.arange(len(labels)), labels=labels)
        self.ax1d.set_xlabel(self.settable.label)
        self.ax1d.set_ylabel(measurement_control._gettable_pars[0].label)



def _matplotlib_plot(name : str, measurement_control : MeasurementControl, parameters : list[Parameter], data_store_path : str, measurement_configuration : measurement_configuration):
    global _hdf5_deletion
    _hdf5_deletion = measurement_configuration.bad_hdf5_deletion
    show_legend = measurement_configuration.show_measurement_legend
    update_hdf5_on = _update_hdf5_map[measurement_configuration.update_hdf5_on]
    update_visual_on = _update_visual_map[measurement_configuration.update_visual_on]



    data_store_path = str(data_store_path)
    dh.set_datadir(_process_exchange._get_source_path() + "/_do_not_use")





    measurement_control._setpoints_shape = [len(i) for i in measurement_control._setpoints_input]
    measurement_control._highest = len(measurement_control._setpoints_shape)
    measurement_control._settables_names = [settable.name for settable in measurement_control._settable_pars]
    measurement_control._init(name)

    trace_figs : list[oned_trace] = []
    index_divisors = [1]
    for i, settable in enumerate(measurement_control._settable_pars):
        fig1d = plt.figure(i+2)
        ax1d = fig1d.add_subplot(1, 1, 1)
        trace_figs.append(oned_trace(settable, ax1d, measurement_control._setpoints_shape[i], i))
        if i > 0:
            index_divisors.append(index_divisors[i-1] * measurement_control._setpoints_shape[i-1])
    index_divisors = list(reversed(index_divisors))

    def make_step_counts(step_num, index_divisors):
        counts = []
        for divisor in index_divisors:
            counts.append(step_num // divisor)
            step_num %= divisor
        return list(reversed(counts))


    def render_2d_window():
        pass
    def render_1d_traces(step_counts):
        for trace_fig in trace_figs:
            trace_fig.ax1d.clear()
        for trace_fig in trace_figs:
            self_height = trace_fig.height
            self_shape = trace_fig.shape
            labels = [round(i,2) for i in numpy.unique(measurement_control._dataset.y0.data)]
            trace_fig.ax1d.set_yticks(numpy.arange(max(labels)+1), labels=numpy.arange(max(labels)+1))
            trace_fig.ax1d.set_xlabel(trace_fig.settable.label)
            trace_fig.ax1d.set_ylabel(measurement_control._gettable_pars[0].label)
            trace_fig.recalculate_limiter(measurement_control, step_counts)
            grouped_dataset = measurement_control._dataset.sortby(f"x{self_height}").y0.data

            for i,set_val in enumerate(measurement_control._setpoints_input[self_height]):
                #print((i * self_shape, i + 1 *self_shape))
                target_data = grouped_dataset[0  + (self_shape * i): self_shape + (self_shape * i)]
                trace_fig.ax1d.plot([set_val for i in range(self_shape)], target_data, marker="o")
                


        """ 
        reshaped_dataset = reshapes[0]
        reshaped_dataset_2 = numpy.rot90(reshapes[0])
        if len(trace_figs) > 1:
            for trace_fig in trace_figs:
                trace_fig[1].clear()
            for trace_fig in trace_figs:
                self_height = trace_fig[3]
                labels = [round(i,2) for i in numpy.unique(measurement_control._dataset.y0.data)]
                #print(labels)
                
                trace_fig[1].set_yticks(numpy.arange(max(labels)+1), labels=numpy.arange(max(labels)+1))
                trace_fig[1].set_xlabel(trace_fig[0].label)
                trace_fig[1].set_ylabel(measurement_control._gettable_pars[0].label)

                

                other_trace = trace_figs[trace_fig[3]-1]
                other_height = other_trace[3]
                
                start = time.time()
                if self_height > other_height:
                    for index in range(other_trace[2]):
                        trace_fig[1].plot([measurement_control._setpoints_input[self_height][index] for i in measurement_control._setpoints_input[self_height]], reshaped_dataset[index], marker="o", label=f"{other_trace[0].label} = {index}")
                        if show_legend:
                            trace_fig[1].figure.legend('',frameon=False)
                            
                            trace_fig[1].legend()
                else:
                    for self_index in range(trace_fig[2]):
                        scatter_list = []
                        for index in range(other_trace[2]):
                            scatter_list.append(reshaped_dataset[index][self_index])
                        trace_fig[1].plot(measurement_control._setpoints_input[self_height], reshaped_dataset_2[index], marker="o", label=f"{other_trace[0].label} = {measurement_control._setpoints_input[other_height][self_index]}")
                        if show_legend:
                            trace_fig[1].figure.legend('',frameon=False)
                            
                            trace_fig[1].legend()
                done = time.time()
                #print(done-start)
        else:
            trace_fig = trace_figs[0]
            trace_fig[1].clear()
            labels = [round(i,2) for i in numpy.unique(measurement_control._dataset.y0.data)]
            trace_fig[1].set_yticks(numpy.arange(max(labels)+1), labels=numpy.arange(max(labels)+1))
            trace_fig[1].set_xlabel(trace_fig[0].label)
            trace_fig[1].set_ylabel(measurement_control._gettable_pars[0].label)

            trace_fig[1].plot(measurement_control._setpoints_input[trace_fig[3]], reshaped_dataset, marker="o", label=f"{measurement_control._gettable_pars[0].label} as a function of {trace_fig[0].label}")
            if show_legend:
                trace_fig[1].figure.legend('',frameon=False)
                
                trace_fig[1].legend()
 """







    if len(measurement_control._setpoints_shape) > 1:
        total_figures = len(trace_figs) + 1
        fig2d = plt.figure(1)
        ax2d = fig2d.add_subplot(1, 1, 1)


        reshaped_dataset = (xarray.DataArray(measurement_control._dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))
        colorbar = fig2d.colorbar(ax2d.imshow(reshaped_dataset, origin="lower"), ax=ax2d, label=measurement_control._gettable_pars[0].label)
        measurement_control._dataset = measurement_control._dataset.assign_coords({"nD" : reshaped_dataset})

        def render_2d_window():
            ax2d.clear()
            ax2d.set_xticks(numpy.arange(measurement_control._setpoints_shape[0]), labels=[round(i,2) for i in measurement_control._setpoints_input[0].tolist()])
            ax2d.set_yticks(numpy.arange(measurement_control._setpoints_shape[1]), labels=[round(i) for i in measurement_control._setpoints_input[1].tolist()])
            ax2d.set_xlabel(measurement_control._settable_pars[0].label)
            ax2d.set_ylabel(measurement_control._settable_pars[1].label)
            reshaped_dataset = (xarray.DataArray(measurement_control._dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))
            other_reshape = (xarray.DataArray(measurement_control._dataset.y0.data.reshape(measurement_control._setpoints_shape, order="F"), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))

            image = ax2d.imshow(reshaped_dataset, origin="lower")

            colorbar.update_normal(image)
            #fig2d.show()

        
        for i,settable_name in enumerate(measurement_control._settables_names):
            measurement_control._dataset = measurement_control._dataset.assign({f"isolated_{settable_name}" : (measurement_control._setpoints_input[i].tolist())})
        ax2d.set_xticks(numpy.arange(measurement_control._setpoints_shape[0]), labels=[round(i,2) for i in measurement_control._setpoints_input[0].tolist()])
        ax2d.set_yticks(numpy.arange(measurement_control._setpoints_shape[1]), labels=[round(i) for i in measurement_control._setpoints_input[1].tolist()])
        ax2d.set_xlabel(measurement_control._settable_pars[0].label)
        ax2d.set_ylabel(measurement_control._settable_pars[1].label)
    else:
        total_figures = len(trace_figs)

    for i,trace_fig in enumerate(trace_figs):
        offset = min(measurement_control._setpoints_input[i])
        trace_fig.offset = offset

        trace_fig.ax1d.set_xticks(numpy.arange(len(measurement_control._setpoints_input[i]) + offset), labels=[round(i,2) for i in list(numpy.arange(offset))+(measurement_control._setpoints_input[i].tolist())])
        labels=[round(i,2) for i in numpy.unique(measurement_control._dataset.y0.data)]
        trace_fig.ax1d.set_yticks(numpy.arange(len(labels)), labels=labels)
        trace_fig.ax1d.set_xlabel(trace_fig.settable.label)
        trace_fig.ax1d.set_ylabel(measurement_control._gettable_pars[0].label)







    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs["name"]}_dataset_{measurement_control._dataset.attrs["tuid"]}.hdf5"
    step_num = [0]
    total_steps = 1
    for shape in measurement_control._setpoints_shape:
        total_steps *= shape
    def step():
        counts = make_step_counts(step_num[0], index_divisors)
        if step_num[0] % measurement_control._setpoints_shape[0] == 0:
            if update_hdf5_on == 2:
                dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
            if not update_visual_on:
                render_2d_window()
                render_1d_traces(counts)
                plt.pause(0.001)
        if update_hdf5_on == 1:
            dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
        step_num[0] += 1


        if update_visual_on:
            render_2d_window()
            render_1d_traces(counts)
            plt.pause(0.001)
        return
        for fig_num in range(total_figures):
            plt.figure(fig_num+1)
            plt.pause(0.001)

    measurement_control.run(name, step_function=step)
    sys.stdout.flush()
    measurement_control._update(force_update=True)
    print("\n\nMeasurement finished.\n", flush=True)
    dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
    plt.show()
    _close_procedure()












































































































def _prep_hdf5_dset(dataset : xarray.Dataset, measurement_control):
    rename_dict = {}
    for var in dataset.variables:
        rename_dict[var] = dataset[var].attrs.get("name", var)
    if len(measurement_control._setpoints_shape) > 1:
        dataset = dataset.assign_coords({"nD" : (xarray.DataArray(dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))})

    if measurement_control.comments:
        dataset.attrs["comments"] = measurement_control.comments
        dataset.assign({"Comments" : measurement_control.comments})
    return dataset.rename_vars(rename_dict)


_update_visual_map = {"after_sweep" : False, "after_step" : True}
_update_hdf5_map = {"after_sweep" : 2, "after_step" : 1, "after_measurement": 3}








def _plot_plotmonitor(measurement_control : MeasurementControl, plotmon : PlotMonitor_pyqt, name : str, parameters : list[Parameter], data_store_path : str, measurement_configuration : measurement_configuration = _default_setup_configuration):
    global _plotmon, _hdf5_deletion
    #measurement_control.verbose.set(True)
    plotmon.interrupt_procedure = _close_procedure
    _plotmon = plotmon
    data_store_path = str(data_store_path)
    dh.set_datadir(_process_exchange._get_source_path() + "/_do_not_use")

    plotmon._remote_plotmon.show_legend = measurement_configuration.show_measurement_legend
    _hdf5_deletion = measurement_configuration.bad_hdf5_deletion

    measurement_control._setpoints_shape = [len(i) for i in measurement_control._setpoints_input]
    measurement_control._settables_names = [settable.name for settable in measurement_control._settable_pars]


    plotmon.tuids_max_num(100)
    measurement_control._init(name)
    if len(measurement_control._setpoints_shape) > 1:
        measurement_control._dataset = measurement_control._dataset.assign_coords({"nD" : (xarray.DataArray(measurement_control._dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))})
        for i,settable_name in enumerate(measurement_control._settables_names):
            measurement_control._dataset = measurement_control._dataset.assign({f"isolated_{settable_name}" : (measurement_control._setpoints_input[i].tolist())})
    measurement_control.run(name, step_function=_build_step_function(measurement_control, plotmon, parameters, data_store_path, measurement_configuration))
    sys.stdout.flush()
    measurement_control._update(force_update=True)
    plotmon.update(measurement_control._dataset.attrs["tuid"])

    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs["name"]}_dataset_{measurement_control._dataset.attrs["tuid"]}.hdf5"
    dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))



    print("\n\nMeasurement finished.\n", flush=True)
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

def _build_step_function(measurement_control : MeasurementControl, plotmon : PlotMonitor_pyqt, parameters : list[Parameter], data_store_path : str, measurement_configuration : measurement_configuration):

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

    if _update_hdf5_map[measurement_configuration.update_hdf5_on] == 1:
        def step_function():
            if step_counter[0] == 0:
                meas_chunk_updater.set_to(_start_new_measurement(highlight_measurement, plotmon, measurement_control, sweep_count, sweep_length, measurement_configuration))
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
            dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
    elif _update_hdf5_map[measurement_configuration.update_hdf5_on] == 2:
        def step_function():
            if step_counter[0] == 0:
                meas_chunk_updater.set_to(_start_new_measurement(highlight_measurement, plotmon, measurement_control, sweep_count, sweep_length, measurement_configuration))
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
                meas_chunk_updater.set_to(_start_new_measurement(highlight_measurement, plotmon, measurement_control, sweep_count, sweep_length, measurement_configuration))
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


def _start_new_measurement(highlight_measurement : MeasurementControl, plotmon : PlotMonitor_pyqt, measurement_control: MeasurementControl, sweep_count, sweep_length, measurement_configuration : measurement_configuration):
    after_step = _update_visual_map[measurement_configuration.update_visual_on]



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
