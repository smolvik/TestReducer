#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk
import sqlite3
from dialogapp import DialogApp
import threading
from enum import IntEnum

class SetupApp(DialogApp):
	
	class CmdEnum(IntEnum):
		START=1
		PAUSE=2
		STOP=3
		ALIVE=4
		EXIT=5
	
	def __init__(self, parent, title, prc):
		print('OscillApp')
		
		self.cmdParam={}
		
		self.cmdQueue = []
		
		self.param = []
		self.param.append(tkinter.StringVar())
		self.param.append(tkinter.IntVar())
		self.param.append(tkinter.DoubleVar())
		self.param.append(tkinter.IntVar())
		self.param.append(tkinter.DoubleVar())
		self.param.append(tkinter.StringVar())
		
		self.cycparam = []
		for i in range(5):
			self.cycparam.append((tkinter.IntVar(),tkinter.IntVar()))
		
		self.currprofName = tkinter.StringVar()
		self.numCycles = tkinter.IntVar()
		self.numCycles.set(1)
		
		DialogApp.__init__(self, parent, title, prc)

	def initUI(self):
		
		parlst = ['Наименование профиля', 'Частота вращения входного вала, об/мин', 'Передаточное отношение механизма', 
		'Полный рабочий ход входного вала, об', 'Максимальный тормозной крутящий момент на выходном валу, Н*м',
		'Циклограмма']
		
		framepar = tkinter.LabelFrame(self.parent, text='Параметры цикла')
		frameprof = tkinter.Frame(self.parent)
		frametst = tkinter.LabelFrame(self.parent, text='Параметры испытания')
		framecyc = tkinter.LabelFrame(self.parent, text='Параметры циклограммы')
		framebut = tkinter.Frame(self.parent)
		
		frameprof.grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		framepar.grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		framecyc.grid(row=2, column=0, padx=5, pady=5, sticky=tkinter.W)
		frametst.grid(row=3, column=0, padx=5, pady=5, sticky=tkinter.W)
		framebut.grid(row=4, column=0, padx=5, pady=5, sticky=tkinter.W)

		tkinter.Label(framepar, text='Выбор профиля для загрузки').grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		self.cboxProf = ttk.Combobox(framepar, width=10, values=[], state='readonly', postcommand = self.updproflst, textvariable = self.currprofName)
		self.cboxProf.grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.E)
		tkinter.Button(framepar, text = 'Загрузить', width = 10, command = self.loadprofile).grid(row=0, column=2, padx=5, pady=5)
		
		for i in range(len(parlst)):
			tkinter.Label(framepar, text=parlst[i]).grid(row=i+1, column=0, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Entry(framepar, width=10, state='readonly', textvariable = self.param[i]).grid(row=i+1, column=1, columnspan=2, padx=5, pady=5, sticky=tkinter.E)

		tkinter.Label(framecyc, text='Рабочий ход входного вала %').grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		tkinter.Label(framecyc, text='Тормозной крутящий момент %').grid(row=2, column=0, padx=5, pady=5, sticky=tkinter.W)
		i=0
		for j in range(1, 6):
			tkinter.Entry(framecyc, width=4, state='readonly', textvariable = self.cycparam[i][0]).grid(row=1, column=j, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Entry(framecyc, width=4, state='readonly', textvariable = self.cycparam[i][1]).grid(row=2, column=j, padx=5, pady=5, sticky=tkinter.W)
			i = i+1
			
		tkinter.Label(frametst, text='Кол-во циклов').grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		tkinter.Entry(frametst, width=10, textvariable=self.numCycles, validate='all', validatecommand = (frametst.register(self.validateNumCycl), '%P')).grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.E)
		svlst=['Каждый','Первый, каждый десятый, последний','Первый, каждый сотый, последний', 'Первый, каждый тысячный, последний']
		tkinter.Label(frametst, text='Частота сохранения результатов').grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		self.cboxSaveMode = ttk.Combobox(frametst, width=40, values=svlst, state='readonly')
		self.cboxSaveMode.grid(row=1, column=1, padx=5, pady=5, sticky=tkinter.E)

		self.startBut = tkinter.Button(framebut, text = 'Запуск', state=tkinter.DISABLED, width = 10, command = self.startproc)
		self.startBut.grid(row=0, column=1, padx=5, pady=5)
		tkinter.Button(framebut, text = 'Пауза', width = 10, command = self.pauseproc).grid(row=0, column=2, padx=5, pady=5)
		tkinter.Button(framebut, text = 'Стоп', width = 10, command = self.stopproc).grid(row=0, column=3, padx=5, pady=5)
		tkinter.Button(framebut, text = 'Выход', width = 10, command = self.parent.withdraw).grid(row=0, column=4, padx=5, pady=5)

	def validateNumCycl(self, what):
		#print('num cycl validation')

		try:
			ncyc = int(what)
		except ValueError:
			return False
			
		if ncyc > 108000 or ncyc < 1:
			print('num cycl validation fault')
			return False
		else:
			print('num cycl validation ОК')
			return True

		
	def updproflst(self):
		print('get profiles list')
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		lst = cursor.execute("select name from Profiles").fetchall()
		conn.close()
				
		print(lst)
		self.cboxProf['values'] = lst
		
	def pauseproc(self):
		print('pause proc')
		self.cmdParam['cmd'] = self.CmdEnum.PAUSE
		self.cmdQueue.append(self.cmdParam)
		
	def stopproc(self):
		print('stop proc')
		self.cmdParam['cmd'] = self.CmdEnum.STOP
		self.cmdQueue.append(self.cmdParam)
		
	def startproc(self):
		print('start proc')
		self.cmdParam['savemod'] = self.cboxSaveMode.current()
		self.cmdParam['numcyc'] = self.numCycles.get()
		self.cmdParam['cmd'] = self.CmdEnum.START
		print(self.cmdParam)
		
		self.cmdQueue.append(self.cmdParam)
		
	def update(self, perc):
		if perc == 100:
			self.timerFlag['mode'] = 1
			
	def loadprofile(self):
		print('load profile')
		name = self.currprofName.get()
		print('load profile:' + name)
		if name=='':
			return
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()

		sql = """select Profiles.name, Profiles.speed_in, Profiles.rd_ratio, 
		Profiles.numrot_in, Profiles.max_torque_out, Cyclograms.name,  
		Cyclograms.n1, Cyclograms.n2, Cyclograms.n3, Cyclograms.n4, Cyclograms.n5,
		Cyclograms.m1, Cyclograms.m2, Cyclograms.m3, Cyclograms.m4, Cyclograms.m5
		from Profiles left join Cyclograms on(Profiles.cyclogram_id==Cyclograms.id)
		where Profiles.name=='{}'""".format(name)
		
		lst=[]
		try:
			lst = cursor.execute(sql).fetchone()
		except Exception as err:
			self.logProc('Ошибка базы данных: {}\n'.format(err))
			conn.close()
			return
		else:
			self.logProc('Запись успешно загружена\n')
			self.startBut['state'] = tkinter.NORMAL
			conn.close()

		# data is sorted by the first element
		cyc = sorted(list(zip(lst[6:11], lst[11:16])), key=lambda l: l[0])
		print("*************cyc={}".format(cyc))
		
		self.cmdParam['speed_in'] = lst[1]
		self.cmdParam['rd_ratio'] = lst[2]
		self.cmdParam['numrot_in'] = lst[3]
		self.cmdParam['max_torque_out'] = lst[4]
		self.cmdParam['cyclo'] = cyc[:]

		i = 0
		for p in self.param:
			p.set(lst[i])
			i+=1
			
		i = 0
		for p in self.cycparam:
			p[0].set(cyc[i][0])
			p[1].set(cyc[i][1])
			i+=1
