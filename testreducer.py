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

servIP = '127.0.0.1'
servPort = 48801

cliIP = '127.0.0.1'
cliPort = 48801

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
	
	# create datagram socket
	udpsock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
	# bind socket to port
	udpsock.bind(('', cliPort))
	# connect udp to remote address
	udpsock.connect((servIP, servPort))

	while True:
		time.sleep(.1)
		#readable, writable, exceptional = select.select([udpsock], [], [], 0.1)

		cmd = {}
		
		if mainApp.setupApp.cmdQueue:
			cmd = mainApp.setupApp.cmdQueue.pop(0)
			
		if cmd.get('cmd') == mainApp.setupApp.CmdEnum.EXIT:
			return
		
		monpar = updateFSM(cmd)
		if monpar:
			mainApp.monitorApp.update(monpar)

def main():
	global bufTorIn
	global mainApp
	
	root = tkinter.Tk()	
	mainApp = MainApp(root)
	
	thrTimer = threading.Thread(target=timerLoop, args=(mainApp.setupApp.timerFlag,), daemon=True)
	thrTimer.start()
	#threading.get_ident()
	
	root.mainloop()
	
	mainApp.setupApp.cmdQueue.append({'cmd':mainApp.setupApp.CmdEnum.EXIT})
	thrTimer.join()

if __name__ == '__main__':
	main()
