#!/usr/bin/python

# This program scans Jon's Mac for any wayward Logic artifacts and, if found, emails
# someone who can help
#
# It checks for:
# - *.logic projects which aren't in a folder of the same name
# - Folders which have more than one *.logic project in it
# - "Audio Files" folders which don't have a *.logic file sibling
# - *.aif or *.wav files which aren't in an "Audio Files" folder
# - or... any Audio*.aif, Korg*.aif, Kurtzweil*.aif files which aren't in an "Audio Files" folder

from os import walk
import os.path
import notify # For notifying the user (email, log file, etc...)

TARGET_FOLDERS = '/Users/jemenake',
IGNORE_FOLDERS = '/Users/jemenake/Music/GarageBand', "/Users/jemenake/all_hashed_audio"
#TARGET_FOLDERS = ('/Users', '/Volumes/Old Macintosh HD', '/Volumes/Iomega HDD', '/Volumes/Logic Project Archives')
LOGIC9_TARGET_EXT = ".logic"
LOGICX_TARGET_EXT = ".logicx"
AUDIO_FOLDER = "Audio Files"

AUDIO_FILE_PREFIXES = "KURZ", "MOTIF", "VOICE", "YAMAHA", "KORG", "CASIO", "AUDIO", "TRACK"

# Should we look through the .logic/.logicx project files to find out what audio files they expect to see?
INSPECT_LOGIC_FILES = False

logic9_projects = list()
logicx_projects = list()
logic_projects = list()
audio_folders = list()
audio_files = list()


#
# Scans a .logic project for all of the audio files it references
#
# Takes: full pathname to a "*.logic" project folder
# Returns: list of full pathnames to audio files
def get_linked_logic9_audio_filenames(project_path):
	pathnames = list()
	data_pathname = project_path + "/" + "LgDoc" + "/documentData"
#	print "Opening " + data_pathname
	try:
		with open(data_pathname, "r") as myfile:
			data = myfile.read()
			offset = 0
			while True:
				offset = data.find("LFUA", offset)
				if offset == -1:
					break
				filename_start = offset + 10
				filename_end = data.find("\0", filename_start)
				path_start = offset + 138
				path_end = data.find("\0", path_start)
				filename = data[filename_start:filename_end]
				path = data[path_start:path_end]
				pathname = path + "/" + filename
				pathnames.append(pathname)
				offset = path_end
	except:
		pass
#		print "Problem reading " + data_pathname
	return pathnames


##########################################
##########################################
# Scan all target folders, finding all .logic and .logicx folders and save what you find in global vars
#
def scan_target_folders(folders):
	for folder in folders:
#		print "Searching for intact Logic projects in " + folder
#		print

		for (dirpath, dirnames, filenames) in walk(folder):
			for ignore_folder in IGNORE_FOLDERS:
				if dirpath[:len(ignore_folder)] == ignore_folder:
#					print "Ignoring " + dirpath
					break
			else:
				logic9_projects.extend([dirpath + "/" + a for a in dirnames if a[-len(LOGIC9_TARGET_EXT):] == LOGIC9_TARGET_EXT])
				logicx_projects.extend([dirpath + "/" + a for a in dirnames if a[-len(LOGICX_TARGET_EXT):] == LOGICX_TARGET_EXT])
				audio_folders.extend([dirpath + "/" + a for a in dirnames if a == AUDIO_FOLDER])
				audio_files.extend([dirpath + "/" + a for a in filenames if os.path.basename(a).upper().startswith(AUDIO_FILE_PREFIXES) and a.lower().endswith(".aif")])
		logic_projects.extend(logic9_projects)
		logic_projects.extend(logicx_projects)

	return

# 	candidate_folders = sorted(candidate_folders, key=lambda x: len(x), reverse=True)
#
# 	found_folders = dict()
#
# 	while len(candidate_folders) > 0:
# 		candidate = candidate_folders[0]
# 		# Remove the candidate from the list
# 		candidate_folders = candidate_folders[1:]
#
# 		# Is this a "*.logic" folder
# 		if candidate[-len(LOGIC9_TARGET_EXT):] == LOGIC9_TARGET_EXT:
# 			parent_path = os.path.dirname(candidate)
# 			parent_name = os.path.basename(parent_path)
# 			candidate_without_ext = os.path.basename(candidate)[:-len(LOGIC9_TARGET_EXT)]
#
# 			# Remove any other projects whose parent folders also hold this
# 			candidate_folders = [a for a in candidate_folders if not parent_path.startswith(os.path.dirname(a))]
#
# 			# Are there any other "*.logic" folders in the same folder we're in?
# 			other_folders = [a for a in candidate_folders if a.startswith(parent_path) and a != parent_path and a[-len(LOGIC9_TARGET_EXT):] == LOGIC9_TARGET_EXT]
# 			if len(other_folders) == 0:
# 				# Is the folder named the same thing as we are?
# 				if parent_name == candidate_without_ext:
# 					# Is there an "Audio Files" folder in here?
# 					if os.path.isdir(parent_path + "/Audio Files"):
# 						found_folders[candidate] = pathsize(parent_path)
# 						print "0:FOUND:" + candidate
# 					else:
# 						print "1:NOAUDIOFILES:" + candidate
# 				else:
# 					print "2:MISMATCHEDPARENT" + candidate
#
# 			else:
# 				# There are other .logic folders in here. Remove all of them from candidates (but don't remove the *parent*, itself)
# 				candidate_folders = [ a for a in candidate_folders if not a.startswith(parent_path) and a != parent_path]
#
# #	print
# 	for name in [ a for a in sorted(found_folders.keys(), key=lambda x: found_folders[x], reverse=True) ]:
# 		print str(found_folders[name]) + ":" + name


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
def run_checks():

	problems = []

	from collections import Counter
	# Check to see if a .logic project has other .logic projects in the same folder
	project_counts = Counter([os.path.dirname(a) for a in logic_projects])
	for k in project_counts.keys():
		if project_counts[k] != 1:
			problems.append(k + " has " + str(project_counts[k]) + " logic projects in it")

	# Check to see if any audio files aren't in Audio Files folders
	folders_with_audio_files = set([os.path.dirname(a) for a in audio_files])
	for foldername in folders_with_audio_files:
		if not foldername in audio_folders:
			problems.append(foldername + " contains audio files, but it's not an Audio Files folder")

	# Check to see that all Audio Files folders are in a folder with ONE .logic project
	for parent_foldername in [os.path.dirname(a) for a in audio_folders]:
		if parent_foldername in project_counts.keys():
			if project_counts[parent_foldername] != 1:
				problems.append(parent_foldername + " has an Audio Files folder, and MULTIPLE Logic projects")
		else:
			# There were ZERO Logic projects with this folder
			problems.append(parent_foldername + " has an Audio Files folder, but no Logic project")

	if INSPECT_LOGIC_FILES:
		# Check to make sure that all linked audio files exist
		for project in logic_projects:
			missing_audio = list()
			project_audio_files = get_linked_logic9_audio_filenames(project)
			for audio_file in project_audio_files:
				if not os.path.isfile(audio_file):
					missing_audio.append(audio_file)
			if(len(missing_audio) > 0):
				problems.append(project + " is missing the following audio files:")
				for a in missing_audio:
					problems.append("  " + a)

		# Check to make sure that all linked audio files are in their assigned "Audio Files" folder
		for project in logic_projects:
			wayward_audio = list()
			project_audio_files = get_linked_logic9_audio_filenames(project)
			for audio_file in project_audio_files:
				if os.path.dirname(project) + "/Audio Files" != os.path.dirname(audio_file):
					wayward_audio.append(audio_file)
			if(len(wayward_audio) > 0):
				problems.append(project + " references a wayward audio file:")
				for a in wayward_audio:
					problems.append("  " + a)

	# Check for any audio in Audio Files that isn't referenced in the project
	pass

	return problems


#########################################
#########################################
def main():
	scan_target_folders(TARGET_FOLDERS)
	problems = run_checks()
	if len(problems) > 0:
		# We found some problems
		notify.notify("\n".join(problems))

if __name__ == "__main__":
	main()
