#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk
from dialogapp import DialogApp
import sqlite3

class ConfigApp(DialogApp):
	
	def __init__(self, parent, title, prc):
		print('ConfigApp')
		
		self.param = []
		self.param.append(tkinter.StringVar())
		self.param.append(tkinter.IntVar())
		self.param.append(tkinter.DoubleVar())
		self.param.append(tkinter.IntVar())
		self.param.append(tkinter.DoubleVar())
		self.param.append(tkinter.StringVar())
		#self.param[0].set('Name')
		
		self.currprofName = tkinter.StringVar()
		
		DialogApp.__init__(self, parent, title, prc)

	def initUI(self):
		
		parlst = ['Наименование профиля', 'Частота вращения входного вала, об/мин', 'Передаточное отношение механизма', 
		'Полный рабочий ход входного вала, об', 'Максимальный тормозной крутящий момент на выходном валу, Н*м',
		'Циклограмма']
		
		valproc = [self.nameValidate, self.speedValidate, self.ratioValidate, 
				self.numrotValidate, self.torqueValidate, self.cyclogramValidate]
		
		framepar = tkinter.LabelFrame(self.parent, text='Параметры профиля')
		frameprof = tkinter.LabelFrame(self.parent, text='Выбор профиля')
		#frameprof = tkinter.Frame(self.parent)
		framebut = tkinter.Frame(self.parent)
		
		frameprof.grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		framepar.grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		framebut.grid(row=2, column=0, padx=5, pady=5, sticky=tkinter.W)
				
		numpar = len(parlst)
		for i in range(numpar):
			tkinter.Label(framepar, text=parlst[i]).grid(row=i, column=0, padx=5, pady=5, sticky=tkinter.W)
			
			if i == numpar-1:
				self.cboxCycl = ttk.Combobox(framepar, width=10, values=[], postcommand = self.updcycllst, state='readonly', textvariable = self.param[i])
				self.cboxCycl.grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.E)
			else:
				tkinter.Entry(framepar, width=10, textvariable = self.param[i], validate='all', validatecommand = (framepar.register(valproc[i]), '%P')).grid(row=i, column=1, padx=5, pady=5, sticky=tkinter.E)
		tkinter.Button(framepar, text = 'Сохранить', width = 10, command = self.saveprofile).grid(row=i+1, column=0, padx=5, pady=5, sticky=tkinter.W)
	
		self.cboxProf = ttk.Combobox(frameprof, width=10, values=[], postcommand = self.updproflst, state='readonly', textvariable = self.currprofName)
		self.cboxProf.grid(row=0, column=0, padx=5, pady=5)
		tkinter.Button(frameprof, text = 'Загрузить', width = 10, command = self.loadprofile).grid(row=0, column=1, padx=5, pady=5)
		tkinter.Button(frameprof, text = 'Удалить', width = 10, command = self.rmproc).grid(row=0, column=3, padx=5, pady=5)		
		
		tkinter.Button(framebut, text = 'Выход', width = 10, command = self.parent.withdraw).grid(row=0, column=3, padx=5, pady=5)
		
	# load profile with the current selected name from the database
	def loadprofile(self):
		name = self.currprofName.get()
		print('load profile:' + name)
		if name=='':
			return
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		#sql = "select * from Profiles where name="+"'"+name+"'"
		sql = """select Profiles.name, Profiles.speed_in, Profiles.rd_ratio, 
		Profiles.numrot_in, Profiles.max_torque_out, Cyclograms.name 
		from Profiles left join Cyclograms on(Profiles.cyclogram_id==Cyclograms.id)
		where Profiles.name=="""+"'"+name+"'"
		lst =[]
		try:
			lst = cursor.execute(sql).fetchone()
		except Exception as err:
			self.logProc('Ошибка базы данных: {}\n'.format(err))
			conn.close()
			return
		else:
			self.logProc('Запись успешно загружена\n')
			conn.close()
	
		i = 0
		for p in self.param:
			p.set(lst[i])
			i+=1
			
	# update cbox cyclograms names list with names quered from the database
	def updcycllst(self):
		print('get cyclograms list')
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		lst = cursor.execute("select name from Cyclograms").fetchall()
		conn.close()
				
		print(lst)
		self.cboxCycl['values'] = lst
	
	# update cbox profiles names list with names quered from the database
	def updproflst(self):
		print('get profiles list')
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		lst = cursor.execute("select name from Profiles").fetchall()
		conn.close()
				
		print(lst)
		self.cboxProf['values'] = lst
		

	# save edited profile to the database
	def saveprofile(self):
		print('save profile to db')
		
		conn = sqlite3.connect('trd.db')
		conn.execute("PRAGMA foreign_keys = 1")
		cursor = conn.cursor()
		
		val = []
		for i in self.param:
			val.append(i.get())
		print(val)
		
		try:
			name = val[0]
			cycname = val[-1]
			if cursor.execute("select exists(select * from Profiles where name='{}')".format(name)).fetchone()[0]:
				# row exists
				# update one
				sql = """update Profiles
				set speed_in=?,rd_ratio=?,numrot_in=?,max_torque_out=?,cyclogram_id=(select id from Cyclograms where name='{}')
				where name='{}'""".format(cycname, name)
				cursor.execute(sql, val[1:-1])
			else:
				# row does not exist
				# insert new one
				sql = """INSERT INTO Profiles(name,speed_in,rd_ratio,numrot_in,max_torque_out,cyclogram_id)
				VALUES(?,?,?,?,?,(select id from Cyclograms where name='{}')) """.format(val[-1])
				cursor.execute(sql, val[:-1])
		except Exception as err:
			self.logProc('Ошибка базы данных: {}\n'.format(err))
			conn.close()
			return 
		else:
			self.logProc('Запись успешно сохранена\n')
			conn.commit()
			conn.close()
		
	# remove selected profile from the database
	def rmproc(self):
		print('rm proc')
		
		name = self.currprofName.get()
		sql = "delete from Profiles where name="+"'"+name+"'"
		
		conn = sqlite3.connect('trd.db')
		cursor = conn.cursor()
		
		try:
			cursor.execute(sql)
		except Exception as err:
			self.logProc('Ошибка базы данных: {}\n'.format(err))
			conn.close()
			return
		else:
			self.logProc('Запись успешно удалена\n')
			conn.commit()
			conn.close()
			self.cboxProf.set('')

	def cyclogramValidate(self, what):
		print('cyclogram validation')

		try:
			ncyc = int(what)
		except ValueError:
			return False
			
		if ncyc == 1 or ncyc == 2:
			return True
		else:
			return False

		
	def torqueValidate(self, what):
		print('torque validation')
		
		try:
			torque = float(what)
		except ValueError:
			return False
		
		if torque <= 38.2:
			return True
		else:
			return False
		
	
	def numrotValidate(self, what):
		print('numrot validation')

		try:
			numrot = int(what)
		except ValueError:
			return False
			
		if numrot <= 999:
			return True
		else:
			return False
	
	def ratioValidate(self, what):
		print('ratio validation')
		
		try:
			ratio = float(what)
		except ValueError:
			return False
		
		if ratio <= 1.5:
			return True
		else:
			return False

	def speedValidate(self, what):
		print('speed validation')
		
		try:
			spd = int(what)
		except ValueError:
			return False
			
		print(spd)
		if spd <= 1000:
			return True
		else:
			return False
		
	def nameValidate(self, what):
		print('name validation')
		return True
