from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
from imports import *
import _process_exchange as _process_exchange
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading



def true():
    return True
def is_nan(other_coord):
    def not_nan(dset):
        print(dataset.get(other_coord).where(dataset.get(color_label) > numpy.nan))
        return dataset.get(other_coord).where(dataset.get(color_label) > numpy.nan)
    return not_nan


with open(_process_exchange._find_signal_path("fig_1d_data.txt"), "r") as fig_data:
    global my_oned_id, settables_labels, color_label, dataset, name
    my_oned_id = int(fig_data.readline().removesuffix("\n"))
    settables_labels = json.loads(fig_data.readline())
    color_label = fig_data.readline().removesuffix("\n")
    dataset = xarray.Dataset.from_dict(json.loads(fig_data.readline()))
    name = fig_data.readline().removesuffix("\n")
    data_store_path = fig_data.readline().removesuffix("\n")
    parent_pid = int(fig_data.readline().removesuffix("\n"))

while os.path.exists(_process_exchange._find_signal_path("fig_1d_data.txt")):
    try:
        os.remove(_process_exchange._find_signal_path("fig_1d_data.txt"))
    except:
        pass


nan_type = dataset.dim_0.data[-1]

all_coords = settables_labels.copy()
other_coords = settables_labels.copy()
other_coords.remove(settables_labels[my_oned_id])
end_signal = False

setpoints = {}
for settable in settables_labels.copy():
    setpoints[settable] = numpy.unique(dataset.get(settable).data)
setpoints_shape = [len(setpoints[i]) for i in settables_labels]


pov_setpoints = {}

my_label = settables_labels[my_oned_id]
shifted_labels = settables_labels.copy()
while shifted_labels[0] != my_label:
    shifted_labels = shifted_labels[1:] + shifted_labels[:1]
for settable in shifted_labels:
    pov_setpoints[settable] = numpy.unique(dataset.get(settable).data)
pov_setpoints_shape = [len(pov_setpoints[i]) for i in shifted_labels]










def save_image_and_html(data_store_path, fig : go.Figure):
    fig.write_html(data_store_path + f"\\HTML  -  {settables_labels[my_oned_id]} with {color_label}  -  {name}.html")
    fig.write_image(data_store_path + f"\\Image  -  {settables_labels[my_oned_id]} with {color_label}  -  {name}.png", format="png", width=1050, height=750, scale=1)




def read_new():
    global oned_id, settables_labels, color_label, dataset
    while True:
        try:
            with open(_process_exchange._find_signal_path("fig_1d_data.txt"), "r") as fig_data:
                global settables_labels, color_label, x_setpoints, y_setpoints, darray, dataset
                dataset = xarray.Dataset.from_dict(json.loads(fig_data.readline()))
            break
        except:
            if not os.path.exists(_process_exchange._get_proc_exchange_dir()):
                save_image_and_html(data_store_path, fig)
                os.abort()
            continue




def close_procedure(fig):
    save_image_and_html(data_store_path, fig)
    os.abort()





data = []

for i in setpoints[settables_labels[my_oned_id]]:
    data.append({"mode" : "lines+markers", 'marker' : {"size" : 10}, 'x': [], 'y': []})
""" 
for other_coord in other_coords:
    for setpoint in setpoints.get(other_coord):
        data.append({"mode" : "lines+markers", 'marker' : {"size" : 10}, 'name' : f"{other_coord} = {setpoint}", 'x': [], 'y': []})
 """


app = Dash()
app.layout = html.Div([
dcc.Graph(figure={'layout': {'title': name,
                               'barmode': 'overlay', "xaxis" : {"title" : {"text" : all_coords[my_oned_id]}}, "yaxis" : {"title" : {"text" : color_label}}},
                    'data': data


                    }, id="graph-extendable"),
dcc.Interval(
        id='interval-component',
        interval=3500, # in milliseconds
        n_intervals=0
    )
])


sorted_getpoints = dataset.sortby(settables_labels[my_oned_id]).get(color_label)
start_index = [numpy.where(numpy.isnan(sorted_getpoints.data), False, True)]
latest_index = [len(dataset.get(color_label).dropna("dim_0"))]
queue = {"x" : [], "y" : []}




@callback(Output('graph-extendable', 'extendData'),
            Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    return
    global end_signal, dataset

    if end_signal:
        os.abort()
    if not os.path.exists(_process_exchange._get_proc_exchange_dir()):
        os.abort()
    _process_exchange._make_signal_file("update_data_1d")
    while os.path.exists(_process_exchange._find_signal_path("update_data_1d")):
        pass

    read_new()

    start = time.time()
    fig_dict = {"x" : [], "y" : []}
    getpoints_total_n = dataset.get(color_label).data





    my_setpoints_length = len(setpoints[settables_labels[my_oned_id]])
    my_setpoints = setpoints[settables_labels[my_oned_id]]
    print()
    print(my_oned_id)
    print(settables_labels[my_oned_id])
    sorted_getpoints = dataset.sortby(settables_labels[my_oned_id]).get(color_label)
    sorted_shaped_getpoints = sorted_getpoints.data.reshape(pov_setpoints_shape)

    latest_index[0] = numpy.where(numpy.isnan(sorted_getpoints.data), False, True)

    mask_diff = (start_index[0] != latest_index[0]).reshape(pov_setpoints_shape)

    trimmed_sorted_shaped_getpoints = numpy.where(mask_diff == True, sorted_shaped_getpoints, numpy.nan)
    for i, all_where in enumerate(trimmed_sorted_shaped_getpoints):
        flattened = numpy.ravel(all_where)
        flattened = flattened[~numpy.isnan(flattened)]
        fig_dict["x"].append([my_setpoints[i]] * len(flattened))
        fig_dict["y"].append(flattened)
        queue["x"].extend([my_setpoints[i]] * len(flattened))
        queue["y"].extend(flattened)



    start_index[0] = latest_index[0]

    if not (True in dataset.get(color_label).isnull().data):
        #_process_exchange._make_signal_file(f"done_1d_{my_oned_id}")
        fig = go.Figure()
        fig.add_scattergl(go.Scattergl(
                        x=queue["x"][0],
                        y=queue["y"][0],
                    ))
        fig.show()
        end_signal = True

    #print(fig_dict)
    
    return None

    for other_coord in other_coords:
        other_coord_setpoints_total = dataset.get(other_coord).data
        #other_empty = [numpy.nan for i in range(len(other_coord_setpoints_total))]
        #other_empty_y = other_empty.copy()
        my_setpoints_total_n = dataset.get(settables_labels[my_oned_id]).data

        uniqued_setpoints, indices = numpy.unique(other_coord_setpoints_total, return_inverse=True, equal_nan=True)
        
        for i,other_setpoint in enumerate(setpoints.get(other_coord)):
            """ fig.add_trace(
                    go.Scattergl(
                        x=setpoints[all_coords[my_oned_id]],
                        y=dataset.where(dataset.get(other_coord) == i).get(color_label).dropna("dim_0"),
                        name=f"{other_coord} = {i}",
                    )
            ) """
            #fig_dict["x"].append(dataset.get(settables_labels[my_oned_id]).where(dataset.get(other_coord) == i).data[start_mask[0][1] : latest_mask[0][1]])
            #fig_dict["y"].append(dataset.get(color_label).where(dataset.get(settables_labels[my_oned_id]).where(dataset.get(other_coord) == i)).data[start_mask[0][1] : latest_mask[0][1]])

            """ 
            other_coord_setpoints_total = list(dataset.get(other_coord).data)
            other_empty = [numpy.nan for i in range(len(other_coord_setpoints_total))]
            other_empty_y = other_empty.copy()
            my_setpoints_total = list(dataset.get(settables_labels[my_oned_id]).data)
            if other_coord_setpoints_total.count(other_setpoint) > 1:
                first_index = other_coord_setpoints_total.index(other_setpoint)
                second_index = other_coord_setpoints_total.index(other_setpoint, first_index+1)
                index_diff = second_index-first_index
                for i in range(other_coord_setpoints_total.count(other_setpoint)):
                    other_empty[first_index + (index_diff * i)] = my_setpoints_total[first_index + (index_diff * i)]
                    other_empty_y[first_index + (index_diff * i)] = getpoints_total[first_index + (index_diff * i)]
            else:
                other_empty[other_coord_setpoints_total.index(other_setpoint)] = my_setpoints_total[other_coord_setpoints_total.index(other_setpoint)]
                other_empty_y[other_coord_setpoints_total.index(other_setpoint)] = getpoints_total[other_coord_setpoints_total.index(other_setpoint)] """
            index = numpy.where(uniqued_setpoints == other_setpoint)
            index = numpy.ravel(index)[0]
            x_graphpoints = numpy.where(indices == index, my_setpoints_total_n, numpy.nan)[start_index[0]:latest_index[0]]
            x_graphpoints = x_graphpoints[~numpy.isnan(x_graphpoints)]
            y_graphpoints = numpy.where(indices == index, getpoints_total_n, numpy.nan)[start_index[0]:latest_index[0]]
            y_graphpoints = y_graphpoints[~numpy.isnan(y_graphpoints)]



            #fig_dict["x"].append(dataset.get(settables_labels[my_oned_id]).where(dataset.get(other_coord) == other_setpoint).data[start_index[0]:latest_index[0]])
            #fig_dict["x"].append(x_graphpoints.tolist())
            #fig_dict["y"].append(dataset.get(color_label).where(dataset.get(other_coord) == other_setpoint).data[start_index[0]:latest_index[0]])
            #fig_dict["y"].append(y_graphpoints.tolist())
            if start_index[0] != latest_index[0] or True:
                fig_dict["x"].append(x_graphpoints.tolist())
                fig_dict["y"].append(y_graphpoints.tolist())

            

    start_index[0] = latest_index[0]

    #print(queue)
    #queue_bite = {"x" : [i[0:2] for i in queue["x"]], "y" : [i[0:2] for i in queue["y"]]}
    #[i.__delitem__(slice(0, 2)) for i in queue["x"]]
    #[i.__delitem__(slice(0, 2)) for i in queue["y"]]


    end = time.time()
    print("1d lap")
    print(end-start)


    if not (True in dataset.get(color_label).isnull().data):
        #_process_exchange._make_signal_file(f"done_1d_{my_oned_id}")
        end_signal = True

    return fig_dict

app.title = "Plotly 1D Window"
















fig = go.Figure()
def update_graph():
    global end_signal, dataset, running_post_script, fig


    if not psutil.pid_exists(parent_pid):
        running_post_script = finished_post_script
        end_signal = True
        try: 
            _process_exchange._del_exchange_dir()
        except:
            pass
        return fig
    _process_exchange._make_signal_file("update_data_1d")
    while os.path.exists(_process_exchange._find_signal_path("update_data_1d")):
        pass

    read_new()

    #fig_dict = {"x" : [], "y" : []}
    #getpoints_total_n = dataset.get(color_label).data
    #my_setpoints_length = len(setpoints[settables_labels[my_oned_id]])
    my_setpoints = setpoints[settables_labels[my_oned_id]]
    #print()
    #print(my_oned_id)
    #print(settables_labels[my_oned_id])
    sorted_getpoints = dataset.sortby(settables_labels[my_oned_id]).get(color_label)
    sorted_setpoints = dataset.sortby(settables_labels[my_oned_id]).get(settables_labels[my_oned_id])

    latest_index[0] = numpy.where(numpy.isnan(sorted_getpoints.data), False, True)




    if my_oned_id == 0:
        sorted_shaped_setpoints = sorted_setpoints.data.reshape(pov_setpoints_shape[::-1], order="F")
        sorted_shaped_getpoints = sorted_getpoints.data.reshape(pov_setpoints_shape[::-1], order="F")
        mask_diff = (start_index[0] != latest_index[0]).reshape(pov_setpoints_shape[::-1], order="F")
        trimmed_sorted_shaped_getpoints = numpy.where(mask_diff == True, sorted_shaped_getpoints, numpy.nan)
        trimmed_sorted_shaped_setpoints = numpy.where(mask_diff == True, sorted_shaped_setpoints, numpy.nan)
        if len(settables_labels) > 1:
            for i, getpoints in enumerate(trimmed_sorted_shaped_getpoints):
                fig.add_scattergl(
                                x=trimmed_sorted_shaped_setpoints[i],
                                y=getpoints,
                                mode="lines+markers",
                                
                            )
        else:
            fig = go.Figure()
            fig.add_scattergl(
                                x=sorted_shaped_setpoints,
                                y=sorted_shaped_getpoints,
                                mode="lines+markers",
                            )
        """  for i, all_where in enumerate(trimmed_sorted_shaped_getpoints):
            flattened = numpy.ravel(all_where)
            flattened = flattened[~numpy.isnan(flattened)]
            fig.add_scattergl(
                        x=[my_setpoints[i]] * len(flattened),
                        y=flattened,
                        mode="lines+markers",
                        
                    )"""
    else:
        sorted_shaped_getpoints = sorted_getpoints.data.reshape(pov_setpoints_shape)
        mask_diff = (start_index[0] != latest_index[0]).reshape(pov_setpoints_shape)
        trimmed_sorted_shaped_getpoints = numpy.where(mask_diff == True, sorted_shaped_getpoints, numpy.nan)
        for i, all_where in enumerate(trimmed_sorted_shaped_getpoints):
            flattened = numpy.ravel(all_where)
            flattened = flattened[~numpy.isnan(flattened)]
            fig.add_scattergl(
                        x=[my_setpoints[i]] * len(flattened),
                        y=flattened,
                        mode="lines+markers")
                        
    fig.update_xaxes(title_text=all_coords[my_oned_id])
    fig.update_yaxes(title_text=color_label)
    fig.update_layout({"title" : name})
    fig.update_layout(showlegend=False) 

    start_index[0] = latest_index[0]
    if not (True in dataset.get(color_label).isnull().data):
        running_post_script = finished_post_script
        end_signal = True
    return fig










def open_browser(port):
    browser = None

    using = None
    if using is None:
        browser = webbrowser.get(None)
    else:
        if not isinstance(using, tuple):
            using = (using,)
        for browser_key in using:
            try:
                browser = webbrowser.get(browser_key)
                if browser is not None:
                    break
            except webbrowser.Error:
                pass

        if browser is None:
            raise ValueError("Can't locate a browser with key in " + str(using))
    browser.open(f"http://127.0.0.1:{port}")
def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
class listener_checker(BaseHTTPRequestHandler):

    def do_GET(self):
        global httpd
        httpd.occupied = True
    def do_POST(self):
        global httpd
        httpd.occupied = True
port = 8050
while True:
    if is_port_in_use(port):
        port -= 1
        continue
    httpd = HTTPServer(('localhost',port),listener_checker)
    httpd.timeout = 3.0
    httpd.occupied = False
    httpd.handle_request()
    if httpd.occupied:
        port -= 1
        continue
    else:
        httpd.server_close()
        del httpd
        break


finished_post_script = "function poster() {fetch(\"http://localhost:"+str(port)+"\", {method: \"POST\"}); setTimeout(function(){poster();},100);} poster();"
"function poster() {fetch(\"http://localhost:"+str(port)+"\", {method: \"POST\"}); setTimeout(function(){poster();},2000);} "
"function replacer() {try{document.open(); fetch(\"http://localhost:"+str(port)+"\").then((response) => response.text()).then((text) => document.write(text)); document.close();} catch (error) {console.log(\"skip\")} } setTimeout(function(){replacer();},2000);"
running_post_script = "setTimeout(function(){window.location.reload();},2000);"

def blank(code):
    pass
class Serv(BaseHTTPRequestHandler):
    def do_GET(self):
        global running_post_script
        self.log_request = blank
        fig = update_graph()
        file_to_open = fig.to_html(post_script=running_post_script)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
    def do_POST(self):
        global httpd
        httpd.occupied = True

httpd = HTTPServer(('localhost',port),Serv)



def start_handling():
    global end_signal
    while True:
        httpd.handle_request()
        if end_signal:
            close_procedure(fig)
i=0

t1 = threading.Thread(target = start_handling)
t1.start()
open_browser(port)
while True:
    time.sleep(0.01)
    if not t1.is_alive():
        sys.exit()
        os.abort()