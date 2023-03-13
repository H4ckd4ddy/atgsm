import serial
import serial.tools.list_ports
from smspdudecoder.codecs import GSM, UCS2
from os import urandom


class AT:
	@classmethod
	def get_ports_list(cls):
		ports = []
		raw_ports = serial.tools.list_ports.comports()
		for port in raw_ports:
			try:
				port_path = '/dev/{}'.format(port.name)
				device = cls(port_path)
				if device.is_responding():
					ports.append(port_path)
			except:
				pass
		return ports

	@classmethod
	def add_checksum_to_imei(cls, imei):
		reverse = ''.join(reversed(str(imei)))
		total = 0
		for index in range(0, len(reverse), 2):
			sub_total = int(reverse[index])*2
			for digit in str(sub_total):
				total += int(digit)
		for index in range(1, len(reverse), 2):
			total += int(reverse[index])
		return str(imei) + str(10 - (total%10))

	@classmethod
	def check_imei(cls, imei):
		return (str(imei) == cls.add_checksum_to_imei(str(imei)[:-1]))


	def __init__(self, device, baudrate=115200):
		self.queue = []
		self.serial = serial.Serial(device, baudrate=baudrate, timeout=0.1, write_timeout=0.1, inter_byte_timeout=0.1)

	def send_command(self, command):
		queue_id = urandom(4).hex()
		self.queue.append(queue_id)

		while self.queue[0] != queue_id:
			pass

		response = ''

		try:
			self.serial.reset_input_buffer()
			self.serial.reset_output_buffer()
			self.serial.write((command+'\n\r').encode())

			buffer = self.serial.readline()
			if not buffer:
				raise Exception('No reponse from serial device')
			
			response_line = ''
			read_tries = 0
			while 'OK' not in response_line and 'ERROR' not in response_line:
				raw = self.serial.readline()
				if raw:
					response_line = raw.decode('iso-8859-1')
					response += response_line
					read_tries = 0
				else:
					read_tries += 1

				if read_tries >= 3:
					raise Exception('Timeout before end of response')
		except:
			pass

		self.queue.remove(queue_id)
		return response.strip('\r\n')



	################
	#              #
	#    Device    #
	#              #
	################

	def is_responding(self):
		return 'OK' in self.send_command('AT')

	def get_imei(self):
		result = self.send_command('AT+GSN')
		return result.split('\r\n')[0] if 'OK' in result else ''

	def set_imei(self, new_imei):
		return 'OK' in self.send_command('AT+EGMR=1,7,"{}"'.format(new_imei))

	def get_imsi(self):
		result = self.send_command('AT+CIMI')
		return result.split('\r\n')[0] if 'OK' in result else ''

	def get_iccid(self):
		result = self.send_command('AT+QCCID')
		return result.split('\r\n')[0] if 'OK' in result else ''

	def get_signal_strength(self):
		result = self.send_command('AT+CSQ')
		return result.split('\r\n')[0].split(' ')[1].split(',')[0] if result else 0

	def is_network_ready(self):
		return 'QNSTATUS: 0' in self.send_command('AT+QNSTATUS')

	def reboot(self):
		self.send_command('AT+QPOWD=1')


	################
	#              #
	#      SIM     #
	#              #
	################

	def is_sim_locked(self):
		return 'SIM PIN' in self.send_command('AT+CPIN?')

	def unlock_sim(self, pin):
		return 'OK' in self.send_command('AT+CPIN="{}"'.format(pin))

	def change_sim_pin(self, pin, new_pin):
		return 'OK' in self.send_command('AT+CPWD="SC","{}","{}"'.format(pin, new_pin))

	def disable_sim_pin(self, pin):
		return 'OK' in self.send_command('AT+CLCK="SC",0,"{}"'.format(pin))

	def enable_sim_pin(self, pin):
		return 'OK' in self.send_command('AT+CLCK="SC",1,"{}"'.format(pin))

	def reset_sim_pin(self, puk, new_pin):
		return 'OK' in self.send_command('AT+CPIN="{}","{}"'.format(puk, new_pin))



	################
	#              #
	#      SMS     #
	#              #
	################

	def init_sms_configuration(self):
		self.send_command('AT+CMGF=1')
		self.send_command('AT+CPMS="SM","SM","SM"')
		self.send_command('AT+CSCS="8859-1"')

	#def send_sms(self, destination, content):
	#	self.send_command('AT+CMGS={}'.format(destination))
	#	self.send_command(content)
	#	self.serial.write(chr(26))


	def parse_sms(self, raw_sms):
		lines = raw_sms.split('\r\n')
		header = lines[0].split(',')
		raw_content = lines[1].strip('"')
		try:
			content = UCS2.decode(raw_content)
		except:
			content = raw_content
		return {
			'index': header[0].strip('"'),
			'status': header[1].strip('"'),
			'readed': ('UNREAD' not in header[1]),
			'sender': header[2].strip('"'),
			'time': header[4].strip('"'),
			'content': content
		}

	def get_sms_list(self, include_read=False, keep_unread=False):
		self.init_sms_configuration()
		command_filter = "ALL" if include_read else "REC UNREAD"
		mode = 1 if keep_unread else 0
		raw_result = self.send_command('AT+CMGL="{}",{}'.format(command_filter, mode))
		if 'OK' in raw_result:
			raw_list = raw_result.split('OK')[0].split('+CMGL: ')[1:]
			sms_list = []
			for sms in raw_list:
				sms_list.append(self.parse_sms(sms))
			return sms_list
		return []

	def get_sms(self, index, keep_unread=False):
		self.init_sms_configuration()
		mode = 1 if keep_unread else 0
		raw_result = self.send_command('AT+CMGR={},{}'.format(index, mode))
		if 'OK' in raw_result:
			raw_sms = raw_result.split('OK')[0].split('+CMGR: ')[1:][0]
			raw_sms = '{},{}'.format(index, raw_sms)
			return self.parse_sms(raw_sms)
		return {}

	def delete_sms(self, index):
		return 'OK' in self.send_command('AT+CMGD={}'.format(index))

	def delete_all_sms(self, include_unread=False):
		command_filter = "DEL ALL" if include_unread else "DEL READ"
		return 'OK' in self.send_command('AT+QMGDA="{}"'.format(command_filter))



	################
	#              #
	#   Contact    #
	#              #
	################

	def init_contact_configuration(self):
		return 'OK' in self.send_command('AT+CPBS="SM"')

	def get_contact(self, id):
		self.init_contact_configuration()
		result = self.send_command('AT+CPBR={}'.format(id))
		if 'OK' in result:
			array = result.split('\r\n')[0].split(',')
			return {
				'id': id,
				'name': array[3].strip('"'),
				'number': array[1].strip('"')
			}
		return {}

	def set_contact(self, id, name, number):
		return 'OK' in self.send_command('AT+CPBW={},"{}",129,"{}"'.format(id, number, name))



	################
	#              #
	#     Call     #
	#              #
	################
	
	def dial(number):
		return 'OK' in self.send_command('ATD{};'.format(number))

	def answer():
		return 'OK' in self.send_command('ATA')

	def hang_up():
		return 'OK' in self.send_command('ATH')

	def press_key(key):
		return 'OK' in self.send_command('AT+CKPD={}'.format(key))

