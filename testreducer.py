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

#mainApp = 0

def msgLoop(args):

	def updateSpd(ts, nr):
		if ts:
			if updateSpd.ncurSpd >= updateSpd.nmaxSpd:
				# remove old data
				updateSpd.bufT.pop(0)
				updateSpd.bufC.pop(0)
			else:
				updateSpd.ncurSpd += 1
			
			# add new one
			updateSpd.bufT.append(ts)
			updateSpd.bufC.append(nr)
			
			dc = updateSpd.bufC[-1] - updateSpd.bufC[0]
			dt = updateSpd.bufT[-1] - updateSpd.bufT[0]
			if dt:
				updateSpd.spd = 1000*60*dc/dt

		return updateSpd.spd

	updateSpd.bufT = []
	updateSpd.bufC = []
	updateSpd.ncurSpd=0
	updateSpd.nmaxSpd=20
	updateSpd.spd=0

	def msg2mon(msg,cmd):
			
		mon = []
		if len(msg) >= 16:
			mon = [0,0]
			mon.append( msg[0]*(2**16) + msg[1] )					# number of rotates at input
			mon.append( (msg[2]*(2**16) + msg[3])*(2**-8) )			# input torque
			mon.append( (msg[4]*(2**16) + msg[5])*(2**-8) )			# input speed rpm from rps
			mon.append( msg[6]*(2**16) + msg[7] )					# number of rotates at output
			mon.append( (msg[8]*(2**16) + msg[9])*(2**-8) )			# output torque
			mon.append( (msg[10]*(2**16) + msg[11])*(2**-8) )		# output speed rpm from rps
			
			if cmd:				
				numcyc = cmd.get('numcyc')
				cyccnt = msg[12]*(2**16) + msg[13] 						# cyc counter
				ts = msg[14]*(2**16) + msg[15]							# time stamp
				
				nrot = mon[2]
				
				# ~ if cyccnt:
					# ~ spd=updateSpd(ts,nrot)
				# ~ else: 
					# ~ spd = 0
				# ~ print("time stamp:{}".format(ts))
				# ~ print("speed:{}".format(spd))
				# ~ mon[4] = spd
				
				rot = msg[0]*(2**16) + msg[1]
				maxrot = cmd.get('numrot_in')
				
				mon[0] = min(100,100*(numcyc-cyccnt)/numcyc)
				mon[1] = min(100,100*rot/maxrot)
		
		return mon

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
	
	#modbusClient = ModbusUdpClient('10.1.0.2', 4660, 17)
	modbusClient = ModbusUdpClient('10.0.0.1', 4660, 17)
	curCmd = {}

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
			if cmd.get('cmd') == mainApp.setupApp.CmdEnum.START:
				curCmd = cmd
				regs = [1,] + cmd2msg(cmd)
				if modbusClient.pdu_write_holding_registers(0x0000, regs):
					mainApp.updateLogMsg('Команда доставлена в контроллер\n')
				else:
					mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
			elif cmd.get('cmd') == mainApp.setupApp.CmdEnum.PAUSE:
				if modbusClient.pdu_write_holding_registers(0x0000, [2,]):
					mainApp.updateLogMsg('Команда доставлена в контроллер\n')
				else:
					mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
			elif cmd.get('cmd') == mainApp.setupApp.CmdEnum.STOP:
				if modbusClient.pdu_write_holding_registers(0x0000, [3,]):
					mainApp.updateLogMsg('Команда доставлена в контроллер\n')
				else:
					mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
			elif cmd.get('cmd') == mainApp.setupApp.CmdEnum.EXIT:
				return
		
		# read telemetry
		fres,regs = modbusClient.read_fifo_queue(0x200)
		if not fres:
			try:
				mainApp.updateLogMsg('Ошибка: контроллер не отвечает\n')
			except RuntimeError:
				return
		elif regs:
			#print(regs)
			i = 0
			while True:
				monpar = msg2mon(regs[i:],curCmd)
				if monpar:
					#print(monpar)
					try:
						mainApp.monitorApp.update(monpar)
						mainApp.oscillApp1.updateBuf(monpar[3], monpar[4])
						mainApp.oscillApp2.updateBuf(monpar[6], monpar[7])
					except RuntimeError:
						pass
				else:
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
		mainApp.setupApp.cmdQueue.append({'cmd':mainApp.setupApp.CmdEnum.EXIT})
		mainApp.setupApp.cmdCondition.notifyAll()
		
	thrTimer.join()

if __name__ == '__main__':
	main()
