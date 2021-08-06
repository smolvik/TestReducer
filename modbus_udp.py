#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import os
import select
import socket
import struct
import sys

class ModbusUdpClient:
	
	def __init__(self, ip, port, uid):
		sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
		sock.connect((ip, port))
		self.sock = sock
		self.unit_id = uid
		
	def set_unit_id(self, uid):
		self.unit_id = uid
	
	def mbap(self, nb):
		m = struct.pack('>H', 0x0001)
		m += struct.pack('>H', 0x0000)
		m += struct.pack('>H', nb)
		m += struct.pack('B', self.unit_id)
		return m

	def execute(self, request):
		self.sock.send(request)
		
		msg = None
		readable, writable, exceptional = select.select([self.sock], [], [], 1.0)		
		if readable:
			for s in readable:
				if s == self.sock:
					try:
						msg = s.recv(1024)
					except:
						print('recv error')
					else:
						#print(msg)
						msg = msg[7:] # make pdu
		else:
			print('modbus timeout')
		return msg

	def pdu_write_holding_registers(self, addrtowrite, regs):
		nrtw = len(regs)
		req = self.mbap(7+2*nrtw)
		req += struct.pack('B', 0x10)			# function code 0x10
		req += struct.pack('>H', addrtowrite)	# starting address
		req += struct.pack('>H', nrtw)			# quantity of registers
		req += struct.pack('B', 2*nrtw)			# byte count
		for r in regs:
			req += struct.pack('>H', r)
		pdu=self.execute(req)
		print(pdu)
		
		resp=()
		if pdu:
			if pdu[0] & 0x80:
				print('modbus error: {}'.format(pdu[1]))
			else:
				resp = struct.unpack('>HH', pdu[1:5])
			
		return resp

	def pdu_read_holding_registers(self, addrtoread, ntoread):
		regs = []		
		req = self.mbap(6)
		req += struct.pack('B', 0x03)			# function code 0x03
		req += struct.pack('>H', addrtoread)	# starting address
		req += struct.pack('>H', ntoread)		# quantity of registers
		pdu=self.execute(req)
				
		if pdu[0] & 0x80:
			print('modbus error: {}'.format(pdu[1]))
		else:
			nmsg = struct.unpack('B', pdu[1:2])
			nreg = int(nmsg[0]/2)
			pform = '>'
			if nreg>0:
				for i in range(nreg):
					pform += 'H'
				regs = struct.unpack(pform, pdu[2:])
			
		return regs		

	def pdu_read_input_registers(self, addrtoread, ntoread):
		regs = []		
		req = self.mbap(6)
		req += struct.pack('B', 0x04)			# function code 0x04
		req += struct.pack('>H', addrtoread)	# starting address
		req += struct.pack('>H', ntoread)		# quantity of registers
		pdu=self.execute(req)
						
		if pdu[0] & 0x80:
			print('modbus error: {}'.format(pdu[1]))
		else:
			nmsg = struct.unpack('B', pdu[1:2])
			nreg = int(nmsg[0]/2)
			pform = '>'
			if nreg>0:
				for i in range(nreg):
					pform += 'H'
				regs = struct.unpack(pform, pdu[2:])
			
		return regs

	def read_fifo_queue(self, adrfifo):
		regs = []		
		req = self.mbap(4)
		req += struct.pack('B', 0x18)		# function code
		req += struct.pack('>H', adrfifo)	# fifo pointer address
		pdu=self.execute(req)
		#print(pdu)
		fres = False
		if pdu:
			if pdu[0] & 0x80:
				print('modbus error: {}'.format(pdu[1]))
			elif (len(pdu)>=5) and (pdu[0] == 0x18):
				fres = True
				nmsg = struct.unpack('>HH', pdu[1:5])
				nreg = nmsg[1]
				pform = '>'
				if nreg>0:
					for i in range(nreg):
						pform += 'H'
					regs = struct.unpack(pform, pdu[5:])
			
		return fres,regs
