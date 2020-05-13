import json
from sys import exit

class Config:
	def __init__(self):
		self.configfile = 'config.json'
		self.load()

	def load(self):
		with open(self.configfile, 'r') as config_file:
			self.config = json.load(config_file)

	def get(self, entry):
		try:
			return self.config[entry]
		except KeyError as error:
			print('Error: {} not found in {}'.format(error, self.configfile))
			exit()
