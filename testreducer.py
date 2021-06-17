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

mainApp = 0

servIP = '10.1.0.1'
cliIP = '10.1.0.2'

fsmPort = 48801
cntPort = 48802
tlmPort = 48803

'''
def timerLoop(args):
	global bufTorIn
	global mainApp

	def cycinterp(x, y, cyclo):
		for i in range(5):
			if x <= cyclo[i][0]:
				x1 = cyclo[i-1][0]
				x2 = cyclo[i][0]
				y1 = cyclo[i-1][1]
				y2 = cyclo[i][1]
				y = y1+(y2-y1)*(x-x1)/(x2-x1)
				break
		return round(y,2)

	def cycloGen(cmd):
		
		numc = cmd['numcyc']
		numr = cmd['numrot_in']

		speed = cmd['speed_in']
		maxtorque = cmd['max_torque_out']
		cyclo = cmd['cyclo']
		
		perc_cyc = 0
		perc_all = 0
		sumrot = 0
		curtor = 0
		for cntc in range(numc):
			
			for cntr in range(numr):
				perc_cyc = int(100*(cntr+1)/numr)
				sumrot += 1
				curtor = cycinterp(100*cntr/numr, curtor, cyclo)
				
				mainApp.oscillApp1.updateBuf(-curtor, 0.1*curtor+speed)
				mainApp.oscillApp2.updateBuf(curtor, -0.1*curtor-speed)
				yield (perc_cyc, perc_all, sumrot, curtor, speed, sumrot, curtor, speed)
			
			perc_all = int(100*(cntc+1)/numc)
			mainApp.updateLogMsg('Цикл {} завершен\n'.format(cntc+1))
		
		yield (perc_cyc, perc_all, sumrot, curtor, speed, sumrot, curtor, speed)
	
	def waitResumeProc(cmd):
		nonlocal updateFSM 
		print('wait proc')
		com = cmd.get('cmd')
		if com == mainApp.setupApp.CmdEnum.STOP:
			updateFSM = idleProc
			mainApp.updateLogMsg('Испытание прервано\n')
		if com == mainApp.setupApp.CmdEnum.START:
			mainApp.updateLogMsg('Продолжение испытания\n')
			updateFSM = workProc

	def waitProc(cmd):
		nonlocal updateFSM, cyclogen
		print('wait proc')
		com = cmd.get('cmd')
		if com == mainApp.setupApp.CmdEnum.STOP:
			updateFSM = idleProc
			mainApp.updateLogMsg('Испытание прервано\n')
		
		per = next(cyclogen)

		if 100 == per[0]:
			if 100 == per[1]:
				updateFSM = idleProc
				mainApp.updateLogMsg('Испытание завершено\n')
			else:
				updateFSM = waitResumeProc
				mainApp.updateLogMsg('Ожидание продолжения\n')
		
		return per

	def workProc(cmd):
		nonlocal updateFSM, cyclogen
		print('work proc')
		com = cmd.get('cmd')
		if com == mainApp.setupApp.CmdEnum.PAUSE:
			updateFSM = waitProc
			mainApp.updateLogMsg('Ожидание окончания цикла\n')
		if com == mainApp.setupApp.CmdEnum.STOP:
			updateFSM = idleProc
			mainApp.updateLogMsg('Испытание прервано\n')
		
		per = next(cyclogen)
		
		if per[1]==100:
			updateFSM = idleProc
			mainApp.updateLogMsg('Испытание завершено\n')
			
		return per

	def idleProc(cmd):
		nonlocal updateFSM, cyclogen
		
		print('idle proc')
		if cmd.get('cmd') == mainApp.setupApp.CmdEnum.START:
			updateFSM = workProc

			cyclogen = cycloGen(cmd)
			mainApp.updateLogMsg('Испытание запущено\n')
			
	updateFSM = idleProc
	cyclogen = None
	
	while True:

		time.sleep(.1)

		cmd = {}
		
		if mainApp.setupApp.cmdQueue:
			cmd = mainApp.setupApp.cmdQueue.pop(0)
			
			if cmd.get('cmd') == mainApp.setupApp.CmdEnum.EXIT:
				return

		monpar = updateFSM(cmd)
		if monpar:
			mainApp.monitorApp.update(monpar)
'''

def msgLoop(args):

	def cmd2msg(cmd):
		cmdid = cmd.get('cmd')
		msg = cmdid.to_bytes(2,'little')
		
		if cmdid == mainApp.setupApp.CmdEnum.START:
			msg = msg+cmd.get('numcyc').to_bytes(4,'little')

			y=cmd.get('speed_in')
			msg = msg+int(y*(2**8) + 0.5).to_bytes(4,'little')
			msg = msg+cmd.get('numrot_in').to_bytes(4,'little')
			
			y = cmd.get('max_torque_out')
			msg = msg+int(y*(2**8) + 0.5).to_bytes(4,'little')
			
			cyc = cmd.get('cyclo')
			msg = msg+bytearray([i for i,j in cyc])
			msg = msg+bytearray([j for i,j in cyc])

		return msg

	def msg2mon(msg):
		
		mon = [msg[0]]
		mon.append(msg[1])
		mon.append(int.from_bytes(msg[2:6], 'little')) 				# number of rotates at input
		mon.append(int.from_bytes(msg[6:10], 'little')*(2**-8))		# input torque
		mon.append(int.from_bytes(msg[10:14], 'little')*(2**-8))		# input speed
		mon.append(int.from_bytes(msg[14:18], 'little')) 			# number of rotates at output
		mon.append(int.from_bytes(msg[18:22], 'little')*(2**-8))	# output torque
		mon.append(int.from_bytes(msg[22:26], 'little')*(2**-8))	# output speed
		#ts = int.from_bytes(msg[28:32], 'little')		# time stamp
		#crc = int.from_bytes(msg[32:34], 'little')		
		
		print(mon)
		return mon
	
	# create datagram socket
	fsmSock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
	# bind socket to port
	#fsmSock.bind((cliIP, fsmPort))
	# connect to remote address
	#fsmSock.connect((servIP, fsmPort))
	
	tlmSock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
	tlmSock.bind((cliIP, tlmPort))
	##tlmSock.connect((servIP, tlmPort))

	while True:
		
		#time.sleep(.1)
		readable, writable, exceptional = select.select([tlmSock], [], [], 0.1)
		for s in readable:
			if s == tlmSock:
				msg = s.recv(1024)
				monpar = msg2mon(msg)
				print(monpar)
				if monpar:
					curtor = monpar[3]
					speed = monpar[4]
					mainApp.monitorApp.update(monpar)
					mainApp.oscillApp1.updateBuf(-curtor, 0.1*curtor+speed)
					mainApp.oscillApp2.updateBuf(curtor, -0.1*curtor-speed)

		cmd = {}
		if mainApp.setupApp.cmdQueue:
			cmd = mainApp.setupApp.cmdQueue.pop(0)
			lastcmd = cmd
			
			if cmd.get('cmd') == mainApp.setupApp.CmdEnum.EXIT:
				return
			
			fsmSock.sendto(cmd2msg(cmd), (servIP, fsmPort))

def main():
	global bufTorIn
	global mainApp
	
	root = tkinter.Tk()	
	mainApp = MainApp(root)
	
	thrTimer = threading.Thread(target=msgLoop, args=(1,), daemon=True)
	thrTimer.start()
	#threading.get_ident()
	
	root.mainloop()
	
	mainApp.setupApp.cmdQueue.append({'cmd':mainApp.setupApp.CmdEnum.EXIT})
	thrTimer.join()

if __name__ == '__main__':
	main()
