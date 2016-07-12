#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')
DB_LOC = app.config['DB_LOC']

# Import modules for CGI handling 
import cgi, cgitb, sqlite3, sys, traceback, time, re

def browse(wnsearch, wnlang):
	lookup = ""
	try:
		conn = sqlite3.connect(DB_LOC+'/db/wnall.db')
		#curs = conn.cursor()

		# when looking up synset ids...

		#if len(re.findall(r"\d",wnsearch)) > 5:
		if re.search(r"^\d{8}-\w$",wnsearch): # looking up a synset id
			synset = wnsearch
			if wnlang == "cmn":
				wnlangpos = "eng"
			else:
				wnlangpos = wnlang

			[wnpos] = conn.execute("SELECT def FROM pos_def WHERE pos=? AND lang=?", [wnsearch[-1:], wnlangpos]).fetchone()

			[wnname] = conn.execute("SELECT name FROM synset WHERE synset=?", [synset]).fetchone()

			wnwords = []
			for [wnword] in conn.execute("SELECT word.lemma FROM word, sense WHERE word.wordid = sense.wordid AND sense.synset=? AND sense.lang=?", [synset, wnlang]):
				wnwords.append(wnword)

			wndefs = []
			for [wndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang=?", [synset, wnlang]):
				wndefs.append(wndef)
			if not wndefs:
				for [wndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang='eng'", [synset]):
					wndefs.append(wndef)
			wndefs = list(set(wndefs))

			wnegs = []
			for [wneg] in conn.execute("SELECT def FROM synset_ex WHERE synset=? AND lang=?", [synset, wnlang]):
				wnegs.append(wneg)
			if not wnegs:
				for [wneg] in conn.execute("SELECT def FROM synset_ex WHERE synset=? AND lang='eng'", [synset]):
					wnegs.append(wneg)

			wnlinks = []
			for (wntwin, wnltype, wntwinid) in conn.execute("SELECT synset.name, synlink.link, synlink.synset2 FROM synlink, synset WHERE synlink.synset1=? AND synset.synset=synlink.synset2", [synset]):
				wnlinks.append((wntwin, wnltype, wntwinid))

			lookup += "<b>synset id:</b> "
			lookup += '<a href="#" class="tag-copy classylink">%s</a>' %wnsearch
			lookup += "<br/><b>language code:</b> "
			lookup += wnlang
			lookup += "<br/><b>part of speech:</b> "
			lookup += wnpos.encode("utf-8")
			lookup += "<br/><b>name:</b> "
			lookup += wnname
			lookup += "<br/><br/><b>lemmas:</b> "
			lookup += ", ".join(i.replace("_", " ").encode("utf-8") for i in wnwords)
			lookup += "<br/><br/><b>definitions:</b><ul>"
			lookup += "\n".join("<li>%s</li>"%i.encode("utf-8") for i in wndefs)
			lookup += "</ul><b>ex:</b><ul>"
			lookup += "\n".join("<li>%s</li>"%i.encode("utf-8") for i in wnegs)
			lookup += "</ul>"
			for ltype in ["also", "syns", "hype", "inst", "hypo", "hasi", "mero", "mmem", "msub", "mprt", "holo", "hmem", "hsub", "hprt", "attr", "sim", "enta", "caus", "dmnc", "dmnu", "dmnr", "dmtc", "dmtu", "dmtr", "ants"]:
				goahead = False
				for (i,j,k) in wnlinks:
					if j == ltype:
						goahead = True
				if goahead:
					[ltypefull] = conn.execute("SELECT def FROM link_def WHERE link=?", [ltype]).fetchone()
					lookup += "<br/><b>%s:</b> " %ltypefull
					lookup += ", ".join("<a href='?wnsearch=%s&wnlang=%s'>%s</a>"%(k,wnlang,i.replace("_", " ")) for (i,j,k) in wnlinks if j == ltype)
		else: # searching a word
			lemma = wnsearch
			foundsomething = False
			#for [synset] in conn.execute("SELECT sense.synset FROM word, sense WHERE word.lemma like ? escape '/' AND word.lang=? AND word.wordid=sense.wordid", ["%"+lemma+"%", wnlang]): # this is the more lenient version, may get too many false hits
			for [synset] in conn.execute("SELECT sense.synset FROM word, sense WHERE word.lemma=? AND word.lang=? AND word.wordid=sense.wordid", [lemma, wnlang]):
				foundsomething = True
				lookup += "<a href='?wnsearch=%s&wnlang=%s'>%s</a><br/><b>"%(synset,wnlang,synset)
				wnwords = []
				for [wnword] in conn.execute("SELECT word.lemma FROM sense, word WHERE sense.synset=? AND sense.lang=? AND sense.wordid=word.wordid", [synset, wnlang]):
					wnwords.append(wnword)
				lookup += ", ".join(i.replace("_", " ").encode("utf-8") for i in wnwords)
				wndefone = []
				for [wndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang=? LIMIT 1", [synset, wnlang]): # even though it's only one, this is used to avoid multiple try except blocks
					wndef = re.sub(r'"', '&quot;', wndef)
					wndef = re.sub(r"'", '&quot;', wndef)
					wndefone.append(wndef)
				if not wndefone:
					for [wndef] in conn.execute("SELECT def FROM synset_def WHERE synset=? AND lang='eng' LIMIT 1", [synset]):
						wndef = re.sub(r'"', '&quot;', wndef)
						wndef = re.sub(r"'", '&quot;', wndef)
						wndefone.append(wndef)
				if wndefone:
					wndef = wndefone[0].encode("utf-8")
				else:
					wndef = ""
				lookup += "</b><br/>"
				lookup += "<br/>".join(d for d in wndef.split("; "))
				lookup += "<br/><br/>"
			if foundsomething == False:
				lookup += "Can't find what you're looking for."

		conn.commit()
		conn.close()
	except TypeError:
		lookup += "Can't find what you're looking for."
	except:
		errtime = '--- '+ time.ctime(time.time()) +' ---\n'
		errlog = open('cgi_errlog.txt', 'a') # 'a' to append to site error log, 'w' to rewrite it completely new each time
		errlog.write("\n"+errtime)
		traceback.print_exc(None, errlog)
		errlog.close()
		lookup += "<p>CGI Error, please check the site error log for details.</p>"
		lookup += traceback.format_exc()
	return lookup
