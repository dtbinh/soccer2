#!/usr/bin/env python

# this works but seems highly inefficient ... my system runs 80% w/ 2 cores
# just displaying a static web page
# although this might be the page --- canvas and two.js???

# for the webserver
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from socket import gethostname, gethostbyname
import time

# for the server/client interface
import multiprocessing as mp
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import lib.zmqclass as zmq


class Kludge(mp.Process):
	"""
	This listens to zmq and passes into between zmq and the client webpage
	"""
	def __init__(self, topics, host="localhost", port=9000):
		mp.Process.__init__(self)
		self.host = host
		self.port = port

	def __del__(self):
		print 'Kludge says goodbye'

	def run(self):
		self.sub = zmq.Sub(['voice'])

		while True:
			time.sleep(3)
			msg = self.sub.recv()
			if msg:
				print msg


PORT = 8800

# take a look at websockets:
# https://github.com/liris/websocket-client


class GetHandler(BaseHTTPRequestHandler):
	@staticmethod
	def page():
		fd = open('node/head/face.htm', 'r')
		results = fd.read()
		fd.close()
		return results

	def do_GET(self):
		print 'Processing request: {0!s}'.format(self.path)
		if self.path == '/':
			response = self.page()
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(response)
		else:
			print "GetHandler doesn't support {0!s}".format(self.path)
			self.send_response(404)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>')
			self.wfile.write('<h1>File not found</h1>')
			self.wfile.write('</body></html>')


if __name__ == '__main__':

	ipaddr = gethostbyname(gethostname())

	k = Kludge()
	k.start()

	print 'Starting server on ' + str(ipaddr) + ':' + str(PORT) + ', use <Ctrl-C> to stop'
	server = HTTPServer(('0.0.0.0', PORT), GetHandler)
	server.serve_forever()

	k.join()
