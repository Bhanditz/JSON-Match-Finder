#!/usr/bin/python
import builtins
from what import *

if __name__ == '__main__':
	builtins.interactive = True
	init()
	ui = UI()
	ui.cmdloop()
