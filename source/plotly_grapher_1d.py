from dash import Dash, dcc, html, Input, Output, callback
from imports import *
import _process_exchange as _process_exchange
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser



def true():
    return True



with open(_process_exchange._find_signal_path("fig_1d_data.txt"), "r") as fig_data:
    global oned_id, x_label, y_label, color_label, dataset
    my_oned_id = int(fig_data.readline().removesuffix("\n"))
    x_label = fig_data.readline().removesuffix("\n")
    y_label = fig_data.readline().removesuffix("\n")
    color_label = fig_data.readline().removesuffix("\n")
    dataset = xarray.Dataset.from_dict(json.loads(fig_data.readline()))
time.sleep(5)
os.remove(_process_exchange._find_signal_path("fig_1d_data.txt"))


other_coords = []
for i,coord in enumerate(dataset.coords._names):
    if i == my_oned_id:
        continue
    other_coords.append(coord)
end_signal = False


def read_new():
    global oned_id, x_label, y_label, color_label, dataset
    while True:
        try:
            with open(_process_exchange._find_signal_path("fig_1d_data.txt"), "r") as fig_data:
                global x_label, y_label, color_label, x_setpoints, y_setpoints, darray, dataset
                dataset = xarray.Dataset.from_dict(json.loads(fig_data.readline()))
            break
        except:
            continue



for coord in other_coords:
    fig = px.line(dataset, x=x_label, y=color_label, color=coord, markers=True)


app = Dash()
app.layout = html.Div([
dcc.Graph(figure=fig, id="live-update-graph"),
dcc.Interval(
        id='interval-component',
        interval=1000, # in milliseconds
        n_intervals=0
    )
])


@callback(Output('live-update-graph', 'figure'),
            Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global end_signal, dataset

    if end_signal:
        os.abort()
    if not os.path.exists(_process_exchange._get_proc_exchange_dir()):
        os.abort()
    _process_exchange._make_signal_file("update_data")
    while _process_exchange._wait_for_signal("update_data", break_condition=true, delete_on_detection=False):
        pass
    
    read_new()
    for coord in other_coords:
        fig = px.line(dataset, x=x_label, y=color_label, color=coord, markers=True)

    return fig


_process_exchange._make_signal_file("first_read")
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
    httpd = HTTPServer(('localhost',port),Serv)
    httpd.timeout = 2.0
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