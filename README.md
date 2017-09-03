## Description

Allows players to solve multilingual crosswords that are randomly generated with WordNet.

## Credits

- The dictionary data used to generate the crosswords are from the [Open Multilingual Wordnet](http://compling.hss.ntu.edu.sg/omw/).
- The original [Python Crossword Puzzle Generator](http://bryanhelmig.com/python-crossword-puzzle-generator/) was created by Bryan Helmig and released under the BSD 2-Clause License.
- The original [JavaScript Crossword Engine](http://softwaresecretweapons.com/crossword_engine.html) was created by Pavel Simakov and released under LGPL.

## Link

[Try it out here](http://multi-xwords.a3c1.starter-us-west-1.openshiftapps.com)

## Instructions

1. Download [wn-multi.db](https://www.dropbox.com/s/zo4u1lbvjuajm8a/wn-multi.db?dl=0) and [wnall.db](https://www.dropbox.com/s/3vszhzz4eafeoqo/wnall.db?dl=0), then copy them over to replace the empty placeholder files with the same name in `staticb/db`
2. Download [wn-ocal.zip](https://www.dropbox.com/s/mz3r9vn0obpo3tt/wn-ocal.zip?dl=0), then place it in the `staticb` folder
3. Ensure OCAL_IS_ZIPPED is set to True in `flaskapp.cfg`, or you can set it to False and unzip wn-ocal.zip in place (`wn-ocal` folder as subfolder of `staticb`)

### To run locally

Run with Flask's built-in dev server by running `python flaskapp.py` at folder root

### To deploy to OpenShift

Upload big files in `staticb` to OpenShift Online v3

#### web console
- create an ebs persistent volume with RWO access mode under storage
- link to it with `Add Storage` under your deployment configuration and mount it to `/data`
- set your `OPENSHIFT_DATA_DIR` environment variable as `/data/staticb`)

#### command prompt / terminal
- login to the openshift cli
- cd to your local repo folder
- `oc rsync staticb <deployment pod name>:/data`
