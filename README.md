## Description

Allows players to solve multilingual crosswords that are randomly generated with WordNet.

## Credits

- The dictionary data used to generate the crosswords are from the [Open Multilingual Wordnet](http://compling.hss.ntu.edu.sg/omw/).
- The original [Python Crossword Puzzle Generator](http://bryanhelmig.com/python-crossword-puzzle-generator/) was created by Bryan Helmig and released under the BSD 2-Clause License.
- The original [JavaScript Crossword Engine](http://softwaresecretweapons.com/crossword_engine.html) was created by Pavel Simakov and released under LGPL.

## Instructions

1. Download [wn-multi.db](https://www.dropbox.com/s/zo4u1lbvjuajm8a/wn-multi.db?dl=0) and [wnall.db](https://www.dropbox.com/s/3vszhzz4eafeoqo/wnall.db?dl=0), then copy them over to replace the empty placeholder files with the same name in `cgi-bin/cwpz`
2. Download [wn-ocal.zip](https://www.dropbox.com/s/mz3r9vn0obpo3tt/wn-ocal.zip?dl=0), then unzip it to `cwpz`
3. Use XAMPP or similar (configure it to make cgi-bin work) to run it from the root folder
4. Set up a MySQL DB and use `cwpz/user table schema.txt` to create the user table, then edit `cwpz/common.php` to define the connection information to that DB