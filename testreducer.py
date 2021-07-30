#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter
import math
import time
import threading
from mainapp import MainApp
import hashlib
import os
import select
import socket
import math
from modbus_udp import ModbusUdpClient
import lzma
import struct
import configparser
from trgdef import CmdEnum

#mainApp = 0

def msgLoop(args):

	def uns2sig(x):
		if x > 0x7fffffff:
			 x = x - 4294967296
		return x

	def msg2mon(msg,cmd):
		
		fsmlst = ['Ожидание запуска...', 'Выполнение цикла...', 'Завершение цикла...', 'Ожидание продолжения...', 'Сброс счетчика...']
		
		fsmmode = 0
		mon = []
		tlmb = b''
		if len(msg) >= 16:
			
			rot1 = uns2sig(msg[0]*(2**16) + msg[1])
			tor1 = uns2sig(msg[2]*(2**16) + msg[3])*(2**-8)
			spd1 = uns2sig(msg[4]*(2**16) + msg[5])*(2**-8)
			rot2 = uns2sig(msg[6]*(2**16) + msg[7])
			tor2 = uns2sig(msg[8]*(2**16) + msg[9])*(2**-8)
			spd2 = uns2sig(msg[10]*(2**16) + msg[11])*(2**-8)

			mon = [0,0]
			mon.append( rot1 )										# number of rotates at input
			mon.append( tor1 )										# input torque
			mon.append( spd1 )										# input speed rpm from rps
			mon.append( rot2 )										# number of rotates at output
			mon.append( tor2 )										# output torque
			mon.append( spd2 )										# output speed rpm from rps

			fsmmode = msg[15]
			if msg[15] < 5:
				mon.append( fsmlst[msg[15]] )						# fsm mode
			else:
				mon.append('')

			if cmd:
				numcyc = cmd.get('numcyc')
				cyccnt = msg[12]*(2**16) + msg[13] 					# cyc counter
				
				rot = abs(mon[2])
				maxrot = cmd.get('numrot_in')
				
				mon[0] = min(100,100*(numcyc-cyccnt)/numcyc)		# percentage of test progress
				mon[1] = min(100,100*rot/maxrot)					# percentage of current cycle progress
				
				tlmb = struct.pack('iiffff', numcyc-cyccnt+1, rot1, tor1, spd1, tor2, spd2)
		
		fact = 0
		if fsmmode == 1 or fsmmode == 2:
			fact = 1
		return fact,mon,tlmb

	def cmd2msg(cmd):
		
		def swp32(inw):
			return [(inw>>16)&0xffff, inw&0xffff]

		msg = swp32(cmd.get('numcyc'))
		y=cmd.get('speed_in')
		msg += swp32(int(y*(2**8) + 0.5))
		msg += swp32(cmd.get('numrot_in'))
		y = cmd.get('max_torque_out')
		msg += swp32(int(y*(2**8) + 0.5))
		cyc = cmd.get('cyclo')
		msg += [i for i,j in cyc]
		msg += [j for i,j in cyc]
		
		return msg

	config = configparser.ConfigParser()
	config.read('test.ini')

	ipcont = '10.0.0.1'
	if 'CONTROLLER' in config:
		ipcont = config['CONTROLLER']['IP']
		#print(ipcont)

	#modbusClient = ModbusUdpClient('10.1.0.2', 502, 17)
	modbusClient = ModbusUdpClient(ipcont, 502, 17)
	curCmd = {}

	tlmFileName = 'tlm.xz'
	#tlmFd = open(tlmFileName, mode='wb')
	#tlmFd.close()
	tlmFd = None
	
	lzc = lzma.LZMACompressor()

	while True:
		
		cmd = {}
		with mainApp.setupApp.cmdCondition:
			tmo = mainApp.setupApp.cmdCondition.wait(timeout=0.5)
			if mainApp.setupApp.cmdQueue:
				cmd = mainApp.setupApp.cmdQueue.pop(0)
				print("get the command from queue {}".format(cmd['cmd']))
		
		if not tmo:
			print("condition timeout occurs")
		
		# read command
		if cmd:
			if cmd.get('cmd') == CmdEnum.START:
				curCmd = cmd
				regs = [1,] + cmd2msg(cmd)
				if modbusClient.pdu_write_holding_registers(0x0000, regs):
					mainApp.updateLogMsg('Команда доставлена в контроллер\n')
				else:
					mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
			elif cmd.get('cmd') == CmdEnum.PAUSE:
				if modbusClient.pdu_write_holding_registers(0x0000, [2,]):
					mainApp.updateLogMsg('Команда доставлена в контроллер\n')
				else:
					mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
			elif cmd.get('cmd') == CmdEnum.STOP:
				if modbusClient.pdu_write_holding_registers(0x0000, [3,]):
					mainApp.updateLogMsg('Команда доставлена в контроллер\n')
				else:
					mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
			elif cmd.get('cmd') == CmdEnum.EXIT:
				return
			elif cmd.get('cmd') == CmdEnum.SETPAR:
				if modbusClient.pdu_write_holding_registers(0x0020, cmd.get('dat')):
					mainApp.updateLogMsg('Команда доставлена в контроллер\n')
				else:
					mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
		
		# read telemetry
		fres,regs = modbusClient.read_fifo_queue(0x200)
		if not fres:
			try:
				mainApp.updateLogMsg('Ошибка2: контроллер не отвечает\n')
			except RuntimeError:
				return
		elif regs:
			#print(regs)
			
			tlmBuffer = b''
			i = 0
			while True:
				fact,monpar,tlmchunk = msg2mon(regs[i:],curCmd)
				if monpar:
					#print(monpar)
					if fact:
						if (not tlmFd) or tlmFd.closed:
							mainApp.updateLogMsg('Испытание запущено\n')
							tlmFd = open(tlmFileName, 'wb')
							lzc = lzma.LZMACompressor()
						tlmBuffer += tlmchunk
					else:
						if tlmFd and (not tlmFd.closed):
							mainApp.updateLogMsg('Испытание завершено\n')
							tlmFd.write(lzc.compress(tlmBuffer))
							tlmFd.write(lzc.flush())
							tlmBuffer = b''
							tlmFd.close()
					try:
						mainApp.monitorApp.update(monpar)
						mainApp.oscillApp1.updateBuf(monpar[3], monpar[4])
						mainApp.oscillApp2.updateBuf(monpar[6], monpar[7])
					except RuntimeError:
						pass
				else:
					# if tlm file is ready to be writen and there is data in buffer
					if tlmFd and (not tlmFd.closed) and len(tlmBuffer):
						print(len(tlmBuffer))
						print(tlmFd.closed)
						tlmFd.write(lzc.compress(tlmBuffer))
					break;
				i += 16

def main():
	global bufTorIn
	global mainApp
	
	root = tkinter.Tk()	
	mainApp = MainApp(root)
	
	thrTimer = threading.Thread(target=msgLoop, args=(1,), daemon=True)
	thrTimer.start()
	#threading.get_ident()
	
	root.mainloop()
	
	with mainApp.setupApp.cmdCondition:
		mainApp.setupApp.cmdQueue.append({'cmd':CmdEnum.EXIT})
		mainApp.setupApp.cmdCondition.notifyAll()
		
	thrTimer.join()

if __name__ == '__main__':
	main()
