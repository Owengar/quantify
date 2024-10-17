from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
from source.imports import *

from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser


from source.imports import *
import threading








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
        file_to_open = fig.to_html(post_script="function replacer() {try{document.open(); fetch(\"http://localhost:"+str(port)+"\").then((response) => response.text()).then((text) => document.write(text)); document.close();} catch (error) {console.log(\"skip\")} } setTimeout(function(){replacer();},2000);")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
    def do_POST(self):
        global httpd
        httpd.occupied = True

port = 8050
httpd = HTTPServer(('localhost',port),Serv)



def start_handling():
    while True:
        httpd.handle_request()
i=0

t1 = threading.Thread(target = start_handling)
t1.start()
while True:
    fig = go.Figure()
    fig.add_scattergl(x=numpy.arange(i), y=numpy.arange(i))
    if i < 1001:
        i += 1
        time.sleep(0.01)