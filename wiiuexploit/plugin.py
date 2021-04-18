import os, socket
import tkinter as tk
from http.server import HTTPServer, BaseHTTPRequestHandler
from gui.widgets import basePlugin, basePage
from asyncthreader import threader
import style

# print(socket.gethostbyname(socket.gethostname()))

ABOUT = """HTTP server is running in background.
Go to http://{}:8000/ on the WiiU browser while 
connected to the same wifi network as this device 
and click the button on the webpage to launch the exploit."""

def get_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# doesn't even have to be reachable
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except Exception as e:
		print(e)
		raise
	finally:
		s.close()
	return IP

class Serv(BaseHTTPRequestHandler):
	def do_GET(self):
		print("received get request")
		self.do_send_file(os.path.join(os.path.dirname(__file__), 'index.html'))

	def do_POST(self):
		print("received post request")
		self.do_send_file(os.path.join(os.path.dirname(__file__), 'payloads/payload.html'))

	def do_send_file(self, file):	
		try:
			filepath = os.path.join(os.path.dirname(__file__), file)
			print(f"Sending {filepath}")
			file_to_open = open(filepath).read()
			self.send_response(200)
		except Exception as e:
			print(e)
			file_to_open = "File not found"
			self.send_response(404)
		self.end_headers()
		self.wfile.write(bytes(file_to_open, 'utf-8'))

class Page(basePage.BasePage):
	def __init__(self, app, container, plugin):
		basePage.BasePage.__init__(self, app, container, "WiiU ~ Exploit")
		self.plugin = plugin
		
		self.about_label = tk.Label(self, text = ABOUT.format(get_ip()), background = style.secondary_color, font = style.smalltext, foreground = style.secondary_text_color)
		self.about_label.place(relx = 0.5, rely = 0.5, width = 500, height = 400, y = - 200, x = - 250)

class Plugin(basePlugin.BasePlugin):
	def __init__(self, app, container):
		basePlugin.BasePlugin.__init__(self, app, "WiiUExploit", container)
		self.app = app
		self.container = container
		#replace the "localhost" with your iPv4
		self.server =  HTTPServer((get_ip(), 8000), Serv)
		print("Server is Running :)")
		threader.do_async(self.server.serve_forever)

	def get_pages(self):
		return [Page(self.app, self.container, self)]

	def exit(self):
		self.server.server_close()

def setup(app, container):
	return Plugin(app, container)
