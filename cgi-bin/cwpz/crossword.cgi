#!/usr/bin/env python
# encoding: utf-8

import random, re, datetime, time, string, sys, traceback, sqlite3, cgi, cgitb
from copy import copy as duplicate
from collections import defaultdict

class BadFormattingError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
 
class Crossword(object):
	def __init__(self, cols, rows, empty = '-', maxloops = 2000, available_words=[]):
		self.cols = cols
		self.rows = rows
		self.empty = empty
		self.maxloops = maxloops
		self.available_words = available_words
		self.randomize_word_list()
		self.current_word_list = []
		self.total_fit_score = 0
		self.this_is_a_seed = True
		self.debug = 0
		self.clear_grid()

		self.letters = defaultdict(list)
 
	def clear_grid(self): # initialize grid and fill with empty character
		self.grid = []
		for i in range(self.rows):
			ea_row = []
			for j in range(self.cols):
				ea_row.append(self.empty)
			self.grid.append(ea_row)
 
	def randomize_word_list(self): # also resets words and sorts by length
		temp_list = []
		for word in self.available_words:
			if isinstance(word, Word):
				temp_list.append(Word(word.word, word.clue, word.clue2, word.synset))
			else:
				temp_list.append(Word(word[0], word[1], word[2], word[3]))
		random.shuffle(temp_list) # randomize word list
		#temp_list.sort(key=lambda i: len(i.word), reverse=True) # sort by length, longest (highest) first
		# the idea is to place the hardest, most unaccommodating words first
		temp_list.sort(key=lambda i: i.scrabble(), reverse=False)
		temp_list.sort(key=lambda i: i.length, reverse=True)
		self.available_words = temp_list
 
	def compute_crossword(self, time_permitted = 1.00, spins=2):
		time_permitted = float(time_permitted)
 
		count = 0
		copy = Crossword(self.cols, self.rows, self.empty, self.maxloops, self.available_words)
 
		start_full = float(time.time())
		while (float(time.time()) - start_full) < time_permitted or count == 0: # only run for x seconds
			self.debug += 1
			copy.current_word_list = []
			copy.total_fit_score = 0
			copy.this_is_a_seed = True
			copy.clear_grid()
			copy.randomize_word_list()
			x = 0
			while x < spins: # spins; 2 seems to be plenty. in a spin, python runs down the word list to see what it can add
				for word in copy.available_words:
					if word not in copy.current_word_list:
						copy.fit_and_add(word)
				x += 1
			#print copy.solution()
			#print len(copy.current_word_list), len(self.current_word_list), self.debug
			# buffer the best crossword by comparing placed words
			if (len(copy.current_word_list) > len(self.current_word_list)) or ( (len(copy.current_word_list) == len(self.current_word_list)) and (copy.total_fit_score > self.total_fit_score) ):
				self.current_word_list = copy.current_word_list
				self.grid = copy.grid
				self.total_fit_score = copy.total_fit_score
			count += 1 # self.debug is the same as count here, to show the total number of cycles (full crosswords generated and compared)
		return
 
	def suggest_coord(self, word):
		count = 0
		coordlist = []

		for glc, given_letter in enumerate(word.word): # cycle through letters in word
			for (colc, rowc) in self.letters[given_letter]:
				if given_letter == self.grid[rowc][colc]:
					try: # suggest vertical placement 
						if rowc - glc >= 0: # make sure we're not suggesting a starting point off the grid
							if ((rowc - glc) + word.length) <= self.rows: # make sure word doesn't go off of grid
								coordlist.append([colc, rowc - glc, 1, colc + (rowc - glc), 0])
					except: pass
					try: # suggest horizontal placement 
						if colc - glc >= 0: # make sure we're not suggesting a starting point off the grid
							if ((colc - glc) + word.length) <= self.cols: # make sure word doesn't go off of grid
								coordlist.append([colc - glc, rowc, 0, rowc + (colc - glc), 0])
					except: pass
		'''
		for glc, given_letter in enumerate(word.word): # cycle through letters in word
			for rowc, row in enumerate(self.grid): # cycle through rows
				for colc, cell in enumerate(row): # cycle through letters in rows
					if given_letter == cell: # check match letter in word to letters in row
						#print given_letter.encode('utf-8'), cell.encode('utf-8'), colc, rowc, self.letters[cell]
						try: # suggest vertical placement 
							if rowc - glc >= 0: # make sure we're not suggesting a starting point off the grid
								if ((rowc - glc) + word.length) <= self.rows: # make sure word doesn't go off of grid
									coordlist.append([colc, rowc - glc, 1, colc + (rowc - glc), 0])
						except: pass
						try: # suggest horizontal placement 
							if colc - glc >= 0: # make sure we're not suggesting a starting point off the grid
								if ((colc - glc) + word.length) <= self.cols: # make sure word doesn't go off of grid
									coordlist.append([colc - glc, rowc, 0, rowc + (colc - glc), 0])
						except: pass
		'''

		# example: coordlist[0] = [col, row, vertical, col + row, score]
		#print word.word
		#print coordlist
		new_coordlist = self.sort_coordlist(coordlist, word)
		#print new_coordlist
		return new_coordlist
 
	def sort_coordlist(self, coordlist, word): # give each coordinate a score, then sort
		new_coordlist = []
		for coord in coordlist:
			col, row, vertical = coord[0], coord[1], coord[2]
			coord[4] = self.check_fit_score(col, row, vertical, word) # checking scores
			if coord[4]: # 0 scores are filtered out
				new_coordlist.append(coord)
		random.shuffle(new_coordlist) # randomize coord list; why not?
		new_coordlist.sort(key=lambda i: i[4], reverse=True) # put the best scores first
		return new_coordlist
 
	def fit_and_add(self, word): # doesn't really check fit except for the first word; otherwise just adds if score is good
		fit = False
		count = 0
		coordlist = self.suggest_coord(word) # get list of possible locations for first tile
 
		while not fit and count < self.maxloops:
 
			#if len(self.current_word_list) == 0: # this is the first word: the seed
			if self.this_is_a_seed:
				self.this_is_a_seed = False
				vertical = random.randrange(0, 2)
				'''
				# top left seed of longest word yields best results (maybe override)
				col, row = 0, 0
				'''
				# optional center seed method, slower and less keyword placement
				if vertical:
					col = int(round(self.cols/2, 0))
					row = int(round(self.rows/2, 0)) - int(round(word.length/2, 0))
				else:
					col = int(round(self.cols/2, 0)) - int(round(word.length/2, 0))
					row = int(round(self.rows/2, 0))
				'''
				# completely random seed method
				col = random.randrange(0, self.cols)
				row = random.randrange(0, self.rows)
				'''
				if self.check_fit_score(col, row, vertical, word): 
					fit = True
					self.set_word(col, row, vertical, word, force=True)
			else: # a subsquent words have scores calculated
				try: 
					col, row, vertical = coordlist[count][0], coordlist[count][1], coordlist[count][2]
				except IndexError: return # no more cordinates, stop trying to fit
 
				if coordlist[count][4]: # already filtered these out (fit score must be at least 1), but double check
					fit = True 
					self.set_word(col, row, vertical, word, force=True)
					self.total_fit_score += coordlist[count][4]
 
			count += 1
		return
 
	def check_fit_score(self, col, row, vertical, word):
		'''
		And return score (0 signifies no fit). 1 means a fit, 2+ means a cross.
 
		The more crosses the better.
		'''
		if col < 0 or row < 0:
			return 0
 
		count, score = 1, 1 # give score a standard value of 1, will override with 0 if collisions detected
		for letter in word.word:			
			try:
				active_cell = self.get_cell(col, row)
			except IndexError:
				return 0
 
			if active_cell == self.empty or active_cell == letter:
				pass
			else:
				return 0
 
			if active_cell == letter:
				score += 1
 
			if vertical:
				# check surroundings
				if active_cell != letter: # don't check surroundings if cross point
					if not self.check_if_cell_clear(col+1, row): # check right cell
						return 0
 
					if not self.check_if_cell_clear(col-1, row): # check left cell
						return 0
 
				if count == 1: # check top cell only on first letter
					if not self.check_if_cell_clear(col, row-1):
						return 0
 
				if count == word.length:#len(word.word): # check bottom cell only on last letter
					if not self.check_if_cell_clear(col, row+1): 
						return 0
			else: # else horizontal
				# check surroundings
				if active_cell != letter: # don't check surroundings if cross point
					if not self.check_if_cell_clear(col, row-1): # check top cell
						return 0
 
					if not self.check_if_cell_clear(col, row+1): # check bottom cell
						return 0
 
				if count == 1: # check left cell only on first letter
					if not self.check_if_cell_clear(col-1, row):
						return 0
 
				if count == word.length:#len(word.word): # check right cell only on last letter
					if not self.check_if_cell_clear(col+1, row):
						return 0
  
			if vertical: # progress to next letter and position
				row += 1
			else: # else horizontal
				col += 1
 
			count += 1
 
		return score
 
	def set_word(self, col, row, vertical, word, force=False): # also adds word to word list
		if force:
			word.col = col
			word.row = row
			word.vertical = vertical
			self.current_word_list.append(word)
 
			for letter in word.word:
				self.set_cell(col, row, letter)
				if vertical:
					row += 1
				else:
					col += 1
		return
 
	def set_cell(self, col, row, value):
		self.grid[row][col] = value

		self.letters[value].append((col, row))
		self.letters[value] = list(set(self.letters[value]))
 
	def get_cell(self, col, row):
		return self.grid[row][col]
 
	def check_if_cell_clear(self, col, row):
		try:
			cell = self.get_cell(col, row)
			if cell == self.empty: 
				return True
		except IndexError:
			pass
		return False
 
	def solution(self): # return solution grid
		outStr = ""

		'''
		for r in range(self.rows):
			for c in self.grid[r]:
				outStr += '%s ' % c
			outStr += '\n'
		'''

		outStr += '<table>'
		for r in range(self.rows):
			outStr += '<tr>'
			for c in self.grid[r]:
				outStr += '<td>%s</td>' %c
			outStr += '</tr>'
		outStr += '</table>'

		return outStr.encode('utf-8')
 
	def word_find(self): # return solution grid
		outStr = ""

		for r in range(self.rows):
			for c in self.grid[r]:
				if c == self.empty:
					outStr += '%s ' % string.lowercase[random.randint(0,len(string.lowercase)-1)]
				else:
					outStr += '%s ' % c
			outStr += '\n'

		'''
		outStr += '<table>'
		for r in range(self.rows):
			outStr += '<tr>'
			for c in self.grid[r]:
				if c == self.empty:
					outStr += '<td>%s</td>' % string.lowercase[random.randint(0,len(string.lowercase)-1)]
				else:
					outStr += '<td>%s</td>' %c
			outStr += '</tr>'
		outStr += '</table>'
		'''

		return outStr.encode('utf-8')
 
	def order_number_words(self): # orders words and applies numbering system to them
		self.current_word_list.sort(key=lambda i: (i.col + i.row))
		count, icount = 1, 1
		for word in self.current_word_list:
			word.number = count
			if icount < len(self.current_word_list):
				if word.col == self.current_word_list[icount].col and word.row == self.current_word_list[icount].row:
					pass
				else:
					count += 1
			icount += 1
 
	def display(self, order=True): # return (and order/number wordlist) the grid minus the words adding the numbers
		outStr = ""
		if order:
			self.order_number_words()
 
		copy = self
 
		for word in self.current_word_list:
			copy.set_cell(word.col, word.row, word.number)
 
		for r in range(copy.rows):
			for c in copy.grid[r]:
				outStr += '%s ' % c
			outStr += '\n'
 
		'''
		outStr += '<table>'
		for r in range(copy.rows):
			outStr += '<tr>'
			for c in copy.grid[r]:
				outStr += '<td>%s</td>' %c
			outStr += '</tr>'
		outStr += '</table>'
		'''
 
		outStr = re.sub(r'[a-z]', ' ', outStr)
		return outStr.encode('utf-8')
 
	def word_bank(self): 
		outStr = ''
		temp_list = duplicate(self.current_word_list)
		random.shuffle(temp_list) # randomize word list
		for word in temp_list:
			outStr += '%s\n<br/>' %(word.word)
		return outStr.encode('utf-8')
 
	def legend(self): # must order first
		outStr = ''
		for word in self.current_word_list:
			outStr += '%d. (%d,%d) %s: %s - %s\n<br/>' % (word.number, word.col, word.row, word.down_across(), word.clue, word.word )
		return outStr.encode('utf-8')
 
	def listthetuples(self):
		listtuple = []
		for word in self.current_word_list:
			listtuple.append((word.length, "\""+word.clue.encode('utf-8')+"\"", "\""+word.word.encode('utf-8')+"\"", "\"\"", word.down_across_int(), word.col, word.row, "\""+word.clue2.encode('utf-8')+"\"", "\""+word.synset+"\""))
		return listtuple

class Word(object):
	def __init__(self, word=None, clue=None, clue2=None, synset=None):
		self.word = re.sub(r'\s', '', word.lower())
		self.clue = clue
		self.clue2 = clue2
		self.synset = synset
		self.length = len(self.word)
		#self.scrabble()
		# the below are set when placed on board
		self.row = None
		self.col = None
		self.vertical = None
		self.number = None

	def scrabble(self):
		scrabblescore = 0
		for letter in self.word:
			#letter = letter.lower()
			if letter in ['e', 'a', 'i', 'o', 'n', 'r', 't', 'l', 's', 'u']:
				scrabblescore += 1
			elif letter in ['d', 'g']:
				scrabblescore += 2
			elif letter in ['b', 'c', 'm', 'p']:
				scrabblescore += 3
			elif letter in ['f', 'h', 'v', 'w', 'y']:
				scrabblescore += 4
			elif letter in ['k']:
				scrabblescore += 5
			elif letter in ['j', 'x']:
				scrabblescore += 8
			elif letter in ['q', 'z']:
				scrabblescore += 10
		return scrabblescore / self.length # should average it out, because the longer (and harder to place) a word, the higher (and easier to place) the scrabble score tends to be
 
	def down_across(self): # return down or across
		if self.vertical: 
			return 'down'
		else: 
			return 'across'
 
	def down_across_int(self): # return down or across as an integer
		if self.vertical: 
			return 1
		else: 
			return 0
 
	def __repr__(self):
		return self.word
 
### end class, start execution

def getclues():
	aword = []
	if cluetype == 1:
		for [synlemma] in conn.execute("SELECT word.lemma FROM word, sense WHERE word.wordid=sense.wordid AND sense.synset=? AND sense.lang=? ORDER BY ABS(sense.freq) DESC, RANDOM()", [synset, cluelang]):
			aword.append(synlemma.replace("_", " "))
		if (sollang == cluelang):
			try:
				# TODO introduce edit distance to remove similar but not identical words
				aword.remove(synname)
			except ValueError:
				pass
		if (len(aword) < 1):
			return
	elif cluetype == 2:
		for [syndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang=? ORDER BY random()", [synset, cluelang]):
			aword.append(syndef.replace('"', '&quot;'))
		if (len(aword) < 1):
			return
	elif cluetype == 3:
		for [syndef] in conn.execute("SELECT def FROM synset_ex WHERE synset=? AND lang=? ORDER BY random()", [synset, cluelang]):
			aword.append(syndef.replace('"', '&quot;'))
		if (len(aword) < 1):
			return
	elif cluetype == 4:
		aword.append(synkanji.replace("_", " "))
	elif cluetype == 5:
		for [syndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang='img' ORDER BY random()", [synset]):
			aword.append("""<img width=20px src='./wn-ocal/img/%s.png' alt='%s' onMouseover=\\"ddrivetip('<img width=150px src=&quot;./wn-ocal/img/%s.png&quot; alt=&quot;%s&quot;>')\\" onMouseout='hideddrivetip()'>""" %(syndef,syndef,syndef,syndef))
		if (len(aword) < 1):
			return

	bword = []
	if clue2type == 1:
		for [synlemma] in conn.execute("SELECT word.lemma FROM word, sense WHERE word.wordid=sense.wordid AND sense.synset=? AND sense.lang=? ORDER BY ABS(sense.freq) DESC, RANDOM()", [synset, cluelang]):
			bword.append(synlemma.replace("_", " "))
		if (sollang == cluelang):
			try:
				# TODO introduce edit distance to remove similar but not identical words
				bword.remove(synname)
			except ValueError:
				pass
		if forceclue2:
			if (len(bword) < 1):
				return
	elif clue2type == 2:
		for [syndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang=? ORDER BY random()", [synset, cluelang]):
			bword.append(syndef.replace('"', '&#39;&#39;').replace("'", '&#39;'))
		if forceclue2:
			if (len(bword) < 1):
				return
	elif clue2type == 3:
		for [syndef] in conn.execute("SELECT def FROM synset_ex WHERE synset=? AND lang=? ORDER BY random()", [synset, cluelang]):
			bword.append(syndef.replace('"', '&#39;&#39;').replace("'", '&#39;'))
		if forceclue2:
			if (len(bword) < 1):
				return
	elif clue2type == 4:
		bword.append(synkanji.replace("_", " "))
	elif clue2type == 5:
		for [syndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang='img' ORDER BY random()", [synset]):
			bword.append("""<img width=20px src='./wn-ocal/img/%s.png' alt='%s' onMouseover=\\"ddrivetip('<img width=150px src=&quot;./wn-ocal/img/%s.png&quot; alt=&quot;%s&quot;>')\\" onMouseout='hideddrivetip()'>""" %(syndef,syndef,syndef,syndef))
		if forceclue2:
			if (len(bword) < 1):
				return

	somewords[synname] = (", ".join(lem for lem in aword)+' --- '+synset[-1].upper(), ", ".join(lem for lem in bword), synset)

try:

	start_full = float(time.time())

	# TODO : add word variant comparison to remove alternative spellings and leave true synonyms
	# TODO : add frequencies from outside sources to wordnet
	# TODO : add support for custom wordlists
	# TODO : allow synlinks, hyponyms, theme hypernyms

	# Get data from html form fields
	form = cgi.FieldStorage()
	gridlength = form.getvalue('gridlength', '13')
	sollang = form.getvalue('sollang', 'eng')
	cluelang = form.getvalue('cluelang', 'jpn')
	cluetype = form.getvalue('cluetype', '1') # synonyms-1; definition-2; examples-3; kanji-4; images-5
	clue2type = form.getvalue('clue2type', '2') # synonyms-1; definition-2; examples-3; kanji-4
	forceclue2 = form.getvalue('forceclue2', '0')

	try:
		gridlength = int(gridlength)
		if not (4 < gridlength < 51):
			gridlength = 13
	except ValueError:
		gridlength = 13
	try:
		cluetype = int(cluetype)
		if not (1 <= cluetype <= 5):
			cluetype = 1
	except ValueError:
		cluetype = 1
	try:
		clue2type = int(clue2type)
		if not (1 <= clue2type <= 5):
			clue2type = 1
	except ValueError:
		clue2type = 1
	if cluetype == 2: # definition
		if cluelang not in ["eng", "jpn", "als"]:
			cluetype = 1
	if cluetype == 3: # examples
		if cluelang not in ["eng", "jpn", "als"]:
			cluetype = 1
	if cluetype == 4: # kanji
		sollang = "jpn"
	if clue2type == 2: # definition
		if cluelang not in ["eng", "jpn", "als"]:
			clue2type = 1
	if clue2type == 3: # examples
		if cluelang not in ["eng", "jpn", "als"]:
			clue2type = 1
	if clue2type == 4: # kanji
		sollang = "jpn"
	try:
		forceclue2 = bool(int(forceclue2))
	except ValueError:
		forceclue2 = False

	username = form.getvalue('username', 'guestie')
	notebooklocation = '../../cwpz/app/userstats/notebook-'+username+'.txt'
	# Create note file if it doesn't exist
	notelog = open(notebooklocation, 'a')
	notelog.close()
	# Start reading from notes
	notes = open(notebooklocation).read()
	notes = re.sub(r'\r\n|\r','\n',notes)
	setwords = []
	sets = []
	words = []
	byewordnet = []
	for line in notes.split('\n'): # splitlines() doesn't get rid of the \n
		try:
			line = line.strip()
			(custype, detail) = line.split(' ',1)
			detail = detail.strip()
			if custype == "w":
				words.append(detail)
			elif custype == "s":
				if re.search(r"^\d{8}-\w$",detail):
					sets.append(detail)
				else:
					raise BadFormattingError(893)
			elif custype == "sw":
				(sset, word) = detail.split(' ',1)
				word = word.strip()
				if re.search(r"^\d{8}-\w$",sset):
					setwords.append((sset, word))
				else:
					raise BadFormattingError(893)
			elif custype == "wc":
				(word, cclue) = detail.split(' ',1)
				cclue = cclue.strip()
				try:
					(aword, bword) = cclue.split('|',1)
					aword = aword.strip()
					bword = bword.strip()
				except ValueError:
					aword = cclue
					bword = ''
				byewordnet.append((word, aword, bword))
			else:
				raise BadFormattingError(893)
		except ValueError:
			continue
		except BadFormattingError:
			continue
	setwords = list(set(setwords))
	sets = list(set(sets))
	words = list(set(words))
	byewordnet = list(set(byewordnet))
	yescustom = len(setwords) + len(sets) + len(words) + len(byewordnet)

	conn = sqlite3.connect('wn-multi.db')
	#curs = conn.cursor()
	somewords = {}

	if yescustom:
		#SELECT * FROM word WHERE lemma='dog' AND lang='eng' ORDER BY RANDOM()		+
		#SELECT * FROM sense WHERE wordid=85237 ORDER BY ABS(freq) DESC, RANDOM()	=
		#SELECT word.lemma, sense.synset FROM word, sense WHERE word.lemma='dog' AND word.lang='eng' AND word.wordid=sense.wordid ORDER BY ABS(sense.freq) DESC, RANDOM()
		for lemma in words:
			synname = lemma.decode('utf-8')
			isFound = False
			if sollang == 'jpn':
				try:
					[synset, wordid] = conn.execute("SELECT sense.synset, sense.wordid FROM word, sense WHERE word.pron=? AND word.lang=? AND word.wordid=sense.wordid ORDER BY ABS(sense.freq) DESC, ABS(sense.freqset) DESC, RANDOM()", [synname, sollang]).fetchone()
					isFound = True
				except TypeError:
					pass
			if not isFound:
				try:
					[synset, wordid] = conn.execute("SELECT sense.synset, sense.wordid FROM word, sense WHERE word.lemma=? AND word.lang=? AND word.wordid=sense.wordid ORDER BY ABS(sense.freq) DESC, ABS(sense.freqset) DESC, RANDOM()", [synname, sollang]).fetchone()
				except TypeError:
					continue
			if sollang == 'jpn':
				[synname, synkanji] = conn.execute("SELECT pron, lemma FROM word WHERE wordid=?", [wordid]).fetchone()
				if synname == None:
					continue
			if (1 < len(synname) < gridlength) and (re.search(r"[\W\d_]",synname,re.UNICODE) == None): # and (re.search(r"ー".decode('utf-8'),synname) == None)
				pass
			else:
				continue
			getclues()
		for synset in sets:
			for [lemma, pron] in conn.execute("SELECT word.lemma, word.pron FROM word, sense WHERE sense.synset=? AND sense.lang=? AND word.wordid=sense.wordid ORDER BY ABS(sense.freq) DESC, RANDOM()", [synset, sollang]):
				synname = lemma
				if sollang == 'jpn':
					if pron == None:
						continue
					synname = pron
					synkanji = lemma
				if (2 < len(synname) < gridlength and (re.search(r"[\W\d_]",synname,re.UNICODE) == None)):
					getclues()
					break
				else:
					continue
		for (synset, synname) in setwords:
			synname = synname.decode('utf-8')
			if (1 < len(synname) < gridlength and (re.search(r"[\W\d_]",synname,re.UNICODE) == None)):
				if cluetype == 4:
					try:
						[synkanji] = conn.execute("SELECT word.lemma FROM word, sense WHERE sense.synset=? AND word.pron=? AND sense.lang='jpn' AND word.wordid=sense.wordid ORDER BY ABS(sense.freq) DESC, RANDOM()", [synset, synname]).fetchone()
						getclues()
						continue
					except TypeError:
						pass
					try:
						synkanji = synname
						[synname] = conn.execute("SELECT word.pron FROM word, sense WHERE sense.synset=? AND word.lemma=? AND sense.lang='jpn' AND word.wordid=sense.wordid ORDER BY ABS(sense.freq) DESC, RANDOM()", [synset, synkanji]).fetchone()
						getclues()
						continue
					except TypeError:
						continue
				getclues()
		for (synname, aword, bword) in byewordnet:
			synname = synname.decode('utf-8')
			if (1 < len(synname) < gridlength and (re.search(r"[\W\d_]",synname,re.UNICODE) == None)):
				aword = aword.replace('"', '&quot;')
				bword = bword.replace('"', '&#39;&#39;').replace("'", '&#39;')
				aword = re.sub(r'[<>]', '', aword)
				bword = re.sub(r'[<>]', '', bword)
				somewords[synname] = (aword, bword, '')

	else:
		queryone = conn.execute("SELECT synset FROM sense_core a WHERE lang=? AND ? IN (SELECT lang FROM sense_core b WHERE a.synset=b.synset) ORDER BY RANDOM() LIMIT 500", [sollang, cluelang]) # limit because doing the whole set would take too long and is rather pointless as we only need a few
		for [synset] in queryone:
			if sollang == 'jpn':
				[synname, synkanji] = conn.execute("SELECT word.pron, word.lemma FROM word, sense WHERE word.wordid=sense.wordid AND sense.synset=? AND sense.lang=? ORDER BY ABS(sense.freq) DESC, RANDOM()", [synset, sollang]).fetchone()
				if synname == None:
					continue
			else:
				[synname] = conn.execute("SELECT word.lemma FROM word, sense WHERE word.wordid=sense.wordid AND sense.synset=? AND sense.lang=? ORDER BY ABS(sense.freq) DESC, RANDOM()", [synset, sollang]).fetchone() # there are very few results of this select statement, so order by random() is fast enough
			if (2 < len(synname) < gridlength) and (re.search(r"[\W\d_]",synname,re.UNICODE) == None): # looks like it has to be < not <= the row/col length
				#synname = synname.replace("_", " ")
				pass
			else:
				continue
			getclues()

	conn.close()

	# somewords.items() IS EQUIVALENT TO [(k,v) for k, v in somewords.iteritems()]
	word_list = [(k,v1,v2,v3) for k, (v1, v2, v3) in somewords.iteritems()]

	a = Crossword(gridlength, gridlength, ' ', 5000, word_list)
	a.compute_crossword(1,2) # seconds, passes
	print """Content-type:text/html;charset=utf-8\r\n\r\n
	<html>
	<head>
	<script type="text/javascript">if (parent.frames.length == 0) location.href="interface.php";</script>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
	<link rel="stylesheet" href="../../cwpz/css/base.css" type="text/css">
	<title>Crossword</title>
	</head>
	<body>
	"""
	'''
	print a.word_bank()
	print a.solution()
	#print a.word_find()
	a.display()
	print a.legend()
	print len(a.current_word_list), 'out of', len(word_list)
	print a.total_fit_score
	print a.debug
	end_full = float(time.time())
	print end_full - start_full
	'''
	listtuple = a.listthetuples()
	numnow = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	random5 = str(random.randint(0, 99999)).zfill(5)
	cwid = numnow+random5
	f = open("../../cwpz/"+cwid+".html", 'w')
	f.write("""
<html>

<head>
	<script type="text/javascript">if (parent.frames.length == 0) location.href="interface.php";</script>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
	<title>WordNet Multilingual Crossword</title>	
</head> 
 
<body>

<div id="dhtmltooltip"></div>

<script type="text/javascript">

/***********************************************
* Cool DHTML tooltip script- © Dynamic Drive DHTML code library (www.dynamicdrive.com)
* This notice MUST stay intact for legal use
* Visit Dynamic Drive at http://www.dynamicdrive.com/ for full source code
***********************************************/

var offsetxpoint=-10 //Customize x offset of tooltip
var offsetypoint=10 //Customize y offset of tooltip
var ie=document.all
var ns6=document.getElementById && !document.all
var enabletip=false
if (ie||ns6)
var tipobj=document.all? document.all["dhtmltooltip"] : document.getElementById? document.getElementById("dhtmltooltip") : ""

function ietruebody(){
return (document.compatMode && document.compatMode!="BackCompat")? document.documentElement : document.body
}

function ddrivetip(thetext, thecolor, thewidth){
if (ns6||ie){
if (typeof thewidth!="undefined") tipobj.style.width=thewidth+"px"
if (typeof thecolor!="undefined" && thecolor!="") tipobj.style.backgroundColor=thecolor
tipobj.innerHTML=thetext
enabletip=true
return false
}
}

function positiontip(e){
if (enabletip){
/*
var curX=(ns6)?e.pageX : event.clientX+ietruebody().scrollLeft;
var curY=(ns6)?e.pageY : event.clientY+ietruebody().scrollTop;
//Find out how close the mouse is to the corner of the window
var rightedge=ie&&!window.opera? ietruebody().clientWidth-event.clientX-offsetxpoint : window.innerWidth-e.clientX-offsetxpoint-20
var bottomedge=ie&&!window.opera? ietruebody().clientHeight-event.clientY-offsetypoint : window.innerHeight-e.clientY-offsetypoint-20

var leftedge=(offsetxpoint<0)? offsetxpoint*(-1) : -1000

//if the horizontal distance isn't enough to accomodate the width of the context menu
if (rightedge<tipobj.offsetWidth)
//move the horizontal position of the menu to the left by its width
tipobj.style.left=ie? ietruebody().scrollLeft+event.clientX-tipobj.offsetWidth+"px" : window.pageXOffset+e.clientX-tipobj.offsetWidth+"px"
else if (curX<leftedge)
tipobj.style.left="5px"
else
//position the horizontal position of the menu where the mouse is positioned
tipobj.style.left=curX+offsetxpoint+"px"

//same concept with the vertical position
if (bottomedge<tipobj.offsetHeight)
tipobj.style.top=ie? ietruebody().scrollTop+event.clientY-tipobj.offsetHeight-offsetypoint+"px" : window.pageYOffset+e.clientY-tipobj.offsetHeight-offsetypoint+"px"
else
tipobj.style.top=curY+offsetypoint+"px"
*/
tipobj.style.visibility="visible"

tipobj.style.right=0+"px"
tipobj.style.top=0+"px"
}
}

function hideddrivetip(){
if (ns6||ie){
enabletip=false
tipobj.style.visibility="hidden"
//tipobj.style.left="-1000px"
tipobj.style.backgroundColor=''
tipobj.style.width=''
}
}

document.onmousemove=positiontip

</script>

	<!-- 
		here we have oygContext top DOM element to which the play area will be bound;
		the HTML template has more binding sites for various visual parts of the puzzle: 
		oygHeader, oygHeaderMenu, oygState, oygPuzzle, oygPuzzleFooter, oygListH, oygListV, oygFooter;
		all element names for binding are prefixed with "oyg"
	-->
	<div id="oygContext" align="center" style="width:100%;">
		<table class="oyOuterFrame" border="0" cellpadding="0" cellspacing="0">
			<tr><td align="center">
				<table class="oyFrame" border="0" cellpadding="0" cellspacing="0">
					<tr>
						<td colspan="5">
							<table class="oyFrame" border="0" cellpadding="0" cellspacing="0" width="100%">
								<tr class="oyHeader">
									<td class="oyHeader">
										<div id="oygHeader"></div>
									</td>
									<td align="right">	
										<div id="oygHeaderMenu"></div>								
									</td> 
								</tr>					
							</table>
						</td>  
					</tr>
					<tr style="height: 4px;">
						<td colspan="5"></td>
					</tr>
					<tr>  
						<td rowspan="3" class="oyPuzzleCell" align="center" valign="top"> 
							<div id="oygState"></div>
							<div class="oyPuzzle" id="oygPuzzle"></div>
							<div class="oyPuzzleFooter" id="oygPuzzleFooter"></div>			
						</td>  
						<td class="oyListCellDot">.</td>    
						<td class="oyListCell" valign="top" id="oygListH"></td>
					</tr>
					<tr style="height: 4px;">
						<td colspan="4"></td>
					</tr>		
					<tr>  
						<td class="oyListCellDot">.</td>   
						<td class="oyListCell" valign="top" id="oygListV"></td>					
					</tr>
					<tr style="height: 4px;">
						<td colspan="5"></td>
					</tr>			
					<tr>
						<td colspan="5" class="oyFooter"> 
							<div id="oygFooter"></div>
						</td>
					</tr>			
				</table>
			</td></tr>
		</table>
		<div id="oygStatic" align="center" style="font-size: 10px; color: #4282B5; font-family: Arial;"></div>
	</div>  

	<!-- 
		here we include all oy-cword-1.0 CSS files; all our style class name are prefixed with "oy" 
	-->
	<link rel="stylesheet" href="./css/base.css" type="text/css">

	<!-- 
		here we include all oy-cword-1.0 JavaScript files; order is important; 
		all the files can be combined into one file to reduce number of separate requests
	-->
	<script type="text/javascript" src="./js/oyPrologue.js"></script>	
	<script type="text/javascript" src="./js/oyJsrAjax.js"></script>	
	<script type="text/javascript" src="./js/oyClue.js"></script>	
	<script type="text/javascript" src="./js/oyMenu.js"></script>	
	<script type="text/javascript" src="./js/oyPuzzle.js"></script>	
	<script type="text/javascript" src="./js/oyServer.js"></script>	
	<script type="text/javascript" src="./js/oySign.js"></script>	
	<script type="text/javascript" src="./js/oyMisc.js"></script>	
 
	<script type="text/javascript"><!--

		// 
		//	here we include our own puzzle; it has to be fully prepared with all words properly arranged on the grid;
		//	currently only one instance of the puzzle can be embedded into the page, we may fix this in the future
		// """)
	f.write('''
		var oygCrosswordPuzzle = new oyCrosswordPuzzle (
		  "''')
	f.write(cwid)
	f.write('''",
		  ".",
		  "''')
	f.write(cwid)
	f.write('''",
		  "WordNet Multilingual Crossword",
		  "",
		  [
''')
	for word in listtuple:
		f.write("""\t\t\tnew oyCrosswordClue(""")
		f.write(""", """.join([str(i) for i in word]))
		f.write("""),\n""")
	f.write("""		  ],
		  """)
	f.write(str(gridlength))
	f.write(""",""")
	f.write(str(gridlength))
	f.write("""
		);""")
	f.write("""
		//
		//	here we configure puzzle options, callbacks and publisher information
		// 
		 
		// publisher information
		oygCrosswordPuzzle.publisherName = "";
		oygCrosswordPuzzle.publisherURL = "";

		// game exit URL
		oygCrosswordPuzzle.leaveGameURL = "";  
      
		// this is how to turn off server support; score submission and action tracking will be disabled
		oygCrosswordPuzzle.canTalkToServer = false;
	
	--></script>	

	<!--
		here we instantiate the puzzle and bind it to the HTML template above and show it to the user
	-->
	<script type="text/javascript" src="./js/oyEpilogue.js"></script>

<script type="text/javascript">
function scrnkey(item) { 
	//document.getElementsByClassName("oyCellActive").item(0).innerHTML = item; //don't do this, breaks the flow if you change innerHTML, but somehow you can't edit value this way
	var x = oygCrosswordPuzzle.xpos;
	var y = oygCrosswordPuzzle.ypos;
	var target = oygCrosswordPuzzle.inputCache.getElement(x,y);
	if (!target.readOnly){
		target.value = item;
		oygCrosswordPuzzle.moveToNextCell(x, y);
	}
}
</script>
<br/>
<div id="donelinks"></div>
""")
	if sollang == "jpn":
		f.write("""
<table class="scrnkeybd">
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="あ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぁ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="か"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="が"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="さ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ざ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="た"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="だ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="な"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="は"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ば"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぱ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ま"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="や"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ゃ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ら"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="わ"></td>
</tr>
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="い"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぃ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="き"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぎ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="し"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="じ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ち"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぢ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="に"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ひ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="び"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぴ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="み"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value=""></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value=""></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="り"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value=""></td>
</tr>
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="う"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぅ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="く"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぐ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="す"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ず"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="つ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="づ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぬ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ふ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぶ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぷ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="む"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ゆ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ゅ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="る"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value=""></td>
</tr>
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="え"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぇ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="け"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="げ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="せ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぜ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="て"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="で"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ね"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="へ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="べ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぺ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="め"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value=""></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value=""></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="れ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value=""></td>
</tr>
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="お"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぉ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="こ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ご"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="そ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぞ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="と"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ど"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="の"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ほ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぼ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ぽ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="も"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="よ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ょ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ろ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="を"></td>
</tr>
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ん"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="っ"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="ー"></td>
</tr>
</table>
""")
	elif sollang == "eng":
		f.write("""
<table class="scrnkeybd">
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="Q"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="W"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="E"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="R"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="T"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="Y"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="U"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="I"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="O"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="P"></td>
</tr>
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="A"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="S"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="D"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="F"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="G"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="H"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="J"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="K"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="L"></td>
</tr>
<tr>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="Z"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="X"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="C"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="V"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="B"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="N"></td>
<td><input type="button" class="scrnkey" onclick="scrnkey(value)" value="M"></td>
</tr>
</table>
""")
	f.write("""
</body>

</html>
""")
	f.close()
	print """<a id="puzzlink" href="../../cwpz/"""+cwid+""".html">Click here to load crossword puzzle</a>"""
	print """<script type="text/javascript">
window.setTimeout(function() {
document.location.href = document.getElementById("puzzlink").href;
}, 500);
</script>
	</body>
	</html>
	"""
except:
	errtime = '--- '+ datetime.datetime.now().strftime('%d %b %Y %H:%M:%S, %a') +' ---\n'
	errlog = open('cgi_errlog.txt', 'a') # 'a' to append to site error log, 'w' to rewrite it completely new each time
	errlog.write("\n"+errtime)
	traceback.print_exc(None, errlog)
	errlog.close()
	print "<p>CGI Error, please check the site error log for details.</p>"
	print traceback.format_exc()