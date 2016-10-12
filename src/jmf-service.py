#!/usr/bin/python
import builtins
from what import *

if __name__ == '__main__':
	builtins.interactive = False
	init()
	service = Service()
	service.run()
