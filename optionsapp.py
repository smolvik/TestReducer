#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk
import sqlite3
from dialogapp import DialogApp
import threading
import struct
import time
import configparser
from trgdef import CmdEnum

class OptionsApp(DialogApp):
	
	def __init__(self, parent, title, prc, cmdC, cmdQ):
		
		self.cmdCondition = cmdC
		self.cmdQueue = cmdQ
		
		self.mac = []
		self.mac.append(tkinter.StringVar(value='12'))
		self.mac.append(tkinter.StringVar(value='34'))
		self.mac.append(tkinter.StringVar(value='56'))
		self.mac.append(tkinter.StringVar(value='78'))
		self.mac.append(tkinter.StringVar(value='9a'))
		self.mac.append(tkinter.StringVar(value='bc'))
		
		self.ip = []
		self.ip.append(tkinter.StringVar(value='10'))
		self.ip.append(tkinter.StringVar(value='0'))
		self.ip.append(tkinter.StringVar(value='0'))
		self.ip.append(tkinter.StringVar(value='1'))
		
		DialogApp.__init__(self, parent, title, prc)

	def initUI(self):
		f1 = tkinter.LabelFrame(self.parent, text='Контроллер')
		f1.grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		tkinter.Button(self.parent, text = 'Сохранить', width = 10, command = self.onSave).grid(row=1, column=0, padx=5, pady=5)
		
		tkinter.Label(f1, text='MAC адрес:').grid(row=0, column=0, padx=5, pady=5, sticky=tkinter.W)
		for i in range(6):
			tkinter.Entry(f1, width=4, textvariable = self.mac[i], validate='all', validatecommand = (f1.register(self.validateMac), '%P')).grid(row=0, column=i+1, padx=5, pady=5, sticky=tkinter.W)
		
		tkinter.Label(f1, text='IP адрес:').grid(row=1, column=0, padx=5, pady=5, sticky=tkinter.W)
		for i in range(4):
			tkinter.Entry(f1, width=4, textvariable = self.ip[i], validate='all', validatecommand = (f1.register(self.validateIp), '%P')).grid(row=1, column=i+1, padx=5, pady=5, sticky=tkinter.W)
	
	def saveToController(self, dat):
		netParam = {}
		netParam['cmd'] = CmdEnum.SETPAR
		# get crc16
		crcpoly = 0xa001
		crc = 0xffff	# crc init
		for b in dat:
			buf=crc^(0xff&b)
			for i in range(8):
				if buf & 0x0001:
					buf = buf>>1;
					buf = buf ^ crcpoly
				else:
					buf = buf>>1;
			crc = buf
		#print(struct.unpack('>HHHHH',dat))
		print(hex(crc))
		
		dat = struct.unpack('HHHHH',dat)
		dat = dat +(crc,)		
		print(dat)
		netParam['dat'] = dat
		with self.cmdCondition:
			self.cmdQueue.append(netParam)
			self.cmdCondition.notifyAll()		
	
	def onSave(self):
		ip = '{}.{}.{}.{}'.format(self.ip[0].get(), self.ip[1].get(), self.ip[2].get(), self.ip[3].get())
		mac = '{}:{}:{}:{}:{}:{}'.format(self.mac[0].get(), self.mac[1].get(), self.mac[2].get(), self.mac[3].get()
			, self.mac[4].get(), self.mac[5].get())
		
		# save to config file
		config = configparser.ConfigParser()
		config['CONTROLLER'] = {'IP':ip,'MAC':mac}
		with open('test.ini', 'w') as configfile:
			config.write(configfile)
		
		# save to controller
		dat = []
		for b in self.ip:
			dat.append(int(b.get()))
		for b in self.mac:
			dat.append(int(b.get(),16))
		self.saveToController(bytes(dat))
		
	def validateMac(self, what):
		try:
			mac = int(what,16)
		except ValueError:
			return False
		
		if (mac >= 0) and (mac < 256):
			return True
		else:
			return False
			
	def validateIp(self, what):
		try:
			mac = int(what)
		except ValueError:
			return False
		
		if (mac >= 0) and (mac < 256):
			return True
		else:
			return False			

