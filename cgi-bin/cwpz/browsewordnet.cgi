#!/usr/bin/env python
# encoding: utf-8

# Import modules for CGI handling 
import cgi, cgitb, sqlite3, sys, traceback, time, re

try:
	# Get data from html form fields

	form = cgi.FieldStorage()
	wnsearch = form.getvalue('wnsearch', '02084071-n').lower().strip().decode("utf-8")
	wnlang = form.getvalue('wnlang', 'eng')

	# Print basic html stuff

	print """Content-type:text/html;charset=utf-8\r\n\r\n
<html>
<head>
<script type="text/javascript">if (parent.frames.length == 0) location.href="../cwpz/interface.php";</script>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
<title>Browse WordNet</title>
<style type="text/css">
body { font-family:"Times New Roman", Times, serif; font-size: 16px; }

a.classylink { text-decoration: none; color: #000000; }

.invistable td { border: 0; }
.crampedtable td { padding: 0 5px; }

#lemmalookup td { vertical-align: top; }
</style>
</head>
<body>
<script type="text/javascript"> function btn_reset() { window.parent.search.location.reload(); /* window.location.reload(); */ } </script>
<script src="../../cwpz/jquery-1.7.2.min.js" type="text/javascript"></script>
<script type="text/javascript">
$('a.tag-copy').live('click', function(e){
	$('#tagadd',top.frames["search"].document).val($(this).text());
	$('#tagmod',top.frames["search"].document).val($(this).text());
	return false; // to prevent default
});
</script>
<b>Browse WordNet</b><br/><br/>
<form action="browsewordnet.cgi" method="post" target="wordnet">
<input id='wnsearch' name="wnsearch" type='text' value=%s />
<select id="wnlang" name="wnlang">
""" %wnsearch.encode("utf-8")
	for l in ["eng","cmn","jpn"]:
		selectyn = ""
		if l == wnlang:
			selectyn = " selected"
		print "<option value='%s'%s/>%s" %(l,selectyn,l)
	print """</select>
<input type="submit" value="Look it up"/>
</form>
""" #sys.stdout.write("")

	# Form select query for sqlite3 database and feedback info

	conn = sqlite3.connect('wnall.db')
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

		print "<b>synset id:</b> ",
		print '<a href="#" class="tag-copy classylink">%s</a>' %wnsearch
		print "<br/><b>language code:</b> ",
		print wnlang
		print "<br/><b>part of speech:</b> ",
		print wnpos.encode("utf-8")
		print "<br/><b>name:</b> ",
		print wnname
		print "<br/><br/><b>lemmas:</b> ",
		print ", ".join(i.replace("_", " ").encode("utf-8") for i in wnwords)
		print "<br/><br/><b>definitions:</b><ul>",
		print "\n".join("<li>%s</li>"%i.encode("utf-8") for i in wndefs)
		print "</ul><b>ex:</b><ul>",
		print "\n".join("<li>%s</li>"%i.encode("utf-8") for i in wnegs)
		print "</ul>"
		for ltype in ["also", "syns", "hype", "inst", "hypo", "hasi", "mero", "mmem", "msub", "mprt", "holo", "hmem", "hsub", "hprt", "attr", "sim", "enta", "caus", "dmnc", "dmnu", "dmnr", "dmtc", "dmtu", "dmtr", "ants"]:
			goahead = False
			for (i,j,k) in wnlinks:
				if j == ltype:
					goahead = True
			if goahead:
				[ltypefull] = conn.execute("SELECT def FROM link_def WHERE link=?", [ltype]).fetchone()
				print "<br/><b>%s:</b> " %ltypefull,
				print ", ".join("<a href='?wnsearch=%s&wnlang=%s'>%s</a>"%(k,wnlang,i.replace("_", " ")) for (i,j,k) in wnlinks if j == ltype)
	else: # searching a word
		lemma = wnsearch
		foundsomething = False
		#for [synset] in conn.execute("SELECT sense.synset FROM word, sense WHERE word.lemma like ? escape '/' AND word.lang=? AND word.wordid=sense.wordid", ["%"+lemma+"%", wnlang]): # this is the more lenient version, may get too many false hits
		for [synset] in conn.execute("SELECT sense.synset FROM word, sense WHERE word.lemma=? AND word.lang=? AND word.wordid=sense.wordid", [lemma, wnlang]):
			foundsomething = True
			print "<a href='?wnsearch=%s&wnlang=%s'>%s</a><br/><b>"%(synset,wnlang,synset)
			wnwords = []
			for [wnword] in conn.execute("SELECT word.lemma FROM sense, word WHERE sense.synset=? AND sense.lang=? AND sense.wordid=word.wordid", [synset, wnlang]):
				wnwords.append(wnword)
			print ", ".join(i.replace("_", " ").encode("utf-8") for i in wnwords)
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
			print "</b><br/>"
			print "<br/>".join(d for d in wndef.split("; "))
			print "<br/><br/>"
		if foundsomething == False:
			print "Can't find what you're looking for."

	print """</body>
</html>
"""
	conn.commit()
	conn.close()
except TypeError:
	print "Can't find what you're looking for."
except:
	errtime = '--- '+ time.ctime(time.time()) +' ---\n'
	errlog = open('cgi_errlog.txt', 'a') # 'a' to append to site error log, 'w' to rewrite it completely new each time
	errlog.write("\n"+errtime)
	traceback.print_exc(None, errlog)
	errlog.close()
	print "<p>CGI Error, please check the site error log for details.</p>"
	print traceback.format_exc()