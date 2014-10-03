#!/usr/bin/python

from os import walk
import os.path


TARGET_FOLDER = '/Users/jemenake'
TARGET_EXT = ".logic"


##########################################
##########################################
def process_folder(folder):
	print "Searching for intact Logic projects in " + folder
	print

	candidate_folders = []
	for (dirpath, dirnames, filenames) in walk(folder):
		# push any *.logic files onto the end of the arrray
#		candidate_folders.extend([dirpath + "/" + a for a in dirnames])
		candidate_folders.extend([dirpath + "/" + a for a in dirnames if a[-len(TARGET_EXT):] == TARGET_EXT])

	candidate_folders = sorted(candidate_folders, key=lambda x: len(x), reverse=True)

	found_folders = dict()

	while len(candidate_folders) > 0:
		candidate = candidate_folders[0]
		# Remove the candidate from the list
		candidate_folders = candidate_folders[1:]

		# Is this a "*.logic" folder
		left = candidate[-len(TARGET_EXT):]
		if candidate[-len(TARGET_EXT):] == TARGET_EXT:
			parent_path = os.path.dirname(candidate)
			parent_name = os.path.basename(parent_path)
			candidate_without_ext = os.path.basename(candidate)[:-len(TARGET_EXT)]

			# Remove any other projects whose parent folders also hold this
			candidate_folders = [ a for a in candidate_folders if not parent_path.startswith(os.path.dirname(a))]

			# Are there any other "*.logic" folders in the same folder we're in?
			other_folders = [a for a in candidate_folders if a.startswith(parent_path) and a != parent_path and a[-len(TARGET_EXT):] == TARGET_EXT]
			if len(other_folders) == 0:
				# Is the folder named the same thing as we are?
				if parent_name == candidate_without_ext:
					# Is there an "Audio Files" folder in here?
					if os.path.isdir(parent_path + "/Audio Files"):
						found_folders[candidate] = pathsize(parent_path)
						print "0:FOUND:" + candidate
					else:
						print "1:NOAUDIOFILES:" + candidate
				else:
					print "2:MISMATCHEDPARENT" + candidate

			else:
				# There are other .logic folders in here. Remove all of them from candidates (but don't remove the *parent*, itself)
				candidate_folders = [ a for a in candidate_folders if not a.startswith(parent_path) and a != parent_path]

	print
	for name in [ a for a in sorted(found_folders.keys(), key=lambda x: found_folders[x], reverse=True) ]:
		print str(found_folders[name]) + ":" + name


##########################################
##########################################
def pathsize(path):
	size = 0
	for (dirpath, dirnames, filenames) in walk(path):
		for filename in filenames:
			size += + os.lstat(dirpath + "/" + filename).st_size
	return size


#########################################
#########################################
def main():
	process_folder(TARGET_FOLDER)

if __name__ == "__main__":
	main()
