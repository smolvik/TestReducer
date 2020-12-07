#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk

from dialogapp import DialogApp

class MonitorApp(DialogApp):
	
	def __init__(self, parent, title):
		print('OscillApp')
		DialogApp.__init__(self, parent, title)


	def initUI(self):
		lblst = ['Обороты, об.', 'Крутящий момент, Н*м', 'Скорость вращения, об/мин']
		f1 = tkinter.LabelFrame(self.parent, text='Входной вал')
		f2 = tkinter.LabelFrame(self.parent, text = 'Выходной вал')
		f3 = tkinter.Frame(self.parent)
		
		f1.grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		f2.grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.W)
		
		for i in range(len(lblst)):
			tkinter.Label(f1, text=lblst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Label(f2, text=lblst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			
			tkinter.Entry(f1, width=10).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Entry(f2, width=10).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.W)
		
		self.progress = ttk.Progressbar(self.parent, orient = tkinter.HORIZONTAL, length = 600, mode = 'determinate')
		self.progress.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
		self.progress['value'] = 0
		
		tkinter.Button(self.parent, text = 'Выход', width = 10, command = self.parent.withdraw).grid(row=2, 
		column=0, padx=5, pady=5, columnspan=2)

	def update(self, perc):
		self.progress['value'] = perc
		


