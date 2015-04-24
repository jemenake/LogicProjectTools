
# Folder Policy Enforcer
#
# 2015-04-23 - joe@emenaker.com
#

import os
import os.path
import re
import fnmatch
import time

POLICYFILE_NAME = ".folderpolicy"
POLICY_REGEXP = "^(DENY|ACCEPT) +(.*)$"
policy_matcher = re.compile(POLICY_REGEXP)

# How many seconds to wait before doing the next folder
THROTTLING = 0.03

violations = list()


def read_policy(policyfile_path):
	policy = list()
	with open(policyfile_path, "rt") as f:
		for line in f.readlines():
			line = line.rstrip()
			if policy_matcher.match(line) is not None:
				policy.append(line)
	return policy

def meets_policy(pathname, policy):
	basename = os.path.basename(pathname)
	for policy_item in policy:
		m = policy_matcher.match(policy_item)
		if m is not None:
			action = m.group(1)
			wildcard = m.group(2)
			if fnmatch.fnmatch(basename, wildcard):
				# We found a matching line
				if action == "DENY":
					return False
				if action == "ACCEPT":
					return True
				else:
					print("Unknown action: {0}".format(action))
	return True


def walk_folder(folder, policy=[]):

	time.sleep(THROTTLING)

	print("Trying {0}".format(folder))
	policyfile_path = os.path.join(folder, POLICYFILE_NAME)
	if os.path.isfile(policyfile_path):
		policy = read_policy(policyfile_path)

	try:
		for name in os.listdir(folder):
			fullpath = os.path.join(folder, name)
			if os.path.islink(fullpath):
				next
			elif os.path.isdir(fullpath):
				walk_folder(fullpath, policy)
			elif os.path.isfile(fullpath):
				if not meets_policy(fullpath, policy):
					violations.append("{0} is not allowed in {1}".format(name, folder))
	except OSError as e:
		# Probably a permission problem
		pass


SENDER = "joe@emenaker.com"
### Mail-sending stuff
def send_report_to(recipient):
	# Import smtplib for the actual sending function
	import smtplib

	# Import the email modules we'll need
	from email.mime.text import MIMEText

	msg = MIMEText("\n".join(violations))

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = "You have some files in places they shouldn't be"
	msg['From'] =SENDER
	msg['To'] = recipient

	s = smtplib.SMTP('localhost')
	s.sendmail(SENDER, [recipient], msg.as_string())
	s.quit()


walk_folder("/Users")
for line in violations:
	print line