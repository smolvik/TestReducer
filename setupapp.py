#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk

from dialogapp import DialogApp

class SetupApp(DialogApp):
	
	def __init__(self, parent, title):
		print('OscillApp')
		DialogApp.__init__(self, parent, title)
		self.timerFlag = {'mode':1}

	def initUI(self):
		
		lbiolst = ['Обороты, об.', 'Крутящий момент, Н*м', 'Скорость вращения, об/мин']
		
		lblst = ['Режим', 'Частота вращения входного вала, об/мин', 
		'Полный рабочий ход входного вала, об',
		'Максимальный тормозной крутящий момент на выходном валу, Н*м',
		'Количество эксплуатационных циклов']
		
		modelst = ['ТВП1', 'КРП1', 'ТВП2', 'КРП2', 'ТВП3', 'СРП', 'РПП',
		'ТВЗ1', 'ТРЗ', 'ТВЗ2', 'УРЗ', 'КРЗ']
		
		framepar = tkinter.LabelFrame(self.parent, text='Параметры теста')
		framein = tkinter.LabelFrame(self.parent, text='Входной вал')
		frameout = tkinter.LabelFrame(self.parent, text = 'Выходной вал')
		framebut = tkinter.Frame(self.parent)
		
		framepar.grid(row=0, column=0, padx=5, pady=5, columnspan=2, sticky=tkinter.W+tkinter.E)
		
		# ~ self.progress = ttk.Progressbar(self.parent, orient = tkinter.HORIZONTAL, length = 600, mode = 'determinate')
		# ~ self.progress.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky=tkinter.W+tkinter.E)
		# ~ self.progress['value'] = 0		
		
		# ~ framein.grid(row=2, column=0, padx=5, pady=5)
		# ~ frameout.grid(row=2, column=1, padx=5, pady=5)
		
		framebut.grid(row=3, column=0, padx=5, pady=5, columnspan=2)
		
		# ~ for i in range(len(lbiolst)):
			# ~ tkinter.Label(framein, text=lbiolst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			# ~ tkinter.Label(frameout, text=lbiolst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			
			# ~ tkinter.Entry(framein, width=10).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.W)
			# ~ tkinter.Entry(frameout, width=10).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.W)
		
		for i in range(len(lblst)):
			tkinter.Label(framepar, text=lblst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			if i ==0:
				ttk.Combobox(framepar, width=9, values=modelst, state='readonly').grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.W)
			else:
				tkinter.Entry(framepar, width=10).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.E)
		
				
		tkinter.Button(framebut, text = 'Запуск', width = 10, command = self.startproc).grid(row=0, column=1, padx=5, pady=5)
		tkinter.Button(framebut, text = 'Остановка', width = 10, command = self.stopproc).grid(row=0, column=2, padx=5, pady=5)
		tkinter.Button(framebut, text = 'Выход', width = 10, command = self.parent.withdraw).grid(row=0, column=3, padx=5, pady=5)
		
		
	def stopproc(self):
		print('stop proc')
		self.timerFlag['mode'] = 1
		
	def startproc(self):
		print('start proc')
		self.timerFlag['mode'] = 2
		
	def update(self, perc):
		#self.progress['value'] = perc
		if perc == 100:
			self.timerFlag['mode'] = 1

