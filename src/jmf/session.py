import pickle
import time
import os
from .config import *
from .libwhat import *
from .api import *


class Session():
	busy = False
	config = os.environ['HOME'] + '/.config/what/'
	def __init__(self):
		self.last_change = self.get_last_change()

	def save_session(self, file='session.pkl'):
		print('Saving . . . ', end='')
		session = self.matches
		session_file = open(config+file, 'wb')
		pickle.dump(session, session_file)
		session_file.close()
		print('done.')
		self.set_last_change()
		self.last_change = self.get_last_change()

	def sure_save(self):
		if self.last_change == self.get_last_change():
			self.save_session()
			return 0
		else:
			warning = True
			prompt = 'Save file was altered by another process during this edit. Are you sure you would like to overwrite?'
			if yn(prompt, 'n') == True:
				self.save_session()
				return 0
			else:
				prompt = 'Would you like to save this session as a new file?'
				if yn(prompt, 'y') == True:
					filename = 'session' + now() + '.pkl'
					self.save_session(filename)
					log_print('Session saved to ' + filename)
				return 1

	def load_session(self):
		try:
			session_file = open(config+'session.pkl', 'rb')
			session = pickle.load(session_file)
			session_file.close()
		except FileNotFoundError:
			session = None
		return session

	def retrieve_session(self):
		session = self.load_session()
		if session == None:
			log_print('No session saved. Initializing empty session.')
		else:
			self.matches = session
			self.user = session.user
			self.last_change = self.get_last_change()
		if self.user.logged_in():
			username = self.user.identity()
			self.prompt = c.bold + c.b + username + c.g + ' > ' + c.end
			log_print('Logged in as ' + username)
		else:
			print('Type \'login\' to log in.')

	def update_session(self):
		session = self.load_session()
		if session == None:
			pass
		else:
			self.matches = session
			self.last_change = self.get_last_change()

	def set_last_change(self):
		last_change_file = open(config+'last_change.pkl', 'wb')
		pickle.dump(now(), last_change_file)
		last_change_file.close()

	def get_last_change(self):
		try:
			last_change_file = open(config+'last_change.pkl', 'rb')
			last_change = pickle.load(last_change_file)
			last_change_file.close()
			return last_change
		except (FileNotFoundError, EOFError) as e:
			print('Error: ' + str(e) + ' (last_change.pkl)')
			return None

	def set_busy(self, busy):
		busy_file = open(config+'busy.pkl', 'wb')
		self.busy = busy
		pickle.dump(busy, busy_file)
		busy_file.close()

	def check_busy(self):
		try:
			busy_file = open(config+'busy.pkl', 'rb')
			busy = pickle.load(busy_file)
			busy_file.close()
			return busy
		except (FileNotFoundError, EOFError) as e:
			print('Warning: ' + str(e) + ' (busy.pkl)')
			return False
