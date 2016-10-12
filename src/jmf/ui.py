import cmd
import getpass
import time
import os
import argparse
from .config import *
from .libjmf import *
from .api import *
from .session import *


class Help():
	def help_login(self):
		print('usage: login [username]\n')
		print('Logs into an account.\n')

	def help_logout(self):
		print('usage: logout\n')
		print('Ends the user session without exiting the shell.\n')

	def help_exit(self):
		print('usage: exit\n')
		print('Exits the shell without logging out.\n')

	def help_py(self):
		print('usage: py [python code]\n')
		print('Execute arbitrary python code with access to this program\'s classes and session state in a non-persistent environment.\n')

	def help_shell(self):
		print('usage: shell [shell command] OR ![shell command]\n')
		print('Executes shell command in a non-persistent environment.\n')

	def help_print(self):
		print('usage: print [text]\n')
		print('Simple text printer.\n')

	def help_match(self):
		self.onecmd('match -h')

	def help_search(self):
		self.onecmd('search -h')

	def help_log(self):
		self.onecmd('log -h')


class Args():
	# parser.add_argument('-', '--', action='store_true', default=False, help='.')
	def parse_line(self, line):
		''' This splits a string into a list of strings.
		The string is split at spaces next to words
		that start with the character '-'.
		'view -rs apple banana --pages 2' becomes:
		['view', '-rs', 'apple banana', '--pages', '2'] '''
		s, t, i = '', [], 0
		last_char_was_space = last_word_was_dash = False
		for char in line:
			is_dash = char == '-'
			is_space = char == ' '
			if not is_space:
				if last_char_was_space and not is_space:
					if not last_word_was_dash and not is_dash:
						s += ' ' + char
					else:
						if s != '':
							t.append(s)
						s = char
				elif not is_space:
					s += char
				if i == 0 or last_char_was_space:
					i = 1
					last_word_was_dash = is_dash
			last_char_was_space = is_space
		t.append(s)
		if t == ['']:
			return None
		return t

	def match_args(self, line):
		# Parent parser
		parser = argparse.ArgumentParser(prog='match', description='Finds openings that match listings.')
		subparsers = parser.add_subparsers(help='Use one of these subcommands.')
		# Find subparser
		parser_find = subparsers.add_parser('find', help='Find new matches.')
		parser_find.add_argument('-s', '--search', default='', help='Specify a search term.')
		parser_find.add_argument('-p', '--pages', type=int, default=1, help='Number of pages.')
		parser_find.add_argument('-i', '--initial_page', type=int, default=1, help='Page to start from.')
		parser_find.add_argument('-r', '--random', action='store_true', default=False, help='Use random pages.')
		# View subparser
		parser_view = subparsers.add_parser('view', help='View matches.')
		parser_view.add_argument('-a', '--all', action='store_true', default=False, help='View all matches instead of only best matches.')
		parser_view.add_argument('-r', '--review', action='store_true', default=False, help='Review and edit matches.')
		parser_view.add_argument('-s', '--skip-check', action='store_true', default=False, help='Skip the opening fill check.')
		# Update subparser
		parser_update = subparsers.add_parser('update', help='Update matches by removed filled openings.')
		# ...
		parsed_line = self.parse_line(line)
		command = parsed_line[0]
		try:
			args = parser.parse_args(parsed_line)
		except SystemExit:
			args = command = None
		return command, args

	def search_args(self, line):
		parser = argparse.ArgumentParser(prog='search', description='Finds openings or listings.')
		group = parser.add_mutually_exclusive_group()
		group.add_argument('-r', '--opening', default='', help='Search openings. Specify a search term.')
		group.add_argument('-t', '--listing', default='', help='Search listings. Specify a search term.')
		parser.add_argument('-p', '--pages', type=int, help='Number of pages.')
		parser.add_argument('-i', '--initial_page', type=int, help='Page to start from.')
		try:
			args = parser.parse_args(self.parse_line(line))
		except SystemExit:
			return
		return args

	def log_args(self, line):
		parser = argparse.ArgumentParser(prog='log', description='Print application log.')
		parser.add_argument('-f', '--find', default='', help='Print only lines containing search string.')
		# Argument group deciding type of output.
		log_type = parser.add_argument_group('Output Type', 'Using any of these options will limit output to explicitly declared log types.')
		log_type.add_argument('-s', '--service', action='store_true', default=False, help='Explicitly declare service logs.')
		log_type.add_argument('-i', '--interactive', action='store_true', default=False, help='Explicitly declare interactive logs.')
		log_type.add_argument('-m', '--matches', action='store_true', default=False, help='Explicitly declare match logs.')
		# Argument group deciding length of output.
		length = parser.add_mutually_exclusive_group()
		length.add_argument('-a', '--all', action='store_true', default=False, help='Do not limit log output length.')
		length.add_argument('-l', '--lines', type=int, default=100, help='Specify output length. Default is 100 lines.')
		try:
			args = parser.parse_args(self.parse_line(line))
		except SystemExit:
			return
		return args


class UI(cmd.Cmd, Help, Session, Args):
	prompt = c.bold + c.g + '> ' + c.end
	def __init__(self):
		log_print('Initializing interactive session.', True)
		cmd.Cmd.__init__(self)
		self.user, self.matches = User(), Match(User())
		self.onecmd('help')
		self.retrieve_session()

	def cmdloop(self):
		try:
			cmd.Cmd.cmdloop(self)
		except KeyboardInterrupt as e:
			#if self.busy:
			#	busy = False
			print()
			self.cmdloop()

	def precmd(self, line):
		self.update_session()
		return line

	def do_login(self, username):
		self.update_session()
		if username == '':
			username = input('Username: ')
		password = getpass.getpass()
		self.user = User()
		self.user.login(username, password)
		if self.user.logged_in():
			self.prompt = c.bold + c.b + username + c.g + ' > ' + c.end
			self.matches.user = self.user
			self.sure_save()
			log_print('Fresh login as ' + username)
		elif not self.user.logged_in():
			print('Incorrect username or password for ' + username)
		else:
			log_print('error: Login check failure.')

	def do_logout(self, line):
		self.update_session()
		self.user = User()
		self.matches.user = User()
		self.sure_save()
		self.prompt = c.bold + c.g + '> ' + c.end

	def do_search(self, line):
		args = self.search_args(line)
		try:
			if args.opening != None:
				self.openings = OpeningSearch(self.user)
				self.openings.search(args.opening)
				print(self.openings)
			elif args.listing != None:
				self.listings = ListingSearch(self.user)
				self.listings.search(args.listing)
				print(self.listings)
			else:
				print('Please select a search type.')
		except:
			return

	def do_match(self, line):
		try:
			command, args = self.match_args(line)
		except TypeError:
			command = None
		if command == 'find':
			log_print('Explicit search: ' + line, True)
			self.find_matches(args)
		elif command == 'view':
			self.view_matches(args)
		elif command == 'update':
			self.matches.fill_check(self)
			self.sure_save()

	def find_matches(self, args):
		print('Please be patient. Due to API rate limits, each full page takes seven minutes.')
		if args.random:
			self.matches.random_listings(args.pages)
		else:
			self.matches.multiple_pages(pages=args.pages, session=self, term=args.search, start_page=args.initial_page)

	def view_matches(self, args):
		if args.all and not args.review:
			print(self.matches.all())
		elif not args.review:
			print(self.matches)
		elif args.review:
			if not args.skip_check:
				log_print('Removing filled openings . . .')
				self.matches.fill_check(self)
			log_print('Initializing manual match review.', quiet=True)
			print(self.matches.good_header)
			self.review_matches()
			if args.all:
				print(self.matches.poor_header)
				self.review_matches(good=False)

	def review_matches(self, good=True):
		for group in self.matches.get(good):
			self.last_change = self.get_last_change()
			yn = ''
			good_color = c.g*good + c.r*(1-good)
			print(group.verbose())
			if len(group.get_openings(good)) > 1:
				yn = input(c.b+c.bold+ ':: ' +c.w+ 'Keep this group? [Y, n]: ' +c.end)
			if yn.lower() == 'n' or yn.lower() == 'no':
				self.matches.remove(group)
				if self.sure_save() == 1:
					break
			else: 
				for opening in group.get_openings(good):
					self.last_change = self.get_last_change()
					yn = ''
					print(center('-', '- ') + '\n')
					print(opening.verbose())
					yn = input(c.b+c.bold+ ':: ' +c.w+ 'Keep this match? [Y, n]: ' + c.end)
					if yn.lower() == 'n' or yn.lower() == 'no':
						group.remove(opening)
						if self.sure_save() == 1:
							break
			if len(group.get_all()) == 0:
				self.matches.remove(group)
				if self.sure_save() == 1:
					break
			print('\n' + c.bold + good_color + center('', '=') + c.end)

	def do_log(self, line):
		args = self.log_args(line)
		try:
			log_file = open(config+'jmf.log', 'r')
			raw_log = log_file.read()
			log_file.close()
			log = self.log_parse(raw_log, args)
		except FileNotFoundError:
			log = 'No log found.'
		except AttributeError:
			log = ''
		print(log)

	def log_parse(self, log, args):
		t, t2 = [], []
		log_list = log.split('\n')
		if args.service or args.interactive or args.matches:
			for line in log_list:
				if args.service and 'Service' in line:
					t.append(line)
				elif args.interactive and 'Interactive' in line:
					t.append(line)
				elif args.matches and '-->' in line:
					t.append(line)
		else:
			t = log_list
		if args.find != '':
			for line in t:
				if args.find.lower() in line.lower():
					t2.append(line)
		else:
			t2 = t
		size = args.lines + args.all*(len(t) - args.lines)
		return '\n'.join(t2[-size:])

	def do_py(self, string):
		try:
			exec(string)
		except Exception as e:
			print(e)

	def do_shell(self, line):
		ps = os.popen('printf \"$USER ${PWD##*/} \\$"').read()
		print(ps, line)
		output = os.popen(line).read()
		print(output)
		self.last_output = output

	def do_exit(self, line):
		log_print('Exiting interactive session.')
		return True

	def do_print(self, line):
		print(line)
		
	def emptyline(self):
		pass
