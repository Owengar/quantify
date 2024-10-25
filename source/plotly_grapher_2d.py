from dash import Dash, dcc, html, Input, Output, callback
from imports import *
import _process_exchange as _process_exchange
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import plotly.graph_objects as go







with open(_process_exchange._find_signal_path("fig_2d_data.txt"), "r") as fig_data:
    global x_label, y_label, color_label, x_setpoints, y_setpoints, darray, name
    x_label = fig_data.readline().removesuffix("\n")
    y_label = fig_data.readline().removesuffix("\n")
    color_label = fig_data.readline().removesuffix("\n")
    x_setpoints = json.loads(fig_data.readline())
    y_setpoints = json.loads(fig_data.readline())
    darray = json.loads(fig_data.readline())
    setpoints_shape = json.loads(fig_data.readline())[::-1]
    name = fig_data.readline()

end_signal = False
nan_type = darray[-1]

def true():
    return True

def read_new():
    while True:
        try:
            with open(_process_exchange._find_signal_path("fig_2d_data.txt"), "r") as fig_data:
                global x_label, y_label, color_label, x_setpoints, y_setpoints, darray
                slice = json.loads(fig_data.readline())
                darray[slice[0]:slice[1]] = json.loads(fig_data.readline())
            break
        except:
            continue


fig = px.imshow(numpy.array(darray).reshape(setpoints_shape), origin="lower", labels={"x" : x_label, "y" : y_label, "color" : color_label}, x=x_setpoints, y=y_setpoints, aspect="auto")

fig.update_layout({"title" : name})
app = Dash()
app.layout = html.Div([
dcc.Graph(figure=fig, id="live-update-graph"),
dcc.Interval(
        id='interval-component',
        interval=2000, # in milliseconds
        n_intervals=0
    )
])


#times = open("times.txt", "a")
old = time.time()
@callback(Output('live-update-graph', 'figure'),
            Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global old, end_signal

    if end_signal:
        os.abort()
    if not os.path.exists(_process_exchange._get_proc_exchange_dir()):
        os.abort()
    _process_exchange._make_signal_file("update_data_2d")
    while os.path.exists(_process_exchange._find_signal_path("update_data_2d")):
        pass
    
    old = time.time()
    read_new()
    now = time.time()
    fig = px.imshow(numpy.array(darray).reshape(setpoints_shape), origin="lower", labels={"x" : x_label, "y" : y_label, "color" : color_label}, x=x_setpoints, y=y_setpoints, aspect="auto")

    if not (darray[-1] is nan_type):
        end_signal = True
    

    fig.update_layout({"title" : name})
    return fig


_process_exchange._make_signal_file("first_read")
app.title = "Plotly 2D Window"








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
def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0



port = 8050
while True:
    if is_port_in_use(port):
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