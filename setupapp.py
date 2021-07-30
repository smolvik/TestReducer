#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
from tkinter import ttk
import sqlite3
from dialogapp import DialogApp
import threading
from enum import IntEnum
import struct
import lzma
import xlsxwriter
import time
from trgdef import CmdEnum

class SetupApp(DialogApp):
	
	# ~ class CmdEnum(IntEnum):
		# ~ START=1
		# ~ PAUSE=2
		# ~ STOP=3
		# ~ ALIVE=4
		# ~ SETPAR=5
		# ~ EXIT=6
	
	def __init__(self, parent, title, prc, cmdC, cmdQ):
		print('OscillApp')
		
		
		self.cmdParam={}
		
		self.cmdCondition = cmdC
		self.cmdQueue = cmdQ
		
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
		tkinter.Button(framebut, text = 'Отчет', width = 10, command = self.reportproc).grid(row=0, column=4, padx=5, pady=5)
		tkinter.Button(framebut, text = 'Выход', width = 10, command = self.parent.withdraw).grid(row=0, column=5, padx=5, pady=5)
		
		self.reportThr = None

	def reportproc(self):
		def titlesheet(workbook, par, cyc):
			titform = workbook.add_format()
			#titform.set_font_size(12)
			titform.set_bold()
			
			headform = workbook.add_format()
			headform.set_text_wrap()
			headform.set_align('top')

			#headform.set_bg_color('gray');
			
			heading = ['Частота вращения входного вала, об/мин', 'Передаточное отношение механизма',
				'Полный рабочий ход входного вала, об', 'Максимальный тормозной крутящий момент на выходном валу, Н*м',
				'Кол-во циклов']
			parlst = [par['speed_in'], par['rd_ratio'], par['numrot_in'], par['max_torque_out'], self.numCycles.get()]
				
			worksheet = workbook.add_worksheet('Title')
			
			worksheet.merge_range('A1:D1','Отчет об испытании', titform)
			worksheet.merge_range('A2:D2',time.strftime('%d.%m.%y %H:%M:%S', time.localtime()), titform)
			
			worksheet.merge_range('A4:E4','Параметры испытания', 0)
			worksheet.write_row(4, 0, heading, headform)
			worksheet.write_row(5, 0, parlst, 0)
			
			worksheet.merge_range('A8:F8','Циклограмма', 0)
			worksheet.write_column(8, 0, ('Обороты', 'Момент'))
			i=1
			for itm in par['cyclo']:
				worksheet.write_column(8, i, itm)
				i+=1
			#worksheet.write_row(6, 0, par['cyclo'], 0)
			
			print(par['cyclo'])

		def newsheet(workbook, buf, cnt):
			nd = len(buf)
			if nd:
				headform = workbook.add_format()
				headform.set_text_wrap();
				headform.set_align('top');
				
				shnm = 'Cycle{}'.format(cnt)
				# create new worksheet for cycle
				worksheet = workbook.add_worksheet(shnm)
				# Add the worksheet data
				heading=['Обороты вх. вала', 'Момент на вх. валу Н*м', 'Частота вращения вх. вала об./мин', 
					'Момент на вых. валу Н*м', 'Частота вращения вых. вала об./мин']
			
				worksheet.write_row(0, 0, heading, headform)
				worksheet.write_column(1, 0, [i1 for i1,i2,i3,i4,i5 in buf])
				worksheet.write_column(1, 1, [i2 for i1,i2,i3,i4,i5 in buf])
				worksheet.write_column(1, 2, [i3 for i1,i2,i3,i4,i5 in buf])
				worksheet.write_column(1, 3, [i4 for i1,i2,i3,i4,i5 in buf])
				worksheet.write_column(1, 4, [i5 for i1,i2,i3,i4,i5 in buf])

				# Create a new chart object.
				chart1 = workbook.add_chart({'type': 'line'})
				# Add a chart title and some axis labels.
				chart1.set_title ({'name': 'Частота вращения вала'})
				chart1.set_x_axis({'name': 'Обороты'})
				chart1.set_y_axis({'name': 'Частота вращения вала, об/мин'})
				# Add a series to the chart.
				# [sheetname, first_row, first_col, last_row, last_col]
				chart1.add_series(
					{'name': [shnm, 0, 2],
					'values': [shnm,1,2,nd+1,2],
					'categories': [shnm, 1,0,nd+1,0]}
				) 
				chart1.add_series(
					{'name': [shnm, 0, 4],
					'values': [shnm,1,4,nd+1,4],
					'categories': [shnm, 1,0,nd+1,0]}
				) 				
				
				# Create a new chart object.
				chart2 = workbook.add_chart({'type': 'line'})
				# Add a chart title and some axis labels.
				chart2.set_title ({'name': 'Момент на валу'})
				chart2.set_x_axis({'name': 'Обороты'})
				chart2.set_y_axis({'name': 'Момент на валу, Н*м'})
				# Add a series to the chart.
				# [sheetname, first_row, first_col, last_row, last_col]
				chart2.add_series(
					{'name': [shnm, 0, 1],
					'values': [shnm,1,1,nd+1,1],
					'categories': [shnm, 1,0,nd+1,0]}
				) 
				chart2.add_series(
					{'name': [shnm, 0, 3],
					'values': [shnm,1,3,nd+1,3],
					'categories': [shnm, 1,0,nd+1,0]}
				) 								
				
				# Insert the chart into the worksheet.
				worksheet.insert_chart('J1', chart1)
				worksheet.insert_chart('J20', chart2)
		
		def reportloop(svdec):
			self.logProc('Формирование отчета...\n')
				
			lzd = lzma.LZMADecompressor()
			fz = open("tlm.xz", 'rb')
			dd = b''
			
			workbook = xlsxwriter.Workbook('report.xlsx')
			
			titlesheet(workbook, self.cmdParam, 0)

			chunksz = 6
			bufsz=1024
			cycCnt = 0
			cycBuf = []
			while not lzd.eof:
				cd = b''
				if lzd.needs_input:
					cd = fz.read(bufsz)

				dd += lzd.decompress(cd, 4*chunksz)
				if not lzd.needs_input:
					while int(len(dd)/4) >= chunksz:
						chunk = struct.unpack('iiffff', dd[:chunksz*4])
						dd = dd[chunksz*4:]
						#print(chunk)

						if cycCnt == chunk[0]:
							cycBuf.append(chunk[1:])
						else:
							# data of the new cycle begin here
							if (cycCnt==1) or (cycCnt%svdec == 0):
								newsheet(workbook, cycBuf, cycCnt)
							cycCnt = chunk[0]
							cycBuf = [chunk[1:],]
			fz.close()
			newsheet(workbook, cycBuf, cycCnt)
			workbook.close()
			self.logProc('Отчет готов\n')
		
		svmod = self.cboxSaveMode.current()
		if svmod < 0:
			self.logProc('Ошибка. Не выбран режим сохранения результатов\n')
			return
		svdec = 10**svmod
		
		if (None==self.reportThr) or (not self.reportThr.isAlive()):
			self.reportThr = threading.Thread(target=reportloop, args=(svdec,), daemon=True)
			self.reportThr.start()
		else:
			self.logProc('Ошибка. Формирование отчета не закончено\n')

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
		self.cmdParam['cmd'] = CmdEnum.PAUSE
		
		with self.cmdCondition:
			self.cmdQueue.append(self.cmdParam)
			self.cmdCondition.notifyAll()
		
	def stopproc(self):
		print('stop proc')
		self.cmdParam['cmd'] = CmdEnum.STOP
		
		with self.cmdCondition:
			self.cmdQueue.append(self.cmdParam)
			self.cmdCondition.notifyAll()		
		
	def startproc(self):
		print('start proc')
		self.cmdParam['savemod'] = self.cboxSaveMode.current()
		self.cmdParam['numcyc'] = self.numCycles.get()
		self.cmdParam['cmd'] = CmdEnum.START
		print(self.cmdParam)
		
		with self.cmdCondition:
			self.cmdQueue.append(self.cmdParam)
			self.cmdCondition.notifyAll()
		
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
			self.logProc('Запись успешно загружена из базы данных\n')
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
