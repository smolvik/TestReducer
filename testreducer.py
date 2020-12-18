#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
import math
import time
import threading
from mainapp import MainApp
import hashlib
import os
import select
import socket
import math

bufSig = 0
mainApp = 0

servIP = '127.0.0.1'
servPort = 48801

cliIP = '127.0.0.1'
cliPort = 48801

class BufSig():
	def __init__(self):
		self.buf = []
		t=0.0
		tmax=10
		f=0.2
		td = 100e-3
		#while t <= tmax:
			#self.buf.append(math.sin(2*math.pi*f*t))
			#self.buf.append(0.0)
			#t += td
			
		self.t = t
		self.td = td
		self.f = f
		self.tmax=tmax
		self.sz = int(tmax/td)
		
	def __str__(self):
		return 'hello from BufSig'
		
	def __repr__(self):
		return 'It is a class BufSig'

	# ~ def update(self):
		# ~ if self.t >= self.tmax:
			# ~ self.buf.pop(0)
		# ~ self.buf.append(math.sin(2*math.pi*self.f*self.t))
		# ~ self.t += self.td
		
	def update(self, x):
		if self.t >= self.tmax:
			self.buf.pop(0)
		self.buf.append(x)
		self.t += self.td

def timerLoop(args):
	global bufSig
	global mainApp
	
	nc = 0
	cc = 0
	perc_cyc = 0
	perc_all = 0
	monpar = {}
	dper = 0
	cr = 0
	nr = 0
	sumrot = 0
	speed = 0
	maxtorque = 0.0
	curtor = 0.0
	
	# create datagram socket
	udpsock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
	# bind socket to port
	udpsock.bind(('', cliPort))
	# connect udp to remote address
	udpsock.connect((servIP, servPort))	

	while True:
		#time.sleep(.1)
		readable, writable, exceptional = select.select([udpsock], [], [], 0.1)
		#print('loop select')
		
		cmd = {}
		if mainApp.setupApp.cmdQueue:
			cmd = mainApp.setupApp.cmdQueue.pop(0)
			
		if cmd.get('cmd') == mainApp.setupApp.CmdEnum.EXIT:
			return

		if cmd.get('cmd') == mainApp.setupApp.CmdEnum.START:
			nc = cmd['numcyc']
			cc = 0
			perc_all = 0
			perc_cyc = 0
			nr = cmd['numrot_in']
			cr = 0
			sumrot = 0
			speed = cmd['speed_in']
			maxtorque = cmd['max_torque_out']
			cyclo = cmd['cyclo']
			mainApp.updateLogMsg('Испытание запущено\n')
			
		if cmd.get('cmd') == mainApp.setupApp.CmdEnum.STOP:
			nc = 0
			mainApp.updateLogMsg('Испытание остановлено\n')

		if nc:
			if cr < nr:
				#print('cycle loop {}'.format(cr))
				cr += 1
				sumrot += 1
				perc_cyc = int(100*cr/nr)
				
				x = 100*cr/nr
				for i in range(5):
					if x <= cyclo[i][0]:
						x1 = cyclo[i-1][0]
						x2 = cyclo[i][0]
						y1 = cyclo[i-1][1]
						y2 = cyclo[i][1]
						curtor = y1+(y2-y1)*(x-x1)/(x2-x1)
						break
				
				bufSig.update(curtor/100.0)
				mainApp.oscillApp1.update()
				mainApp.oscillApp2.update()

			else:
				mainApp.updateLogMsg('Цикл {} завершен\n'.format(cc+1))
				cc += 1
				perc_all = int(100*cc/nc)
				cr = 0
				if cc >= nc:
					mainApp.updateLogMsg('Испытание завершено\n')
					nc = 0
					cr = nr
			mainApp.monitorApp.update([perc_cyc, perc_all, sumrot, maxtorque, speed, sumrot, maxtorque, speed])

def main():
	global bufSig
	global mainApp
	
	bufSig = BufSig()

	root = tkinter.Tk()	
	mainApp = MainApp(root)
	mainApp.oscillApp1.setupBuf(bufSig.buf, bufSig.sz)
	mainApp.oscillApp2.setupBuf(bufSig.buf, bufSig.sz)
	
	thrTimer = threading.Thread(target=timerLoop, args=(mainApp.setupApp.timerFlag,), daemon=True)
	thrTimer.start()
	#threading.get_ident()
	
	root.mainloop()
	
	mainApp.setupApp.cmdQueue.append({'cmd':mainApp.setupApp.CmdEnum.EXIT})
	thrTimer.join()

if __name__ == '__main__':
	main()
