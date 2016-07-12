import os
from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, render_template, abort, send_from_directory, session

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

from crossword import run
from browsewordnet import browse

@app.route("/")
def home():
	return render_template('interface.html')

@app.route("/prog", methods=['GET', 'POST'])
def prog():
	if request.method == 'POST':
		session['gridlength'] = request.form.get('gridlength', '13')
		session['sollang'] = request.form.get('sollang', 'eng')
		session['cluelang'] = request.form.get('cluelang', 'jpn')
		session['cluetype'] = request.form.get('cluetype', '1')
		session['clue2type'] = request.form.get('clue2type', '2')
		session['forceclue2'] = request.form.get('forceclue2', '0')
		session['notebook'] = request.form.get('notebook', '').encode("utf-8")
		gridlength, sollang, cwid, listtuple = run(session)
		return render_template('puzzle.html', gridlength=gridlength, sollang=sollang, cwid=cwid, listtuple=listtuple)
	else:
		return "To start, click on the 'Generate Puzzle' button at the top right, then wait a while for the puzzle to load (may take up to a few minutes)"

@app.route("/options")
def options():
	langs = [('als', 'Albanian'), ('arb', 'Arabic'), ('ind', 'Bahasa Indonesia'), ('zsm', 'Bahasa Melayu'), ('eus', 'Basque'), ('nob', 'Bokmal'), ('por', 'Brazilian Portuguese'), ('cat', 'Catalan'), ('dan', 'Danish'), ('eng', 'English'), ('fin', 'Finnish'), ('fre', 'French'), ('glg', 'Galician'), ('heb', 'Hebrew'), ('ita', 'Italian'), ('jpn', 'Japanese'), ('cmn', 'Mandarin Chinese - Taiwan'), ('nno', 'Nynorsk'), ('fas', 'Persian'), ('pol', 'Polish'), ('spa', 'Spanish'), ('tha', 'Thai')]
	cluetypes = [('1', 'Synonyms'), ('2', 'Definition'), ('3', 'Examples'), ('4', 'Japanese Kanji'), ('5', 'Images')]
	cluetypes2 = [('1', 'Synonyms'), ('2', 'Definition'), ('3', 'Examples'), ('4', 'Japanese Kanji')]
	return render_template('options.html', langs=langs, cluetypes=cluetypes, cluetypes2=cluetypes2)

@app.route("/wordnet", methods=['GET', 'POST'])
def wordnet():
	wnsearch = '02084071-n'
	wnlang = 'eng'
	if request.method == 'POST':
		wnsearch = request.form.get('wnsearch', wnsearch)
		wnlang = request.form.get('wnlang', wnlang)
	elif request.method == 'GET':
		wnsearch = request.args.get('wnsearch', wnsearch)
		wnlang = request.args.get('wnlang', wnlang)
	wnsearch = wnsearch.lower().strip().decode("utf-8")
	lookup = browse(wnsearch, wnlang)
	return render_template('browse.html', langs=["eng","cmn","jpn"], wnsearch=wnsearch, wnlang=wnlang, lookup=lookup)

@app.route('/getocal/wn-ocal/img/<path:filename>')
def getocal(filename):
    return send_from_directory(app.config['SERVE_OCAL_LOC']+"/wn-ocal/img", filename, as_attachment=False)

app.secret_key = app.config['SESSION_SECRET']

if __name__ == '__main__':
	if app.config['IS_OPENSHIFT']:
		app.run()
	else:
		app.run(debug=True)
