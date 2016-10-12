import json
import requests
import pickle
import copy
from random import randint
from .config import *
from .libjmf import *


class User():
	loginpage = 'https://website.com/login.php'

	def __init__(self, username=None):
		self.session = requests.session()

	def __str__(self):
		return self.identity()

	def login(self, username, password):
		data = {'username': username,
			'password': password,
			'keeplogged': '1'}
		self.session.post(self.loginpage, data=data)
		return self.logged_in()

	def logged_in(self):
		try:
			page = json.loads(self.session.get('https://website.com/api.php?action=openings&search=sf938jf').text)
			test = page['status'] == 'success'
		except:
			test = False
		return test

	def index(self):
		if self.logged_in():
			return json.loads(self.session.get('https://website.com/api.php?action=index').text)

	def identity(self):
		return self.index()['response']['username']

	def ratio(self):
		return self.index()['response']['username']

	def save_session(self):
		session_file = open('user_session.pkl', 'wb')
		pickle.dump(self, session_file)
		session_file.close()

	def load_session(self):
		try:
			session_file = open('user_session.pkl', 'rb')
			user = pickle.load(session_file)
			session_file.close()
		except FileNotFoundError:
			user = None
		return user


class Opening():
	def __init__(self, json_data):
		""" Openings are instantiated from opening search results, NOT from an
		individual API reply for a specific opening.
		"""
		self.authors, self.media, self.encodings, self.formats = {}, {}, {}, {}
		self.id = json_data['openingId']
		self.url = 'https://website.com/openings.php?action=view&id=' + str(self.id)
		self.api_url = 'https://website.com/api.php?action=opening&id=' + str(self.id)
		self.title = h.unescape(json_data['title'])
		self.filled = json_data['isFilled']
		self.size = json_data['size']
		self.description = unBB(h.unescape(json_data['description']))
		self.year = json_data['year']
		self.log, self.cert, self.log_score = self.log_cert(json_data['logCert'])
		self.bad = False
		self.api_url = 'https://website.com/api.php?action=opening&id=' + str(self.id)
		self.url = 'https://website.com/openings.php?action=view&id=' + str(self.id)
		for author_group in json_data['authors']:
			for author in author_group:
				self.authors.setdefault(h.unescape(author['name']), 1)
		for data_type, identifier in [('self.formats', 'formatList'), ('self.media', 'mediaList'), ('self.encodings', 'encodingList')]:
			exec("%s = parse_bars(json_data[\'%s\'])" % (data_type, identifier))

	def log_cert(self, log_cert):
		log = 'Log' in log_cert
		cert = 'Cert' in log_cert
		if '%' in log_cert:
			pre_cent = log_cert.split('(')[1].split('%')[0]
			if '=' in pre_cent:
				log_score = int(pre_cent.split(' ')[1])
			else:
				log_score = int(pre_cent)
		else:
			log_score = 0
		return log, cert, log_score
		
	def __str__(self):
		""" Brief overview listing string. """
		return c.c + str(self.title) + c.end + ' - ' + self.url + '\n'

	def verbose(self):
		""" A more verbose alternative to __str__ for match review. """
		log_cert = 'None'
		t = c.c+c.bold+ 'Opening: ' + str(self.title) + c.end
		u = self.url
		v = c.bold+'Size: '+c.end + legible(self.size)
		a = c.bold+'Authors: '+c.end + ', '.join([item for item in self.authors])
		f = c.bold+'Formats: '+c.end + ', '.join([item for item in self.formats])
		b = c.bold+'Encodings: '+c.end + ', '.join([item for item in self.encodings])
		m = c.bold+'Media: '+c.end + ', '.join([item for item in self.media])
		d = c.bold+'Description: '+c.end + self.description
		if self.log == True:
			log_cert = 'Log ' + str(self.log_score) + '%'
		if self.cert == True:
			log_cert += ' + Cert'
		l = c.bold+'VM Requirements: '+c.end + log_cert
		return '\n'.join([t, u, v, a, f, b, m, l, d])

	def url_set(self):
		""" Not sure why I ever had this outside of __init__. Keeping for now in
		case I realize why I had it in the first place.
		"""
		self.api_url = 'https://website.com/api.php?action=opening&id=' + str(self.id)
		self.url = 'https://website.com/openings.php?action=view&id=' + str(self.id)
		return self.url

	def is_filled(self, user):
		""" Check fill status of the opening. Account for possibly deleted
		openings as well as possible errors in fetching the opening.
		"""
		#self.url_set()
		opening_page = user.session.get(self.api_url).text
		json_data = json.loads(opening_page)
		try:
			status = json_data['response']['isFilled']
			self.bad = False
			return status
		except KeyError as e:
			log_print('KeyError: Failed to check fill status for opening #' + str(self.id) + ' because: ' + str(e))
			return False
		except TypeError as e:
			if user.logged_in():
				# Redo everything to make sure we didn't screw up.
				opening_page = user.session.get(self.api_url).text
				json_data = json.loads(opening_page)
				dead = {'status': 'failure', 'response': []}
				if json_data == dead and self.bad == True:
					log_print('Opening #' + str(self.id) + ' no longer exists. Removing . . .')
					return True
				elif json_data == dead:
					log_print('Opening #' + str(self.id) + ' may no longer exist. Keeping for now.')
					self.bad = True
					return False
			log_print('TypeError: Failed to check fill status for opening #' + str(self.id) + ' because: ' + str(e))
			print('Debugging info:\n' + json_data)
			return False

class Listing():
	def __init__(self, json_data, group):
		self.id = json_data['listingId']
		self.format = json_data['format']
		self.encoding = json_data['encoding']
		self.medium = json_data['media']
		self.log = json_data['hasLog']
		self.cert = json_data['hasCert']
		self.log_score = int(json_data['logScore'])
		self.group = group
		self.url = 'https://website.com/listings.php?id=' + str(self.group.id) + '&listingid=' + str(self.id)
		for author in json_data['authors']:
			group.authors.setdefault(h.unescape(author['name']), 1)

	def __str__(self):
		return self.medium +', '+ self.format +', '+ self.encoding  #+ self.authors

	def match(self, opening):
		""" Determines if an opening matches this listing.
		Returns 2 if perfect match, 1 if poor match, 0 if no match.
		"""
		f_match = opening.formats.get(self.format, 0)
		b_match = opening.encodings.get(self.encoding, 0)
		m_match = opening.media.get(self.medium, 0)
		t_match = self.group.title.lower() == opening.title.lower()
		a_match, l_match, self_titled = False, False, False
		if self.medium == 'VM':
			bad_log = bad_cert = False
			if opening.log:
				bad_log = not self.log or self.log_score < opening.log_score
			bad_cert = opening.cert and not self.cert
			l_match = not bad_log and not bad_cert
		for author in self.group.authors:
			self_titled = self.group.title.lower() == author.lower()
			a_match = opening.authors.get(author, a_match)
		if f_match and b_match and m_match and a_match and l_match and not opening.filled:
			if t_match:
				return 2
			elif not self_titled:
				return 1
			else:
				log_print('Self referential: ' + self.url)
		return 0


class ListingGroup():
	def __init__(self, json_data):
		self.authors, self.media, self.encodings, self.formats = {}, {}, {}, {}
		self.listings  = []
		self.openings = [{}, {}]		# poor, good
		self.id = json_data['groupId']
		self.url = 'https://website.com/listings.php?id=' + str(self.id)
		self.title = h.unescape(json_data['groupName'])
		try:
			for listing in json_data['listings']:
				self.listings.append(Listing(listing, self))
		except KeyError:
			pass 		# some weird listings don't behave, ignore them

	def __str__(self):
		s = self.stringify()
		head = c.bold + 'Title: ' + c.end+c.y + self.title + c.end + '\n'
		return head + self.url + s.subhead + s.reqs + '\n'

	def verbose(self, verbose=True):
		s = self.stringify()
		return s.head + s.authors + self.url + s.subhead + s.reqs + '\n'

	def stringify(self):
		s = Blank()
		s.authors = c.bold + 'Authors: ' + c.end + ', '.join([author for author in self.authors]) + '\n'
		s.head = c.bold+c.y + center('== Listing Group: ' + self.title + ' ==', ' ') + c.end
		s.subhead = c.bold + '\nMatching Openings:\n' + c.end
		s.reqs = ''.join([c.bold+' * '+c.end + str(opening) for opening in self.get_all()])
		return s

	def find_openings(self, user):
		""" Finds openings that can be filled by any listings in this group. """
		r = OpeningSearch(user)
		pluses = self.title.replace(' ', '+')
		done, times = False, 2
		pause()
		while not done:
			try:
				r.search(pluses)
				done = True
			except KeyError:
				print(r)
				log_print('Rate limit exceeded. Pausing ' + str(times*2) + ' seconds.')
				repeat(pause, times)
				times *= 2
		for listing in self.listings:
			for opening in r.results:
				if listing.match(opening) == 2:
					self.add(opening, good=True)
					log_print('--> Match: ' + self.title +' '+ self.url +' '+ opening.url)
				elif listing.match(opening):
					self.add(opening, good=False)
					log_print('--> Poor match: \"' + self.title + '\" ?= \"' + opening.title + '\"')

	def add(self, opening, good=True):
		self.openings[good][opening.id] = copy.deepcopy(opening)

	def remove(self, opening):
		try:
			del self.openings[1][opening.id]
		except KeyError:
			del self.openings[0][opening.id]
		log_print('Removed Opening #' + str(opening.id) + ' from Group #' + str(self.id))

	def get_openings(self, good=True):
		return unindex(self.openings[good])

	def get_all(self):
		return self.get_openings(True) + self.get_openings(False)


class Search():
	def __init__(self, user):
		self.user = user
		self.results = []

	def __str__(self):
		return ''.join([str(result) for result in self.results])

	def verbose(self):
		return ''.join([result.verbose() for result in self.results])

	def raw_search(self, search='', page=1):
		raw = self.user.session.get(self.search_url + str(search) + '&page=' + str(page))
		return json.loads(raw.text)

	def search(self, search='', page=1, tags=''):
		self.index(self.raw_search(search, page))


class OpeningSearch(Search):
	search_url = 'https://website.com/api.php?action=openings&search='
	def index(self, search_result):
		for opening in search_result['response']['results']:
			self.results.append(Opening(opening))


class ListingSearch(Search):
	search_url = 'https://website.com/api.php?action=browse&searchstr='
	def index(self, search_result):
		for listing_group in search_result['response']['results']:
			self.results.append(ListingGroup(listing_group))

	def __str__(self):
		return '\n'.join([group.title + ' - ' + group.url for group in self.results])


class Groups():
	""" A container that holds multiple ListingGroup()s """
	def __init__(self, user):
		self.user = user
		self.groups = {}
	
	def __str__(self):
		return ''.join([str(group) for group in self.get(True)])

	def all(self):
		groups = ''.join([str(group) for group in self.get(True)])
		poor_groups = ''.join([str(group) for group in self.get(False)])
		return self.good_header + groups + self.poor_header + poor_groups

	def add(self, group):
		self.groups[group.id] = copy.deepcopy(group)

	def remove(self, group):
		del self.groups[group.id]
		log_print('Removed Group #' + str(group.id))
		
	def get(self, good=True):
		t = []
		for group in self.get_all():
			if len(group.openings[good]):
				t.append(group)
		return t

	def get_all(self):
		return unindex(self.groups)

	def listing_search(self, term='', page=1):
		t = ListingSearch(self.user)
		t.search(term, page)
		return t


class Match(Groups):
	""" A Groups() specialized towards finding matching openings. """
	good_header = c.g + c.bold + center('', '=') + center('==== GOOD MATCHES ====', ' ') + center('-'*22, ' ') + '\n' + c.end
	poor_header = c.r + c.bold + center('', '=') + center('==== POOR MATCHES ====', ' ') + center('-'*22, ' ') + '\n' + c.end

	def __init__(self, user):
		self.recently_checked = ListingSearch(user)
		self.user = user
		self.groups = {}

	def time_to_match(self, listing_search):
		""" Look at last search and compare results. If less than 10 in common,
		return True so we know to run the next search.
		"""
		overlap = 0
		for new_group in listing_search.results:
			for old_group in self.recently_checked.results:
				if new_group.id == old_group.id:
					overlap += 1
		log_print(str(overlap) + ' groups remain from previous match.')
		if overlap <= 10:
			return True, overlap
		else:
			return False, overlap

	def match(self, listing_search, session):
		for group in listing_search.results:
			group.find_openings(self.user)
			if group.openings != [{}, {}]:
				session.update_session()
				session.matches.add(group)
				session.save_session()
			pause()

	def auto_match(self, session):
		t = self.listing_search()
		time_to_match, overlap = self.time_to_match(t)
		if time_to_match:
			log_print('Running search . . .')
			self.recently_checked = copy.deepcopy(t)
			session.save_session()
			self.match(t, session)
			return
		elif 22 < overlap < 28:
			self.fill_check(session)
		print('Not yet time to search.')

	def explicit_match(self, session, term='', page=1):
		t = self.listing_search(term, page)
		self.match(t, session)

	def multiple_pages(self, pages, session, term='', start_page=1):
		for i in range(start_page, start_page+pages):
			self.explicit_match(session=session, term=term, page=i)

	def random_listings(self, session, pages=1):
		test = ListingSearch(self.user)
		total_pages = test.raw_search()['response']['pages']
		pause()
		for i in range(pages):
			random_page = randint(1, total_pages)
			print('page', random_page)
			self.explicit_match(session=session, page = random_page)

	def fill_check(self, session):
		""" Go through every opening for every listing group, and use
		Opening().is_filled() to check fill state for each.
		"""
		for group in self.get_all():
			for opening in group.get_all():
				pause()
				if opening.is_filled(self.user):
					log_print('Opening #' + str(opening.id) + ' filled.')
					group.remove(opening)
					session.save_session()
			if len(group.get_all()) == 0:
				self.remove(group)
				session.save_session()
