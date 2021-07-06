#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from oscillapp import OscillApp
from setupapp import SetupApp
from monitorapp import MonitorApp
from configapp import ConfigApp
from cycloconfigapp import CycloConfigApp
import hashlib
import os
from datetime import datetime

class MainApp():
	def __init__(self, parent):
		self.parent = parent
		
		self.initUI()
		
		self.logmsg = []
		
		self.oscillWnd1 = tkinter.Toplevel(parent)
		#self.oscillWnd1.transient(parent) # window always at the foreground
		self.oscillApp1 = OscillApp(self.oscillWnd1, "Панель осциллографа канал 1", self.updateLogMsg)
		
		self.oscillWnd2 = tkinter.Toplevel(parent)
		#self.oscillWnd2.transient(parent) # window always at the foreground
		self.oscillApp2 = OscillApp(self.oscillWnd2, "Панель осциллографа канал 2", self.updateLogMsg)
		
		self.setupWnd = tkinter.Toplevel(parent)
		#self.setupWnd.transient(parent) # window always at the foreground
		self.setupApp = SetupApp(self.setupWnd, "Панель управления", self.updateLogMsg)
		
		self.monitorWnd = tkinter.Toplevel(parent)
		#self.monitorWnd.transient(parent) # window always at the foreground
		self.monitorApp = MonitorApp(self.monitorWnd, "Панель индикации", self.updateLogMsg)
		
		self.configWnd = tkinter.Toplevel(parent)
		#self.configWnd.transient(parent) # window always at the foreground
		self.configApp = ConfigApp(self.configWnd, "Редактор профилей режима эксплуатационного цикла", self.updateLogMsg)
		
		self.cycloconfigWnd = tkinter.Toplevel(parent)
		#self.cycloconfigWnd.transient(parent) # window always at the foreground
		self.cycloconfigApp = CycloConfigApp(self.cycloconfigWnd, "Редактор профилей циклограммы", self.updateLogMsg)
		
	def initUI(self):
		self.parent.title('Программа управления стендом тестирования редукторов')
		
		self.textFrame = tkinter.Frame(self.parent, height = 340, width = 600)
		self.textFrame.pack(side = 'bottom', fill = 'both', expand = 1)
		
		self.textbox = tkinter.Text(self.textFrame, font='Arial 12', wrap='word', foreground='blue')
		self.scrollbar = tkinter.Scrollbar(self.textFrame)

		self.scrollbar['command'] = self.textbox.yview
		self.textbox['yscrollcommand'] = self.scrollbar.set

		self.textbox.pack(side = 'left', fill = 'both', expand = 1)
		self.scrollbar.pack(side = 'right', fill = 'y')
		
		menubar = tkinter.Menu(self.parent) #font='Arial 12'
		self.parent.config(menu=menubar)
		filemenu = tkinter.Menu(menubar)
		winmenu = tkinter.Menu(menubar)
		cmdmenu = tkinter.Menu(menubar)
		
		filemenu.add_command(label='Отчет', command=self.onExit)
		filemenu.add_command(label='Выход', command=self.onExit)
		
		winmenu.add_command(label='Редактор циклограмм', command=self.cycloconfigUp)
		winmenu.add_command(label='Редактор профилей', command=self.configUp)
		winmenu.add_command(label='Панель управления', command=self.setupUp)
		winmenu.add_command(label='Панель индикации', command=self.monitorUp)
		winmenu.add_command(label='Панель осциллографа канал 1', command=self.oscillUp1)
		winmenu.add_command(label='Панель осциллографа канал 2', command=self.oscillUp2)
		
		cmdmenu.add_command(label='О программе', command=self.onAbout)
		cmdmenu.add_command(label='Проверка готовности', command=self.onCheck)

		menubar.add_cascade(label="Файл", menu=filemenu)
		menubar.add_cascade(label="Команды", menu=cmdmenu)
		menubar.add_cascade(label="Окна", menu=winmenu)

	def onAbout(self):
		
		hashobj = hashlib.md5()
		fllst = os.listdir()
		fllst.sort()
		for fn in fllst:
			if fn[-2:] == 'py':
				#print(fn)
				hashobj.update(open(fn, "rb").read())		
		
		#self.textbox.insert(tkinter.INSERT, '****************\nПрограмма для управления САУ в1.1\n')
		#self.textbox.insert(tkinter.INSERT, 'md5sum='+hashobj.hexdigest()+'\n*****************\n')
		self.updateLogMsg('Программа управления САУ в1.1 md5sum={}\n'.format(hashobj.hexdigest()))
		#self.updateLogMsg('md5sum={}\n'.format(hashobj.hexdigest()))
		
	def onCheck(self):
		#self.updateLogMsg(open('man.txt', 'rt').read())
		self.updateLogMsg('Item under construction\n')
		
	def cycloconfigUp(self):
		self.cycloconfigWnd.deiconify()
				
	def configUp(self):
		self.configWnd.deiconify()
		
	def setupUp(self):
		self.setupWnd.deiconify()
		
	def monitorUp(self):
		self.monitorWnd.deiconify()
		
	def oscillUp1(self):
		self.oscillWnd1.deiconify()
		
	def oscillUp2(self):
		self.oscillWnd2.deiconify()		
		
	def onExit(self):		
		self.parent.destroy()
		
	def updateLogMsg(self, msg):
			
		self.logmsg.append(datetime.now().strftime("%d.%m.%y %H:%M:%S ") + msg)
		if len(self.logmsg) > 24:
			self.logmsg.pop(0)
		
		self.textbox.delete('1.0', 'end')
		for s in self.logmsg:
			self.textbox.insert(tkinter.INSERT, s)
			
