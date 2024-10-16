from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
from imports import *
import _process_exchange as _process_exchange
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser



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
    name = fig_data.readline()

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
setpoints_shape = [len(setpoints[i]) for i in setpoints]



def read_new():
    global oned_id, settables_labels, color_label, dataset
    while True:
        try:
            with open(_process_exchange._find_signal_path("fig_1d_data.txt"), "r") as fig_data:
                global settables_labels, color_label, x_setpoints, y_setpoints, darray, dataset
                dataset = xarray.Dataset.from_dict(json.loads(fig_data.readline()))
            break
        except:
            continue

"""
fig = go.Figure()
for other_coord in other_coords:
    start = time.time()
    for i in setpoints.get(other_coord):
        fig.add_trace(
                go.Scattergl(
                    x=setpoints[all_coords[my_oned_id]],
                    #y=dataset.where(dataset.get(other_coord) == i).get(color_label).data,
                    y=dataset.where(dataset.get(other_coord) == i).get(color_label).dropna("dim_0"),
                    name=f"{other_coord} = {i}"
                )
        )
fig = fig.update_xaxes(title_text=all_coords[my_oned_id])
fig = fig.update_yaxes(title_text=color_label)
"""



data = []
for other_coord in other_coords:
    for setpoint in setpoints.get(other_coord):
        data.append({"mode" : "lines+markers", 'marker' : {"size" : 10}, 'name' : f"{other_coord} = {setpoint}", 'x': [], 'y': []})
app = Dash()
app.layout = html.Div([
dcc.Graph(figure={'layout': {'title': name,
                               'barmode': 'overlay', "xaxis" : {"title" : {"text" : all_coords[my_oned_id]}}, "yaxis" : {"title" : {"text" : color_label}}},
                    'data': data


                    }, id="graph-extendable"),
dcc.Interval(
        id='interval-component',
        interval=1000, # in milliseconds
        n_intervals=0
    )
])





start_index = [0]
latest_index = [len(dataset.get(color_label).dropna("dim_0"))]
queue = {"x" : [], "y" : []}




@callback(Output('graph-extendable', 'extendData'),
            Input('interval-component', 'n_intervals'))
def update_graph_live(n):
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
    latest_index[0] = len(dataset.get(color_label).dropna("dim_0"))
    fig_dict = {"x" : [], "y" : []}
    #getpoints_total = list(dataset.get(color_label).data)
    getpoints_total_n = dataset.get(color_label).data
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


class Serv(BaseHTTPRequestHandler):

    def do_GET(self):
        file_to_open = "File not found"
        self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
    def do_POST(self):
        global httpd
        httpd.occupied = True

port = 8050
while True:
    if is_port_in_use(port):
        print("in use")
        port -= 1
        continue
    httpd = HTTPServer(('localhost',port),Serv)
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

open_browser(port)
app.run(port=str(port), dev_tools_silence_routes_logging=True)