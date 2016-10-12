import time
import os
from .config import *
from .libjmf import *
from .api import *
from .session import *

class Service(Session):
	def __init__(self):
		log_print('Initializing service.')
		self.user, self.matches = User(), Match(User())
		self.retrieve_session()

	def run(self):
		if not self.user.logged_in():
			log_print('Search canceled! No user is logged in. Please login for the service to work.')
		else:
			this_session = self
			pause()
			self.matches.auto_match(this_session)
		log_print('Service terminated.')

	def busy_loop(self):
		# 200 seconds
		for i in range(20):
			if not self.check_busy():
				self.set_busy(True)
				self.run()
				self.set_busy(False)
				break
			else:
				log_print('Session currently busy elsewhere, waiting 10 seconds.')
				time.sleep(10)
