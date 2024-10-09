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
    global my_oned_id, settables_labels, color_label, dataset
    my_oned_id = int(fig_data.readline().removesuffix("\n"))
    settables_labels = json.loads(fig_data.readline())
    color_label = fig_data.readline().removesuffix("\n")
    dataset = xarray.Dataset.from_dict(json.loads(fig_data.readline()))

while os.path.exists(_process_exchange._find_signal_path("fig_1d_data.txt")):
    try:
        os.remove(_process_exchange._find_signal_path("fig_1d_data.txt"))
    except:
        pass


nan_type = dataset.dim_0.data[-1]

other_coords = list(dataset.coords)
other_coords.pop(my_oned_id)
end_signal = False

setpoints = {}
for settable in dataset.coords:
    setpoints[settable] = numpy.unique(dataset.get(settable).data)
setpoints_shape = [len(setpoints[i]) for i in setpoints]
settables_names = list(dataset.coords._names)



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


fig = go.Figure()
for coord in other_coords:
    for i in setpoints.get(coord):
        fig.add_trace(
                go.Scattergl(
                    x=dataset.get(settables_labels[my_oned_id]).data,
                    y=dataset.where(dataset.get(coord) == i).get(color_label).data
                )
        )
    #fig = px.scatter(dataset, x=settables_labels[my_oned_id], y=color_label, color=coord, markers=True, render_mode="webgl")


app = Dash()
app.layout = html.Div([
dcc.Graph(figure=fig, id="live-update-graph"),
dcc.Interval(
        id='interval-component',
        interval=1000, # in milliseconds
        n_intervals=0
    )
])


times = open(f"times{my_oned_id}", "w")

@callback(Output('live-update-graph', 'figure'),
            Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global end_signal, dataset

    if end_signal:
        pass
        #os.abort()
    if not os.path.exists(_process_exchange._get_proc_exchange_dir()):
        os.abort()
    _process_exchange._make_signal_file("update_data")
    while _process_exchange._wait_for_signal("update_data", break_condition=true, delete_on_detection=False):
        pass
    
    read_new()
    #fig = go.Figure()
    for other_coord in other_coords:
        start = time.time()
        """ for i in setpoints.get(coord):
            fig.add_trace(
                    go.Scattergl(
                        x=dataset.get(settables_labels[my_oned_id]).data,
                        y=dataset.where(dataset.get(coord) == i).get(color_label).data,
                        name=f"{coord} = {i}"

                    )
            ) """
        #print(color_label)
        #print(dataset.get(other_coord).where(dataset.get(color_label) > 0).data.reshape(setpoints_shape))
        fig = px.imshow(dataset.get(other_coord).where(dataset.get(color_label)/dataset.get(color_label) == 1).data.reshape(setpoints_shape), origin="lower")
        #fig = px.scatter(dataset, x=settables_labels[my_oned_id], y=color_label, color=coord, markers=True, render_mode="webgl")
        end = time.time()
        times.write(str(end-start) + "\n")
        times.flush()
    fig = fig.update_xaxes(title_text=settables_labels[my_oned_id])
    fig = fig.update_yaxes(title_text=color_label)
    if not (dataset.dim_0.data[-1] is nan_type):
        _process_exchange._make_signal_file(f"done_1d_{my_oned_id}")
        end_signal = True


    return fig


app.title = "hello?!"










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
app.run(port=str(port))