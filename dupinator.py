#! /usr/bin/python

import os
import hashlib
import pickle
from collections import defaultdict

REPOSITORY_BASE = "all_hashed_audio"
# ROOTS = ( "/Users/jemenake", )
ROOTS = ( "/Volumes/Old Macintosh HD", "/Volumes/Old Time Machine")


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

def want(pathname):
	return pathname.endswith(".aif")

pathnames = list()

for rootname in ROOTS:
	print 'Scanning directory "%s"....' % rootname
	for (dirpath, dirnames, filenames) in os.walk(rootname):
		pathnames.extend([ dirpath + "/" + a for a in filenames if want(dirpath + "/" + a)])

	REPOSITORY = rootname + "/" + REPOSITORY_BASE
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

i=0
dupes = []
for aSet in potentialDupes:
	i+=1
	outFiles = []
	hashes = {}
	for fileName in aSet:
		print 'Scanning %d/%d "%s"...' % (i, potentialCount, fileName)
		aFile = file(fileName, 'r')
		hasher = hashlib.md5()
		while True:
			r = aFile.read(4096)
			if not len(r):
				break
			hasher.update(r)
		aFile.close()
		hashValue = hasher.digest()
		if hashes.has_key(hashValue):
			if not len(outFiles):
				outFiles.append(hashes[hashValue])
			outFiles.append(fileName)
		else:
			hashes[hashValue] = [fileName]
	for k in hashes.keys():
		if len(hashes[k]) > 1:
			dupes.append(hashes[k])

dupdump = file("dupedump", "w")
pickle.dump(dupes, dupdump)
dupdump.close()

i = 0
for d in dupes:
	print 'Original is %s' % d[0]
	for f in d[1:]:
		i = i + 1
		print 'Deleting/linking %s' % f
		os.remove(f)
		os.link(d[0],f)
	print
