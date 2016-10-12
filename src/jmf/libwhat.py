import html.parser
import shutil
import math
import datetime
from .config import *


h = html.parser.HTMLParser()

def center(s, pattern):
	'''
	This creates a bar across the entire page with s in the middle.
	It is complex to ensure symmetry regardless of window/pattern size.
	The right end of the pattern will always butt against string s.
	The outer edges depend on the total number of columns.
	1. Figure out how much room both sides have to fill.
	2. Fill (possibly overfill if len(unit) > 1) both sides with
	pattern in the same direction.
	3. Trim both from left if they overfill.
	4. Add extra character to right's left if total chars to fill is odd.
	--> If we are trimming, do this by reducing trim by one.
	--> If no trimming, do this by actually adding a character.
	5. Flip right side for mirror effect.
	'''
	split_me = shutil.get_terminal_size().columns - len(s)
	fit_in = int(split_me/2)
	shrink_me = int(math.ceil(fit_in/(len(pattern)))) * pattern
	trim_both = len(shrink_me) - fit_in
	add_one = split_me%2
	more = pattern[len(pattern)-add_one:] * (trim_both == 0)
	right_start = trim_both - add_one * (trim_both != 0)
	left = shrink_me[trim_both:]
	right = more + shrink_me[right_start:] 
	return left + s + right[::-1]

def repeat(function, times):
	for i in range(times):
		function()

def legible(size):
	for unit in ['B','KB','MB','GB','TB','PB']:
		if abs(size) < 1000:
			return str(size) + ' ' + unit
		num /= 1000.0

def yn(prompt, preferred='neither'):
	force = preferred.lower() == 'y' or preferred.lower() == 'n'
	if force:
		preference = preferred.lower() == 'y'
		yn_prompt = (preference*' [Y, n]: ') + ((not preference)*' [y, N]: ')
	else:
		yn_prompt = [y, n]
	while 1:
		yn = input(prompt + yn_prompt)
		yes = yn.lower() == 'y' or yn.lower() == 'yes' 
		no = yn.lower() == 'n' or yn.lower() == 'no'
		confused = not no and not yes
		if not confused:
			return yes
		elif force:
			return preference
		else:
			print('You must select either yes or no.')

def unBB(text):
	fixed = ''
	silent = False
	for char in text:
		if char == '[':
			silent = True
		elif char == ']':
			silent = False
		elif silent == False:
			fixed += char
	return fixed

def parse_bars(string):
	organized = {}
	letter_list = []
	for letter in string:
		if letter != '|':
			letter_list.append(letter)
		else:
			organized[''.join(letter_list)] = 1
			letter_list = []
	organized[''.join(letter_list)] = 1
	return organized

def unindex(index):
	undone = []
	for identifier in index:
		undone.append(index[identifier])
	return undone

def now():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_print(s, quiet=False):
	log_file = open(config+'jmf.log', 'a')
	time = str(now())
	if interactive:
		prefix = time + ' - Interactive - '
	else:
		prefix = time + ' - @@@ Service - '
	log_file.write(prefix + s + '\n')
	log_file.close()
	if 'match:' in s.lower():
		match_file = open(config+'match.log', 'a')
		match_file.write(time + s + '\n')
		match_file.close()
	if not quiet:
		print(s)

def init():
	if not os.path.exists(config):
		os.makedirs(config)

class Blank(): pass

class c():
	# rgb
	r = '\033[91m'
	g = '\033[92m'
	b = '\033[94m'
	# cym
	c = '\033[96m'
	y = '\033[93m'
	m = '\033[95m'
	# misc
	p = '\033[95m'		# purple
	w = '\033[97m'		# white
	grey = '\033[90m'	# grey
	k = '\033[90m'		# black
	d = '\033[99m'		# default
	bold = '\033[1m'
	ul = '\033[4m'
	end = '\033[0m'
