#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from oscillapp import OscillApp
from setupapp import SetupApp
from monitorapp import MonitorApp
import hashlib
import os

class MainApp():
	def __init__(self, parent):
		self.parent = parent
		self.initUI()
		
		self.oscillWnd1 = tkinter.Toplevel(parent)
		self.oscillApp1 = OscillApp(self.oscillWnd1, "Панель осциллографа канал 1")
		
		self.oscillWnd2 = tkinter.Toplevel(parent)
		self.oscillApp2 = OscillApp(self.oscillWnd2, "Панель осциллографа канал 2")
		
		self.setupWnd = tkinter.Toplevel(parent)
		self.setupApp = SetupApp(self.setupWnd, "Панель управления")
		
		self.monitorWnd = tkinter.Toplevel(parent)
		self.monitorApp = MonitorApp(self.monitorWnd, "Панель индикации")
		
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
		
		menubar = tkinter.Menu(self.parent, font='Arial 12')
		self.parent.config(menu=menubar)
		filemenu = tkinter.Menu(menubar, font='Arial 12')
		winmenu = tkinter.Menu(menubar, font='Arial 12')
		cmdmenu = tkinter.Menu(menubar, font='Arial 12')
		
		filemenu.add_command(label='Выход', command=self.onExit)		
		winmenu.add_command(label='Панель управления', command=self.setupUp)
		winmenu.add_command(label='Панель индикации', command=self.monitorUp)
		winmenu.add_command(label='Панель осциллографа канал 1', command=self.oscillUp1)
		winmenu.add_command(label='Панель осциллографа канал 2', command=self.oscillUp2)
		cmdmenu.add_command(label='Руководство', command=self.onMan)
		cmdmenu.add_command(label='О программе', command=self.onAbout)

		menubar.add_cascade(label="Файл", menu=filemenu)
		menubar.add_cascade(label="Команды", menu=cmdmenu)
		menubar.add_cascade(label="Окна", menu=winmenu)

		#self.frame = tkinter.Frame(self.parent)
		
		#tkinter.Button(self.frame, text = 'Setup', width = 25, command = self.setupUp).pack()		
		#self.button1 = tkinter.Button(self.frame, text = 'Oscill', width = 25, command = self.oscillUp).pack()
		#tkinter.Button(self.frame, text = 'Exit', width = 25, command = self.onExit).pack()
		
		#self.frame.pack()
		#self.app = 0
		
	def onAbout(self):
		
		hashobj = hashlib.md5()
		fllst = os.listdir()
		fllst.sort()
		for fn in fllst:
			if fn[-2:] == 'py':
				#print(fn)
				hashobj.update(open(fn, "rb").read())		
		
		self.textbox.insert(tkinter.INSERT, '****************\nПрограмма для управления САУ в1.1\n')
		self.textbox.insert(tkinter.INSERT, 'md5sum='+hashobj.hexdigest()+'\n*****************\n')
		
	def onMan(self): 
		self.textbox.delete('1.0', 'end') 
		self.textbox.insert('1.0', open('man.txt', 'rt').read())
		
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
