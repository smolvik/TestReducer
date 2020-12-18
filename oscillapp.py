#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from dialogapp import DialogApp

class OscillApp(DialogApp):
	
	def __init__(self, parent, title, prc):
		print('OscillApp')
		DialogApp.__init__(self, parent, title, prc)
		self.buf=0

	def initUI(self):
		frame = tkinter.Frame(self.parent)
		frame.pack()

		w=500
		h=375
		self.w=w
		self.h=h
		
		self.paintArea = tkinter.Canvas(frame, width = w, height=h, bg='black')
		self.paintArea.pack(padx=5, pady=5)

		self.paintArea.create_line(0, h/2, w, h/2, fill='white')
		
		self.quitButton = tkinter.Button(frame, text = 'Quit', width = 25, command = self.parent.withdraw)
		self.quitButton.pack()
				
	def setupBuf(self, buf, nmax):
		self.buf=buf
		self.nmax = nmax
		
	def update(self):
		self.paintArea.delete('all')
		
		tmax = self.nmax
		if tmax <= 1:
			return
		
		t = 0		
		x0 = 0
		x = x0
		y0 = self.h/2*(1-self.buf[0])
		for y in self.buf:
			x = t*self.w/(tmax-1)
			y = self.h/2*(1-y)
			self.paintArea.create_line(x0, y0, x, y, fill='red')
			x0 = x
			y0 = y
			t += 1
