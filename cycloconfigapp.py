#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk
from dialogapp import DialogApp
import sqlite3

class CycloConfigApp(DialogApp):
	
	def __init__(self, parent, title):
		print('CycloConfigApp')
		
		self.param1 = []
		self.param2 = []
		for i in range(5):
			self.param1.append(tkinter.IntVar())
			self.param2.append(tkinter.IntVar())
					
		self.currprofName = tkinter.StringVar()
		self.cycloName = tkinter.StringVar()
		
		DialogApp.__init__(self, parent, title)

	def initUI(self):
		
		framepar = tkinter.LabelFrame(self.parent, text='Параметры циклограммы')
		frameprof = tkinter.LabelFrame(self.parent, text='Выбор профиля')
		framebut = tkinter.Frame(self.parent)
				
		frameprof.grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		framepar.grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		framebut.grid(row=2, column=0, padx=5, pady=5, sticky=tkinter.W)
				
		tkinter.Label(framepar, text='Наименование профиля').grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		tkinter.Entry(framepar, width=10, textvariable = self.cycloName).grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tkinter.E)
		
		tkinter.Label(framepar, text='Рабочий ход входного вала').grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		tkinter.Label(framepar, text='Тормозной крутящий момент').grid(row=2, column=0, padx=5, pady=5, sticky=tkinter.W)
		for i in range(len(self.param1)):
			tkinter.Entry(framepar, width=4, textvariable = self.param1[i], validate='all', validatecommand = (framepar.register(self.percValidate), '%P')).grid(row=1, column=i+1, padx=5, pady=5, sticky=tkinter.W)
			tkinter.Entry(framepar, width=4, textvariable = self.param2[i], validate='all', validatecommand = (framepar.register(self.percValidate), '%P')).grid(row=2, column=i+1, padx=5, pady=5, sticky=tkinter.W)
		
		tkinter.Button(framepar, text = 'Сохранить', width = 10, command = self.saveprofile).grid(row=3, column=0, padx=5, pady=5, sticky=tkinter.W)
	
		self.cboxProf = ttk.Combobox(frameprof, width=10, values=[], postcommand = self.updproflst, state='readonly', textvariable = self.currprofName)
		self.cboxProf.grid(row=0, column=0, padx=5, pady=5)
		tkinter.Button(frameprof, text = 'Загрузить', width = 10, command = self.loadprofile).grid(row=0, column=1, padx=5, pady=5)
		tkinter.Button(frameprof, text = 'Удалить', width = 10, command = self.rmproc).grid(row=0, column=2, padx=5, pady=5)		
		
		tkinter.Button(framebut, text = 'Выход', width = 10, command = self.parent.withdraw).grid(row=0, column=3, padx=5, pady=5)
		
	# load profile with the current selected name from the database
	def loadprofile(self):
		name = self.currprofName.get()
		print('load Cyclogram:' + name)
		
		if name=='':
			return
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		sql = "select * from Cyclograms where name="+"'"+name+"'"
		lst = cursor.execute(sql).fetchone()
		conn.close()
		
		print(lst)
		
		ldname = lst[1]
		# data is sorted by the first element
		ldpar = sorted(list(zip(lst[2:7], lst[7:12])), key=lambda lst: lst[0])
		
		print(ldname)
		print(ldpar)
		
		self.cycloName.set(ldname)
		for i in range(len(ldpar)):
			self.param1[i].set(ldpar[i][0])
			self.param2[i].set(ldpar[i][1])
	
	# update cbox profiles names list with names quered from the database
	def updproflst(self):
		print('get Cyclogram list')
	
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		lst = cursor.execute("select name from Cyclograms").fetchall()
		conn.close()
				
		print(lst)
		self.cboxProf['values'] = lst
		

	# save edited profile to the database
	def saveprofile(self):
		print('save Cyclogram to db')
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		
		name = self.cycloName.get()
		val = [name]
		for i in self.param1:
			val.append(i.get())
			
		for i in self.param2:
			val.append(i.get())
		print(val)
		
		# delete old row with name
		cursor.execute("delete from Cyclograms where name="+"'"+name+"'")
		# insert new one
		sql = ''' INSERT INTO Cyclograms(name,n1,n2,n3,n4,n5,m1,m2,m3,m4,m5) VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
		cursor.execute(sql, val)
		
		conn.commit()
		conn.close()
		
	# remove selected profile from the database
	def rmproc(self):
		print('rm proc')
		
		name = self.currprofName.get()
		sql = "delete from Cyclograms where name="+"'"+name+"'"
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.cboxProf.set('')
	
	def percValidate(self, what):
		print('percent validation')

		try:
			per = int(what)
		except ValueError:
			return False
			
		if per > 100 or per < 0:
			return False
		else:
			return True

