#!/usr/bin/python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter import ttk

from dialogapp import DialogApp

class MonitorApp(DialogApp):
	
	def __init__(self, parent, title, prc):
		print('OscillApp')
		
		self.param = []
		for i in range(9):
			if i == 3 or i == 6:
				self.param.append(tkinter.DoubleVar())
			else:
				self.param.append(tkinter.IntVar())
		
		DialogApp.__init__(self, parent, title, prc)


	def initUI(self):
		lblst = ['Обороты, об.', 'Крутящий момент, Н*м', 'Частота вращения, об/мин']
		f1 = tkinter.LabelFrame(self.parent, text='Входной вал')
		f2 = tkinter.LabelFrame(self.parent, text = 'Выходной вал')
		f3 = tkinter.Frame(self.parent)
		
		f1.grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		f2.grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.W)
		
		for i in range(3):
			tkinter.Label(f1, text=lblst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Entry(f1, width=10, textvariable = self.param[i+2]).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.W)
			
			tkinter.Label(f2, text=lblst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Entry(f2, width=10, textvariable = self.param[i+5]).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.W)			
		
		ttk.Progressbar(self.parent, value = 0, orient = tkinter.HORIZONTAL, length = 600, mode = 'determinate', variable = self.param[0]).grid(row=1, column=0, padx=5, pady=5, columnspan=2)
		ttk.Progressbar(self.parent, value = 0, orient = tkinter.HORIZONTAL, length = 600, mode = 'determinate', variable = self.param[1]).grid(row=2, column=0, padx=5, pady=5, columnspan=2)
		tkinter.Label(self.parent, textvariable = self.param[8]).grid(row=3, column=0, padx=5, pady=5, sticky=tkinter.W)
		tkinter.Button(self.parent, text = 'Выход', width = 10, command = self.parent.withdraw).grid(row=4, column=0, padx=5, pady=5, columnspan=2)

	def update(self, par):
		#self.progress['value'] = par[0]
		for i in range(len(par)):
			self.param[i].set(par[i])
		


