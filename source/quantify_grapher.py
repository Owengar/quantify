import http.server
import multiprocessing.spawn
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
    try:
        _process_exchange._del_exchange_dir()
    except:
        pass
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














class plotly():
    def __init__(self, trace_plotting_method : Literal["total_live"] = "total_live"):
        self.trace_plotting_method = trace_plotting_method
    def plot(self, name : str, measurement_control : MeasurementControl, data_store_path : str, comments : str = None):
        self.measurement_configuration._set_comments(comments, measurement_control)
        _plotly_plot(name, measurement_control, data_store_path, self, self.trace_plotting_method)
default_plotly_configuration = plotly()




class measurement_configuration():
    def __init__(self, plotting_engine : plotly = default_plotly_configuration):
        self._plotting_engine = plotting_engine
        self._plotting_engine.measurement_configuration = self
        
        self.plot = self._plotting_engine.plot
    def _set_comments(self, comments, measurement_control):
        if comments:
            measurement_control.comments = comments
        else:
            measurement_control.comments = "No comments written."

default_measurement_configuration = measurement_configuration()

"""

class measurement_configuration():
    def __init__(self, plot_visuals : Literal["matplotlib", "plot_monitor"] = "matplotlib", update_visual_on : Literal["after_step", "after_sweep"] = "after_step", update_hdf5_on : Literal["after_step", "after_sweep", "after_measurement"] = "after_sweep", show_measurement_legend : bool = True, bad_hdf5_deletion : bool = True):
        \"""
        A configuration object that stores different visual and data preferences that are used in the ``plot`` function. Pass into the ``plot`` to use your own configuration.

        Parameters
        -

        - .. plot_visuals:: Choose what graphing system to use when plotting the visuals.
        - .. update_visual_on:: At what point to update the main plot monitor's individual sweeps. ``after_sweep`` for after the sweep completes, and ``after_step`` for after a new data point is measured.
        - .. update_hdf5_on:: At what point to write newly measured data into the hdf5 file.  ``after_step`` for after a new data point is measured, ``after_sweep`` for after a sweep completes, and ``after_measurement`` for after the enire measurement completes.
        - .. show_measurement_legend:: Whether or not to show the legend of all measurements on the main plot monitor. This is useful when doing many sweeps to prevent visual clutter. ``True`` for legend, ``False`` for no legend.
        - .. bad_hdf5_deletion :: Whether or not to delete the automatically made and incorrectly structured hdf5 files quantify uses to render once the measurement is done. This is reccomended to be ``True`` to prevent file clutter.\"""
        self.plot_visuals = plot_visuals
        self.update_visual_on = update_visual_on
        self.update_hdf5_on = update_hdf5_on
        self.show_measurement_legend = show_measurement_legend
        self.bad_hdf5_deletion = bad_hdf5_deletion

    def plot(self, name : str, measurement_control : MeasurementControl, parameters : list[Parameter], data_store_path : str, comments : str = None):
        \"""Please do not include spaces in the name parameter.\"""
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
        elif self.plot_visuals == "plotly":
            _plotly_plot(name, measurement_control, parameters, data_store_path, self)
"""




class _function_wrapper():
    def blank():
        print("blank", flush=True)
    def __init__(self, function = blank):
        self.func = function
    def __call__(self):
        self.func()
    def set_to(self, new_function):
        self.func = new_function
def true():
        return True






























def _plotly_plot(name, measurement_control : MeasurementControl, data_store_path, measurement_configuration, trace_plotting_method):


    data_store_path = str(data_store_path)
    dh.set_datadir(_process_exchange._get_source_path() + "/_do_not_use")





    measurement_control._setpoints_shape = [len(i) for i in measurement_control._setpoints_input]
    measurement_control._highest = len(measurement_control._setpoints_shape)
    measurement_control._settables_names = [settable.label+ f" ({settable.unit})" for settable in measurement_control._settable_pars]
    measurement_control._init(name)
    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs['name']}_dataset_{measurement_control._dataset.attrs['tuid']}.hdf5"


    def rename_coord_sorter(name):
        return name[1]
    rename_dict = {}
    sorted_coords = list(measurement_control._dataset.coords._names)
    sorted_coords.sort(key=rename_coord_sorter)
    for i,settable_coord in enumerate(sorted_coords):
        rename_dict[settable_coord] = measurement_control._settable_pars[i].label + f" ({measurement_control._settable_pars[i].unit})"
    for i,gettable_coord in enumerate(measurement_control._dataset.data_vars.keys()):
        rename_dict[gettable_coord] = measurement_control._gettable_pars[i].label + f" ({measurement_control._gettable_pars[i].unit})"



    def prep_traces_dset():
        return measurement_control._dataset.rename_vars(rename_dict)




    def write_new_2d_data():
        unshaped_dset = measurement_control._dataset.y0.data
        #dset = unshaped_dset.reshape(measurement_control._setpoints_shape).tolist()

        unshaped_dset = unshaped_dset[~numpy.isnan(unshaped_dset)]

        new_dset_len = len(unshaped_dset)
        with open(_process_exchange._get_proc_exchange_dir()+"\\fig_2d_data.txt", "w") as fig_data:
            #print(make_step_counts(old_dset_len[0], index_divisors))
            fig_data.write(json.dumps([old_dset_len[0], new_dset_len]) + "\n")
            fig_data.write(json.dumps(unshaped_dset[old_dset_len[0]:new_dset_len].tolist()) + "\n")
        old_dset_len[0] = new_dset_len

    def write_new_1d_data():
        with open(_process_exchange._get_proc_exchange_dir()+"\\fig_1d_data.txt", "w") as fig_data:
            fig_data.write(json.dumps(prep_traces_dset().to_dict()) + "\n")






    all_plot_functions = []
    old_dset_len = [0]
    def twod_plot():
        if last_data_request[0] == -1:
            last_data_request[0] = time.time()
        if _process_exchange._wait_for_signal("update_data_2d", true, False):
            last_data_request[0] = time.time()
            write_new_2d_data()
            while True:
                try:
                    os.remove(_process_exchange._find_signal_path("update_data_2d"))
                    break
                except:
                    continue
        else:
            if time.time() - last_data_request[0] > 4:
                pass
                #plotly_proc_2d.terminate()
                #print("\n2D Graphing Stopped\n")
                """ dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
                print("\n\nMeasurement interrupted.\n", flush=True)
                sys.stdout.flush()
                _close_procedure() """


    def oned_plot():
        if last_data_request[0] == -1:
            last_data_request[0] = time.time()
        if _process_exchange._wait_for_signal("update_data_1d", true, False):
            last_data_request[0] = time.time()
            write_new_1d_data()
            while True:
                try:
                    os.remove(_process_exchange._find_signal_path("update_data_1d"))
                    break
                except:
                    continue
        else:
            if time.time() - last_data_request[0] > 150:
                pass
                #terminate_procs()
                #dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
                #print("\n\nMeasurement interrupted.\n", flush=True)
                #sys.stdout.flush()
                #_close_procedure()

    processes = []
    if len(measurement_control._setpoints_shape) == 2:
        _process_exchange._make_signal_file("fig_2d_data.txt")
        with open(_process_exchange._get_proc_exchange_dir()+"\\fig_2d_data.txt", "w") as fig_data:
            fig_data.write(measurement_control._settables_names[0] + "\n")
            fig_data.write(measurement_control._settables_names[1] + "\n")
            fig_data.write(measurement_control._gettable_pars[0].label + f" ({measurement_control._gettable_pars[0].unit})" + "\n")
            fig_data.write(json.dumps(list(measurement_control._setpoints_input[0])) + "\n")
            fig_data.write(json.dumps(list(measurement_control._setpoints_input[1])) + "\n")
            fig_data.write(json.dumps(measurement_control._dataset.y0.data.tolist()) + "\n")
            fig_data.write(json.dumps(measurement_control._setpoints_shape) + "\n")
            fig_data.write(name + "\n")
        plotly_proc_2d = subprocess.Popen("python source/plotly_grapher_2d.py", shell=True, text=True)
        processes.append(plotly_proc_2d)
        all_plot_functions.append(twod_plot)
    
    all_plot_functions.append(oned_plot)
    for i,settble in enumerate(measurement_control._settable_pars):
        _process_exchange._make_signal_file("fig_1d_data.txt")
        with open(_process_exchange._get_proc_exchange_dir()+"\\fig_1d_data.txt", "w") as fig_data:
            fig_data.write(str(i) + "\n")
            fig_data.write(json.dumps(measurement_control._settables_names) + "\n")
            fig_data.write(measurement_control._gettable_pars[0].label + f" ({measurement_control._gettable_pars[0].unit})" + "\n")
            fig_data.write(json.dumps(prep_traces_dset().to_dict()) + "\n")
            fig_data.write(name + "\n")
        if trace_plotting_method == "total_live":
            plotly_proc_1d = subprocess.Popen("python source/live_total_plotly_grapher_1d.py", shell=True, text=True)
        elif trace_plotting_method == "last_100_points_live":
            plotly_proc_1d = subprocess.Popen("python source/last_100_plotly_grapher_1d.py", shell=True, text=True)
        elif trace_plotting_method == "no_live_trace_plotting":
            break
        while os.path.exists(_process_exchange._find_signal_path("fig_1d_data.txt")):
            pass
            #print("waiting")
        processes.append(plotly_proc_1d)

    #EXTRA GETTABLES
    for i,gettable in enumerate(measurement_control._gettable_pars[1:]):
        _process_exchange._make_signal_file("fig_1d_data.txt")
        with open(_process_exchange._get_proc_exchange_dir()+"\\fig_1d_data.txt", "w") as fig_data:
            fig_data.write("0" + "\n")
            fig_data.write(json.dumps(measurement_control._settables_names) + "\n")
            fig_data.write(gettable.label + f" ({gettable.unit})" + "\n")
            fig_data.write(json.dumps(prep_traces_dset().to_dict()) + "\n")
            fig_data.write(name + "\n")
        if trace_plotting_method == "total_live":
            plotly_proc_1d = subprocess.Popen("python source/live_total_plotly_grapher_1d.py", shell=True, text=True)
        elif trace_plotting_method == "last_100_points_live":
            plotly_proc_1d = subprocess.Popen("python source/last_100_plotly_grapher_1d.py", shell=True, text=True)
        elif trace_plotting_method == "no_live_trace_plotting":
            break
        while os.path.exists(_process_exchange._find_signal_path("fig_1d_data.txt")):
            pass
            #print("waiting")
        processes.append(plotly_proc_1d)




    def terminate_procs():
        for proc in processes:
            proc.terminate()
    
    def check_all_done():
        for proc in processes:
            if not proc.poll():
                return False
        return True
    def all_plot():
        for plot_function in all_plot_functions:
            plot_function()

    last_data_request = [-1]
    measurement_control.run(step_function=all_plot)
    while not check_all_done():
        all_plot()


    while True:
        try:
            os.remove(_process_exchange._find_signal_path("update_data"))
        except:
            pass
        if check_all_done():
            terminate_procs()
            break


 

    dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
    print("\n\nMeasurement finished.\n", flush=True)
    sys.stdout.flush()
    _close_procedure()


































































class oned_trace():
    def __init__(self, settable, ax1d, shape, height, measurement_control):
        self.settable = settable
        self.ax1d = ax1d
        self.shape = shape
        self.height = height
        self.trace_limiter = 0


        self.measurement_control = measurement_control
        self.offset = min(measurement_control._setpoints_input[self.height])
        #self.xticks = numpy.arange(len(measurement_control._setpoints_input[self.height]) + self.offset)
        #self.xlabels = [round(i,2) for i in list(numpy.arange(self.offset))+(measurement_control._setpoints_input[self.height].tolist())]
        #self.xticks = self.xlabels
        self.xticks = numpy.arange(len(measurement_control._setpoints_input[self.height]) + self.offset)
        xlen = len(self.xticks) / 20
        self.xticks = [self.xticks[0]] + [self.xticks[int(xlen*i)] for i in range(1, 20)] + [self.xticks[-1]]
        self.xlabels = [xtick for xtick in self.xticks]

    def recalculate_limiter(self, measurement_control, step_counts):
        if self.trace_limiter != self.shape:
            self.trace_limiter = step_counts[self.height]+1
            self.x_list = measurement_control._setpoints_input[self.height][:self.trace_limiter]
    
    def relabel(self, measurement_control):
        yticks = numpy.arange(max(measurement_control._dataset.y0.data) + 1)
        if not len(yticks):
            yticks = [0]
        ylen = len(yticks) / 25
        yticks = [yticks[0]] + [yticks[int(ylen*i)] for i in range(1, 25)] + [yticks[-1]]
        self.ax1d.set_yticks(yticks, labels=yticks)

        self.ax1d.set_xticks(self.xticks, labels=self.xlabels)
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
        trace_figs.append(oned_trace(settable, ax1d, measurement_control._setpoints_shape[i], i, measurement_control))
        if i > 0:
            index_divisors.append(index_divisors[i-1] * measurement_control._setpoints_shape[i-1])
    index_divisors = list(reversed(index_divisors))
    fig_nums = list(range(2, len(trace_figs)+2))

    def make_step_counts(step_num, index_divisors):
        counts = []
        for divisor in index_divisors:
            counts.append(step_num // divisor)
            step_num %= divisor
        return list(reversed(counts))


    def render_2d_window():
        pass
    def render_1d_traces(step_counts):
        new_datapoint = measurement_control._dataset.y0.data[step_num[0]-1]
        for trace_fig in trace_figs:
            trace_fig.relabel(measurement_control)
            trace_fig.new_setpoint = measurement_control._setpoints_input[trace_fig.height][step_counts[trace_fig.height]]
            trace_fig.ax1d.scatter(trace_fig.new_setpoint, new_datapoint)
                









    if len(measurement_control._setpoints_shape) > 1:
        total_figures = len(trace_figs) + 1
        fig2d = plt.figure(1)
        fig_nums.append(1)
        ax2d = fig2d.add_subplot(1, 1, 1)

        reshaped_dataset = (xarray.DataArray(measurement_control._dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))
        colorbar = fig2d.colorbar(ax2d.imshow(reshaped_dataset, origin="lower"), ax=ax2d, label=measurement_control._gettable_pars[0].label)
        measurement_control._dataset = measurement_control._dataset.assign_coords({"nD" : reshaped_dataset})


        for i,settable_name in enumerate(measurement_control._settables_names):
            measurement_control._dataset = measurement_control._dataset.assign({f"isolated_{settable_name}" : (measurement_control._setpoints_input[i].tolist())})

        xticks = numpy.arange(measurement_control._setpoints_shape[0])
        xlen = len(xticks) / 20
        xticks = [xticks[0]] + [xticks[int(xlen*i)] for i in range(1, 20)] + [xticks[-1]]
        xlabels = [round(measurement_control._setpoints_input[0][xtick], 2) for xtick in xticks]


        yticks = numpy.arange(measurement_control._setpoints_shape[1])
        ylen = len(yticks) / 20
        yticks = [yticks[0]] + [yticks[int(ylen*i)] for i in range(1, 20)] + [yticks[-1]]
        ylabels = [round(measurement_control._setpoints_input[1][ytick], 2) for ytick in yticks]



        def twod_labels_ticks():
            ax2d.set_xticks(xticks, labels=xlabels)
            ax2d.set_yticks(yticks, labels=ylabels)
            ax2d.set_xlabel(measurement_control._settable_pars[0].label)
            ax2d.set_ylabel(measurement_control._settable_pars[1].label)
        twod_labels_ticks()

        def render_2d_window():
            ax2d.clear()
            twod_labels_ticks()
            reshaped_dataset = (xarray.DataArray(measurement_control._dataset.y0.data.reshape(list(reversed(measurement_control._setpoints_shape))), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))
            image = ax2d.imshow(reshaped_dataset, origin="lower")

            colorbar.update_normal(image)

        

    else:
        total_figures = len(trace_figs)

    for i,trace_fig in enumerate(trace_figs):
        offset = min(measurement_control._setpoints_input[i])
        #trace_fig.offset = offset


        #trace_fig.xticks = numpy.arange(len(measurement_control._setpoints_input[i]) + offset)
        #trace_fig.xlabels = [round(i,2) for i in list(numpy.arange(offset))+(measurement_control._setpoints_input[i].tolist())]
        #trace_fig.ax1d.set_xticks(numpy.arange(len(measurement_control._setpoints_input[i]) + offset), labels=[round(i,2) for i in list(numpy.arange(offset))+(measurement_control._setpoints_input[i].tolist())])
        labels=[round(i,2) for i in numpy.unique(measurement_control._dataset.y0.data)]
        trace_fig.ax1d.set_yticks(numpy.arange(len(labels)), labels=labels)
        trace_fig.ax1d.set_xlabel(trace_fig.settable.label)
        trace_fig.ax1d.set_ylabel(measurement_control._gettable_pars[0].label)





    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs['name']}_dataset_{measurement_control._dataset.attrs['tuid']}.hdf5"
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

        for fig_num in fig_nums:
            if plt.fignum_exists(fig_num):
                return
        plt.close()
        measurement_control._update(force_update=True)
        dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
        print("\n\nMeasurement finished.\n", flush=True)
        sys.stdout.flush()
        _close_procedure()

    measurement_control.run(name, step_function=step)
    measurement_control._update(force_update=True)
    dh.write_dataset(dataset_path_name, _prep_hdf5_dset(measurement_control._dataset, measurement_control))
    print("\n\nMeasurement finished.\n", flush=True)
    sys.stdout.flush()
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








def _plot_plotmonitor(measurement_control : MeasurementControl, plotmon : PlotMonitor_pyqt, name : str, parameters : list[Parameter], data_store_path : str, measurement_configuration : measurement_configuration = default_measurement_configuration):
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
    plotmon.update(measurement_control._dataset.attrs['tuid'])

    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs['name']}_dataset_{measurement_control._dataset.attrs['tuid']}.hdf5"
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

    dataset_path_name = data_store_path+f"\\{measurement_control._dataset.attrs['name']}_dataset_{measurement_control._dataset.attrs['tuid']}.hdf5"
    meas_chunk_updater = _function_wrapper()

    if _update_hdf5_map[measurement_configuration.update_hdf5_on] == 1:
        def step_function():
            if step_counter[0] == 0:
                meas_chunk_updater.set_to(_start_new_measurement(highlight_measurement, plotmon, measurement_control, sweep_count, sweep_length, measurement_configuration))
            meas_chunk_updater()
            if step_counter[0] == sweep_length-1:
                highlight_measurement._update(force_update=True)
                #before = time.time()
                plotmon.update(highlight_measurement._dataset.attrs['tuid'])
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
                plotmon.update(highlight_measurement._dataset.attrs['tuid'])
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
                plotmon.update(highlight_measurement._dataset.attrs['tuid'])
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
            plotmon.update(highlight_measurement._dataset.attrs['tuid'])

    else:
        def update_measurement_chunk():
            _nan_empty_dataset(highlight_measurement._dataset)
            current_dset_y0 = measurement_control._dataset.y0.data
            start_selection_index = ((sweep_count[0]-1) * sweep_length)
            end_selection_index = ((sweep_count[0]) * sweep_length)-1
            for i in range(len(current_dset_y0)):
                if i >= start_selection_index and i <= end_selection_index:
                    highlight_measurement._dataset.y0.data[i] = current_dset_y0[i]









    plotmon.tuids_append(highlight_measurement._dataset.attrs['tuid'], append_right=True)
    return update_measurement_chunk
