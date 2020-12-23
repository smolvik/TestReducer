#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from dialogapp import DialogApp
import math


class OscillApp(DialogApp):
	
	def __init__(self, parent, title, prc):
		print('OscillApp')
		
		self.buf1 = []
		self.buf2 = []
		self.ncur=0
		self.nmax=200

		self.picw=500
		self.pich=375

		self.xmax = 20
		self.ymax = [1, 1]
		
		self.scale1 = tkinter.DoubleVar()
		self.scale2 = tkinter.DoubleVar()
		self.scale1.set(500)
		self.scale2.set(500)
		
		DialogApp.__init__(self, parent, title, prc)
		self.buf=0

	def initUI(self):
		
		self.paintArea = tkinter.Canvas(self.parent, width = self.picw, height=self.pich, bg='black')
		self.paintArea.grid(row=0, column=1, padx=5, pady=5)
		
		tkinter.Scale(self.parent, variable=self.scale1, resolution = 10, showvalue = 0,
			troughcolor='red', orient=tkinter.VERTICAL, 
			from_ = 10, to=1000, length=300).grid(row=0, column=0, padx=5, pady=5)
		
		tkinter.Scale(self.parent, variable=self.scale2, resolution = 10, showvalue = 0,
			troughcolor = 'green', orient=tkinter.VERTICAL, 
			from_=10, to=1000, length=300).grid(row=0, column=2, padx=5, pady=5)
		
		tkinter.Button(self.parent, text = 'Выход', width = 10, 
			command = self.parent.withdraw).grid(row=1, column=1, padx=5, pady=5)

		self.paintall()
	
	# update circular buffers
	def updateBuf(self, x1, x2):
		if self.ncur >= self.nmax:
			# remove old data
			self.buf1.pop(0)
			self.buf2.pop(0)
		else:
			self.ncur += 1
		
		# add new one
		self.buf1.append(x1)
		self.buf2.append(x2)
	
	# draw grids and labels
	def drawGrid(self):
		y = 0
		yl1 = self.ymax[0]
		yl2 = self.ymax[1]
		dy1 = yl1/2
		dy2 = yl2/2
		for i in range(4):
			self.paintArea.create_line(0, y, self.picw, y, fill='gray')
			self.paintArea.create_text(20, y+10, text=str(yl1), fill='red')
			self.paintArea.create_text(self.picw-20, y+10, text=str(yl2), fill='green')
			y = y + self.pich/4
			yl1 -= dy1
			yl2 -= dy2
		x = 0
		t = 0
		tm = self.xmax
		for i in range(4):
			self.paintArea.create_line(x, 0, x, self.pich, fill='gray')
			self.paintArea.create_text(x-20, self.pich-10, text=str(t), fill='white')
			x = x + self.picw/4
			t += tm/4
			
		self.paintArea.create_text(50, self.pich-20, text='Момент Н*м', fill='red')
		self.paintArea.create_text(self.picw-60, self.pich-20, text='Частота Об/мин', fill='green')
	
	# repaint graph with current buffers
	def paintall(self):
		self.paintArea.delete('all')
		
		self.ymax = [self.scale1.get(), self.scale2.get()]
		self.drawGrid()
		
		ib = 0
		color = 'red'
		for buf in [self.buf1[:], self.buf2[:]]:
			ymax = self.ymax[ib]
			if buf:
				t = 0
				x0 = 0
				x = x0
				y0 = self.pich/2*(1-buf[0]/ymax)
				for y in buf:
					x = t*self.picw/(self.nmax-1)
					y = self.pich/2*(1-y/ymax)
					self.paintArea.create_line(x0, y0, x, y, fill=color)
					x0 = x
					y0 = y
					t += 1
			color = 'green'
			ib += 1
		# repaint through 100 ms
		self.paintArea.after(100, self.paintall)
