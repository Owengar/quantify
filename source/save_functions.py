import os, xarray, shutil, traceback, time, datetime
import quantify_core.data.handling as dh


def make_data_store_path(meas_ctrl):
	measurements_dir = f"{os.environ['USERPROFILE']}\\Box\\Quantum Device Lab\\Quantify\\Measurements"
	now = datetime.datetime.now()
	measurements_dir += f"\\{now.year}"
	if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt"):
		with open(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt", "r") as install_info:
			measurements_dir += f"\\{install_info.readline().removesuffix('\n')}"
	else:
		measurements_dir += f"\\{os.path.basename(os.environ['USERPROFILE'])}"
	measurements_dir += f"\\{now.month}"
	measurements_dir += f"\\{now.day}"
	if not os.path.exists(measurements_dir):
		os.makedirs(measurements_dir)

	data_store_path = measurements_dir + f"\\{meas_ctrl._dataset.attrs['name']}_dataset_{meas_ctrl._dataset.attrs['tuid']}"
	if not os.path.exists(data_store_path):
		os.makedirs(data_store_path)
	return data_store_path

def make_local_data_store_path(meas_ctrl):
	measurements_dir = f"{os.environ['USERPROFILE']}\\Quantify\\local_measurements"
	now = datetime.datetime.now()
	measurements_dir += f"\\{now.year}"
	if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt"):
		with open(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt", "r") as install_info:
			measurements_dir += f"\\{install_info.readline().removesuffix('\n')}"
	else:
		measurements_dir += f"\\{os.path.basename(os.environ['USERPROFILE'])}"
	measurements_dir += f"\\{now.month}"
	measurements_dir += f"\\{now.day}"
	if not os.path.exists(measurements_dir):
		os.makedirs(measurements_dir)

	data_store_path = measurements_dir + f"\\{meas_ctrl._dataset.attrs['name']}_dataset_{meas_ctrl._dataset.attrs['tuid']}"
	if not os.path.exists(data_store_path):
		os.makedirs(data_store_path)
	return data_store_path


def get_computer_name():
	if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt"):
		with open(os.path.dirname(os.path.abspath(__file__)) + "\\install_info.txt", "r") as install_info:
			return install_info.readline().removesuffix('\n')
	else:
		return os.path.basename(os.environ['USERPROFILE'])

#Prep dataset for hdf5 saving
def prep_hdf5_dset(dataset : xarray.Dataset, measurement_control):

	occurrences = {}
	def duplicate_name_check(name):
		pretty_name = name
		if pretty_name in occurrences:
			occurrences[pretty_name] += 1
			pretty_name = name + f"#{occurrences[pretty_name]-1}"
		else:
			occurrences[pretty_name] = 2
		return pretty_name

	rename_dict = {}
	for var in dataset.variables:
		rename_dict[var] = duplicate_name_check(dataset[var].attrs.get("name", var))
	if len(measurement_control._setpoints_shape) > 1:
		dataset = dataset.assign_coords({"nD" : (xarray.DataArray(dataset.y0.data.reshape(measurement_control._setpoints_shape), dims=[f"isolated_{name}" for name in measurement_control._settables_names]))})

	if measurement_control.comments:
		dataset.attrs["comments"] = measurement_control.comments
		dataset.assign({"Comments" : measurement_control.comments})
	return dataset.rename_vars(rename_dict)


def save_hdf5(data_store_path, meas_ctrl):
	hdf5_path = data_store_path+f"\\{meas_ctrl._dataset.attrs['name']}_dataset_{meas_ctrl._dataset.attrs['tuid']}.hdf5"
	dh.write_dataset(hdf5_path, prep_hdf5_dset(meas_ctrl._dataset, meas_ctrl))

def save_measurement_script(data_store_path):
	script_path = traceback.extract_stack()[0].filename
	shutil.copy(script_path, data_store_path+f"\\Script - {script_path.split("\\")[-1]}")

def request_screenshot(data_store_path, wait_s=5):
	time.sleep(7) #pre wait to let the grahphs open in time (Only helps testing)
	with open("source\\screenshot_0.txt", "w") as screenshot_request:
		screenshot_request.write(data_store_path+"\\graph_thumbnail\n")
	start_time = time.time()
	while time.time()-start_time < wait_s:
		if not os.path.exists("source\\screenshot_0.txt"):
			return "screenshot request succeeded"
	#failure
	os.remove("source\\screenshot_0.txt")
	return "screenshot request failed"

def get_formatted_time():
	now = datetime.datetime.now()
	formatted_time = now.strftime("%I:%M %p")
	return f"{now.date()} {formatted_time}"


def save_text(txt : str):
	str_time = str(time.time())
	with open(f"txt_log_{str_time}", "w") as file:
		file.write(txt)