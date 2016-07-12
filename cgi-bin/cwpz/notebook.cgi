#!/usr/bin/env python
# encoding: utf-8

# Import modules for CGI handling 
import cgi, cgitb, sqlite3, sys, traceback, time, re

class BadFormattingError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

try:
	form = cgi.FieldStorage()
	username = form.getvalue('username', 'guestie')

	notebooklocation = '../../cwpz/app/userstats/notebook-'+username+'.txt'
	# Create note file if it doesn't exist
	notelog = open(notebooklocation, 'a')
	notelog.close()
	# Get notes from file
	notes = open(notebooklocation).read()#.decode("utf-8") seems to treat CJK kters fine without needing to bother about these stuff, everything done in raw string mode since you don't need to write to sql database
	# Get notes from form
	notes = form.getvalue('notebook', notes)
	# Get rid of doubling line-break problem caused by form encoding newlines as CR LF which are separately treated as newlines by python
	notes = re.sub(r'\r\n|\r','\n',notes)

	setwords = []
	sets = []
	words = []
	byewordnet = []
	newnotes = []
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
			newnotes.append(line)
		except ValueError:
			continue
		except BadFormattingError:
			continue
	setwords = list(set(setwords))
	sets = list(set(sets))
	words = list(set(words))
	byewordnet = list(set(byewordnet))

	# Process notes
	newnotes = '\n'.join(line for line in newnotes)

	# Save notes to file
	notelog = open(notebooklocation, 'w')
	notelog.write(newnotes)
	notelog.close()

	# Feedback to user

	sys.stdout.write("""Content-type:text/html;charset=utf-8\r\n\r\n
<html>
<head>
<script type="text/javascript">if (parent.frames.length == 0) location.href="interface.php";</script>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
<link rel="stylesheet" href="../../cwpz/css/base.css" type="text/css">
<title>Notebook</title>
<style type="text/css">
body { font-family:"Times New Roman", Times, serif; font-size: 16px; }
@media (min-width: 280px) and (min-height: 350px) {
textarea { width: 270px; height: 310px; padding: 2px;　}
}
@media (max-width: 279px), (max-height: 349px) {
textarea { width: 100%; height: 88%; padding: 2px;　}
}
</style>
</head>
<body>
<form action="notebook.cgi" method="post">
<b>Custom Word List</b>
<input type="submit" value="Save"><br/>
<textarea name="notebook">""")
	sys.stdout.write(newnotes)
	sys.stdout.write("""</textarea>
""")
	sys.stdout.write('<input name="username" type="hidden" value="')
	sys.stdout.write(username)
	sys.stdout.write("""">
</form>""")
	'''
	for i in words:
		sys.stdout.write(i)
		sys.stdout.write("<br/>")
	'''
	sys.stdout.write("""
</body>
</html>
""") #rows="18" cols="35"
except IOError:
	print """Content-type:text/html;charset=utf-8\r\n\r\n
<p>Can't find text file</p>"""
except:
	errtime = '--- '+ time.ctime(time.time()) +' ---\n'
	errlog = open('cgi_errlog.txt', 'a') # 'a' to append to site error log, 'w' to rewrite it completely new each time
	errlog.write("\n"+errtime)
	traceback.print_exc(None, errlog)
	errlog.close()
	print "<p>CGI Error, please check the site error log for details.</p>"
	print traceback.format_exc()