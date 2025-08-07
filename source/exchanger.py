import time, os










###############   PLOTTER SIDE FUNCTIONS
def set_proc_id(id: int):
    global _exchanger_file_name
    if "data_ingester_.py" in os.listdir():
        _exchanger_file_name = "source/exchanger.txt"
        big_path = os.path.abspath("data_ingester_.py")
        big_path = big_path.rsplit("\\", 2)
        _exchanger_file_name = big_path[0] + f"\\exchanger{id}.txt"
    else:
        _exchanger_file_name = f"source/exchanger{id}.txt"

    

def ask():
    read_result = 1
    while read_result:
        with open(_exchanger_file_name, "r") as exchanger:
            read_result = len(exchanger.read().removesuffix("\n"))
            time.sleep(0.001)
    with open(_exchanger_file_name, "a") as exchanger:
        exchanger.write("0")
def wait(state : str):
    while True:
        with open(_exchanger_file_name, "r") as exchanger:
            txt = exchanger.read().removesuffix("\n")
            if state == txt:
                break
        time.sleep(0.001)
def done(msg : str):
    with open(_exchanger_file_name, "a") as exchanger:
        exchanger.write(msg)

#################







############# MEAS SIDE FUNCTIONS
_exchanger_names = []
def find_exchangers(num_of_procs : int):
    for proc_id in range(num_of_procs):
        name = f"source/exchanger{proc_id}.txt"
        _exchanger_names.append(name)
        with open(name, "w") as exchanger: #pre clear
            pass



def wait_for_all_asking():
    all_zero = True
    while True:
        for proc_name in _exchanger_names:
            with open(proc_name, "r") as exchanger:
                txt = exchanger.read().removesuffix("\n")
                if txt != "0":
                    all_zero = False
        if all_zero:
            return
        else:
            time.sleep(0.001)
            all_zero = True
            
def give_all_one():
    for proc_name in _exchanger_names:
        with open(proc_name, "a") as exchanger:
            exchanger.write("1")



def wait_to_clear(): #wait for all procs to write 2
    all_two = True
    while True:
        for proc_name in _exchanger_names:
            with open(proc_name, "r") as exchanger:
                txt = exchanger.read().removesuffix("\n")
                if not ("2" in txt):
                    all_two = False
        if all_two:
            break
        else:
            time.sleep(0.001)
            all_two = True

    for proc_name in _exchanger_names:
        with open(proc_name, "w") as exchanger:
            pass

###############























"""

with open(_exchanger_file_name, "w") as exchanger: #pre clear
    pass

def ask():
    while True:
        print("stuck asking")
        with open(_exchanger_file_name, "r") as exchanger:
            read_result = exchanger.read().removesuffix("\n")
            if "1" in read_result or "2" in read_result: #if something else is happening wait to ask
                time.sleep(0.001)
            else: #this means that either the file is empty or there are zeroes
                break
    with open(_exchanger_file_name, "a") as exchanger:
        exchanger.write("0")
        return
        
def wait_for_ask(num_zeros : int):
    while True:
        with open(_exchanger_file_name, "r") as exchanger:
            txt = exchanger.read().removesuffix("\n")
            if txt == "0"*num_zeros:
                break
        time.sleep(0.001)

def wait_for_response():
     while True:
        print("stuck waiting for 1")
        with open(_exchanger_file_name, "r") as exchanger:
            txt = exchanger.read().removesuffix("\n")
            if "1" in txt:
                break
        time.sleep(0.001)
        
def done(msg : str):
    with open(_exchanger_file_name, "a") as exchanger:
        exchanger.write(msg)

def wait_to_clear(num_twos : int):
    while True:
        with open(_exchanger_file_name, "r") as exchanger:
            txt = exchanger.read().removesuffix("\n")
            if txt.endswith("2"*num_twos):
                break
        time.sleep(0.001)
    with open(_exchanger_file_name, "w") as exchanger:
        pass"""