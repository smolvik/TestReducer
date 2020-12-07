#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
import math
import time
import threading
from mainapp import MainApp
import hashlib
import os

bufSig = 0
mainApp = 0

class BufSig():
	def __init__(self):
		self.buf = []
		t=0.0
		tmax=10
		f=0.2
		td = 100e-3
		while t <= tmax:
			self.buf.append(math.sin(2*math.pi*f*t))
			t += td
			
		self.t = t
		self.td = td
		self.f = f

	def update(self):
		self.buf.pop(0)
		self.buf.append(math.sin(2*math.pi*self.f*self.t))
		self.t += self.td

def timerLoop(args):
	global bufSig
	global mainApp
	
	while args['mode'] != 0:
		#time.sleep(1)
		#print(args)
		if args['mode'] == 1:
			print('timer idle')
			time.sleep(1)
			continue
			
		if args['mode'] == 2:
			for i in range(100):
				print('update timer')
				bufSig.update()
				mainApp.oscillApp1.update()
				mainApp.oscillApp2.update()
				mainApp.setupApp.update(i)
				mainApp.monitorApp.update(i)
				time.sleep(1)
			mainApp.setupApp.update(100)

		
def main():
	global bufSig
	global mainApp
	
	bufSig = BufSig()

	root = tkinter.Tk()	
	mainApp = MainApp(root)
	mainApp.oscillApp1.setupBuf(bufSig.buf)
	mainApp.oscillApp2.setupBuf(bufSig.buf)
	
	thrTimer = threading.Thread(target=timerLoop, args=(mainApp.setupApp.timerFlag,), daemon=True)
	thrTimer.start()
	
	root.mainloop()
	
	mainApp.setupApp.timerFlag['mode'] = 0
	thrTimer.join()

if __name__ == '__main__':
	main()
