## Description

Allows players to solve multilingual crosswords that are randomly generated with WordNet.

## Credits

- The dictionary data used to generate the crosswords are from the [Open Multilingual Wordnet](http://compling.hss.ntu.edu.sg/omw/).
- The original [Python Crossword Puzzle Generator](http://bryanhelmig.com/python-crossword-puzzle-generator/) was created by Bryan Helmig and released under the BSD 2-Clause License.
- The original [JavaScript Crossword Engine](http://softwaresecretweapons.com/crossword_engine.html) was created by Pavel Simakov and released under LGPL.

## Link

[Try it out here](http://multi-xwords.rhcloud.com)

## Instructions to run locally

1. Download [wn-multi.db](https://www.dropbox.com/s/zo4u1lbvjuajm8a/wn-multi.db?dl=0) and [wnall.db](https://www.dropbox.com/s/3vszhzz4eafeoqo/wnall.db?dl=0), then copy them over to replace the empty placeholder files with the same name in `static/db`
2. Download [wn-ocal.zip](https://www.dropbox.com/s/mz3r9vn0obpo3tt/wn-ocal.zip?dl=0), then place it in the `static` folder
3. Ensure IS_OPENSHIFT is set to False in `flaskapp.cfg`
4. Ensure OCAL_IS_ZIPPED is set to True in `flaskapp.cfg`, or you can set it to False and unzip wn-ocal.zip in place (`wn-ocal` folder as subfolder of `static`)
5. Run with Flask's built-in dev server by running `python flaskapp.py` at folder root

## Instructions to deploy to OpenShift

1. Download [wn-multi.db](https://www.dropbox.com/s/zo4u1lbvjuajm8a/wn-multi.db?dl=0) and [wnall.db](https://www.dropbox.com/s/3vszhzz4eafeoqo/wnall.db?dl=0), then upload them to OPENSHIFT_DATA_DIR under the subfolder `db`
2. Download [wn-ocal.zip](https://www.dropbox.com/s/mz3r9vn0obpo3tt/wn-ocal.zip?dl=0), then upload the zip file to OPENSHIFT_DATA_DIR
3. Ensure IS_OPENSHIFT is set to True in `flaskapp.cfg`
4. Ensure OCAL_IS_ZIPPED is set to True in `flaskapp.cfg`, or you can set it to False and unzip wn-ocal.zip in place (`wn-ocal` folder as subfolder of OPENSHIFT_DATA_DIR)
5. Deploy to OpenShift

(To upload to OPENSHIFT_DATA_DIR, you can [FTP into your OpenShift app](https://blog.openshift.com/using-filezilla-and-sftp-on-windows-with-openshift/), then go to `app-root/data`)
