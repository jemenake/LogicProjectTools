#! /usr/bin/python

# Derived from dupinator.py.
#
# This program takes a list of pathnames to audio files and moves them to a central archive.
# It replaces the original with a symbolic link to the archived version.
# The archived version will have several names (all hard-linked): the MD5 hash (with the extension)
# appended to it, *plus* all names that the file has been archived as.
#
# For example:
#   Audio#123.aif
# might get archived to:
#   /all_hashed_audio/a/f/af171f6a82b3caf793d3b3ac3.aif
#   /all_hashed_audio/a/f/af171f6a82b3caf793d3b3ac3.aliases/Audio#123.aif
# if the same audio is encountered in a file called:
#   Audio#987.aif
# then it will be replaced by a symlink to the MD5-named file and an alias will be added:
#   /all_hashed_audio/a/f/af171f6a82b3caf793d3b3ac3.aliases/Audio#987.aif
#
#
# WHAT IS THIS FOR?
#
# This program is for filesystems where there are a lot of large audio files and there is a
# high incidence of duplicates. This program allows for a great deal of space to be reclaimed.
#
# 2015-04-26 - joe@emenaker.com


import os
import hashlib
import pickle
from collections import defaultdict

REPOSITORY_BASE = "/Volumes/Old Time Machine/all_hashed_audio"
# ROOTS = ( "/Users/jemenake", )
ROOTS = ("/Volumes/Old Macintosh HD", "/Volumes/Old Time Machine")


def pickle_data(data, pathname):
	picklefile = file(pathname, "w")
	pickle.dump(data, picklefile)
	picklefile.close()


###
### If a directory doesn't exist, create it
###
def ensuredir(pathname):
	if not os.path.isdir(pathname):
		try:
			os.mkdir(pathname)
		except:
			print "Can't create mandatory directory: " + pathname + " : Does it exist? Do we have permissions?"
			exit()

###
### If a file is in the archive
###
def is_in_archive(md5):
	pathname = get_archive_md5_name(md5)
	return os.path.isfile(pathname)

###
### If an archived file with a MD5 is listed with a particular name
###
def has_alias(md5, alias):
	pathname = get_archive_alias_name(md5, alias)
	return os.path.isfile(pathname)

###
### Do we want this file?
### (Used to indicate if a file qualifies as an audio file)
###
def want(pathname):
	return pathname.endswith(".aif")


###
###
###
pathnames = list()

for rootname in ROOTS:
	print 'Scanning directory "%s"....' % rootname
	for (dirpath, dirnames, filenames) in os.walk(rootname):
		pathnames.extend([ dirpath + "/" + a for a in filenames if want(dirpath + "/" + a)])

	REPOSITORY = REPOSITORY_BASE
	PICKLE_FILE = REPOSITORY + "/" + "hash_values.pickle"

	print "  creating hash folders..."
	# Make sure that we have a place to stick all of the links for the hashes
	ensuredir(REPOSITORY)
	## Make a two-deep folder tree for holding all of the hashes
	digits = range(10)
	digits.extend([ 'a', 'b', 'c', 'd', 'e', 'f' ])
	for digit1 in digits:
		dir1 = REPOSITORY + "/" + str(digit1)
		ensuredir(dir1)
		for digit2 in digits:
			dir2 = dir1 + "/" + str(digit2)
			ensuredir(dir2)

	print "  calcuating hashes..."
	# Calc the hash-value of every file
	thehashes = defaultdict(list)
	hashes_by_pathname = dict()
	for pathname in pathnames:
		print pathname

		hashValue = hashlib.md5(pathname).hexdigest()
		thehashes[hashValue].append(pathname)
		basename = os.path.basename(pathname)
		if basename in hashes_by_pathname.keys() and hashes_by_pathname[basename] != hashValue:
			print "There are multiple files named " + basename + " and they have different hash values!"

	pickle_data(thehashes, PICKLE_FILE)

	print "  making the hard-links..."
	# Make the hash links
	for hash in thehashes.keys():
		print hash
		hash_pathname = REPOSITORY + "/" + hash[0] + "/" + hash[1] + "/" + hash
		# Link the first pathname in our list of files with this hash to a file with the hashvalue
		if not os.path.isfile(hash_pathname):
			os.link(thehashes[hash][0], hash_pathname)
		alias_dir = hash_pathname + ".aliases"
		ensuredir(alias_dir)
		for pathname in thehashes[hash]:
			alias_pathname = alias_dir + "/" + os.path.basename(pathname)
			if not os.path.isfile(alias_pathname):
				os.link(hash_pathname, alias_pathname)
			print "  " + pathname

exit()

print 'Finding potential dupes...'
potentialDupes = []
potentialCount = 0
trueType = type(True)
sizes = filesBySize.keys()
sizes.sort()
for k in sizes:
	inFiles = filesBySize[k]
	outFiles = []
	hashes = {}
	if len(inFiles) is 1: continue
	print 'Testing %d files of size %d...' % (len(inFiles), k)
	for fileName in inFiles:
		if not os.path.isfile(fileName):
			continue
		aFile = file(fileName, 'r')
		hasher = hashlib.md5(aFile.read(1024))
		hashValue = hasher.digest()
		if hashes.has_key(hashValue):
			x = hashes[hashValue]
			if type(x) is not trueType:
				outFiles.append(hashes[hashValue])
				hashes[hashValue] = True
			outFiles.append(fileName)
		else:
			hashes[hashValue] = fileName
		aFile.close()
	if len(outFiles):
		potentialDupes.append(outFiles)
		potentialCount += len(outFiles)
del filesBySize

print 'Found %d sets of potential dupes...' % potentialCount
print 'Scanning for real dupes...'


dupdump = file("dupedump", "w")
pickle.dump(dupes, dupdump)
dupdump.close()

