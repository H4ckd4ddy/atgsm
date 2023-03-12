# AT-GSM
Python lib for AT GSM commands

## Install

```bash
pip install atgsm
```

## Usage

```python
from atgsm import AT

AT.get_ports_list()
# Ex result: ['/dev/ttyXX1', '/dev/ttyXX2']

# Create new device instance
device = AT('/dev/ttyACM0', baudrate=115200)


############################
# Device related functions #
############################

device.is_responding()
# return boolean (ex: True)

device.get_imei()
# return device IMEI (ex: '000000000000001')

device.get_imsi()
# return SIM IMSI (ex: '000000000000001')

device.get_iccid()
# return SIM ICCID (ex: '00000000000000000001')

device.get_signal_strength()
# return signal strength from 0 to 31 (ex: 12')

device.is_network_ready()
# return boolean (ex: True)


#########################
# SIM related functions #
#########################

device.is_sim_locked()
# return boolean (ex: True)

device.unlock_sim(pin)
# return boolean of success (ex: True)

device.change_sim_pin(actual_pin, new_pin)
# return boolean of success (ex: True)

device.disable_sim_pin(pin)
# return boolean of success (ex: True)

device.enable_sim_pin(pin)
# return boolean of success (ex: True)

device.reset_sim_pin(puk, new_pin)
# return boolean of success (ex: True)


#########################
# SMS related functions #
#########################

device.get_sms_list(include_read, keep_unread)
# - include_read = boolean (include already read messages only if True)
# - keep_unread = boolean (keep messages unread only if True)
# return list of messages dicts, ex :
# [{'index': '1', 'status': 'REC READ', 'readed': True, 'sender': '+33XXXXXXXXX', 'time': '2023/XX/XX XX:XX:XX+XX', 'content': 'This is text'}]

device.get_sms(message_index, keep_unread)
# - message_index = int (index of specific message to get)
# - keep_unread = boolean (keep messages unread only if True)
# return requested message as dict
# {'index': '1', 'status': 'REC READ', 'readed': True, 'sender': '+33XXXXXXXXX', 'time': '2023/XX/XX XX:XX:XX+XX', 'content': 'This is text'}

device.delete_sms(message_index)
# - message_index = int (index of specific message to delete)
# return boolean of success (ex: True)

device.delete_all_sms(include_unread)
# - include_read = boolean (delete also unread messages if True)
# return boolean of success (ex: True)


##############################
# Contacts related functions #
##############################

device.get_contact(contact_id)
# - contact_id = int (id of specific contact to get)
# return requested contact as dict
# {'id': 1, 'name': 'My phone number', 'number': '+33XXXXXXXXX'}

device.set_contact(contact_id, contact_name, contact_phone_number)
# - contact_id = int (id of specific contact to create)
# - contact_name = string (name of contact to create)
# - contact_phone_number = string (phone number of contact to create)
# return boolean of success (ex: True)


###########################
# Calls related functions #
###########################

device.dial(phone_number)
# - phone_number = string (phone number to dial)
# return boolean of success (ex: True)

device.answer()
# (answer to incomming call)
# return boolean of success (ex: True)

device.hang_up()
# (hang up actual call)
# return boolean of success (ex: True)

device.press_key(key)
# - key = string (key to press on keypad during call)
# return boolean of success (ex: True)
```
