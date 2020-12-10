#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk

from dialogapp import DialogApp

class SetupApp(DialogApp):
	timerFlag = {'mode':1}
	
	def __init__(self, parent, title):
		print('OscillApp')
		DialogApp.__init__(self, parent, title)
		

	def initUI(self):
		
		parlst = ['Наименование профиля', 'Скорость вращения входного вала, об/мин', 'Передаточное отношение механизма', 
		'Полный рабочий ход входного вала, об', 'Максимальный тормозной крутящий момент на выходном валу, Н*м',
		'Циклограмма']
		
		framepar = tkinter.LabelFrame(self.parent, text='Параметры цикла')
		frameprof = tkinter.Frame(self.parent)
		frametst = tkinter.LabelFrame(self.parent, text='Параметры испытания')
		framebut = tkinter.Frame(self.parent)
		
		frameprof.grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		framepar.grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		frametst.grid(row=2, column=0, padx=5, pady=5, sticky=tkinter.W)
		framebut.grid(row=3, column=0, padx=5, pady=5, sticky=tkinter.W)

		proflst=['a','b','c']
		tkinter.Label(framepar, text='Выбор профиля для загрузки').grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		ttk.Combobox(framepar, width=10, values=proflst, state='readonly').grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.E)					
		tkinter.Button(framepar, text = 'Загрузить', width = 10, command = self.loadprofile).grid(row=0, column=2, padx=5, pady=5)
		
		for i in range(len(parlst)):
			tkinter.Label(framepar, text=parlst[i]).grid(row=i+1, column=0, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Entry(framepar, width=10, state='readonly').grid(row=i+1, column=1, columnspan=2, padx=5, pady=5, sticky=tkinter.E)
			

		tkinter.Label(frametst, text='Кол-во циклов').grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		tkinter.Entry(frametst, width=10, ).grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.E)
		svlst=['a','b','c']
		tkinter.Label(frametst, text='Частота сохранения результатов').grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		ttk.Combobox(frametst, width=10, values=svlst, state='readonly').grid(row=1, column=1, padx=5, pady=5, sticky=tkinter.E)					
				
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
		if perc == 100:
			self.timerFlag['mode'] = 1
			
	def loadprofile(self):
		print('load profile')

