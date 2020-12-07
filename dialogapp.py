#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter

class DialogApp:
	
	def __init__(self, parent, title):
		print('DialogApp')
		self.parent = parent
		
		self.parent.title(title)
		self.parent.withdraw()		
		self.parent.protocol('WM_DELETE_WINDOW', parent.withdraw)
		self.initUI()

	def initUI(self):
		pass
		
