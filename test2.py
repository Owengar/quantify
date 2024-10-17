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
        print("in use")
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

open_browser(port)
