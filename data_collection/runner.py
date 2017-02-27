'''
This file sets up multiple jobs to run on a PBS cluster. Each job collects
a portion of the total dataset via the change.org api by pointing.
'''

# Imports
import os
import sys
import pandas as pd
from os.path import isfile as file_exists

# Define full path to working folder
path="/full/path/to/working/folder"

# Define list of data files
file_list = ['en-CA_1.dat',
			 'en-CA_2.dat',
			 'en-US_1.dat',
			 'en-US_2.dat',
			 'en-US_3.dat',
			 'en-US_4.dat',
			 'en-AU_1.dat',
			 'en-AU_2.dat',
			 'en-GB_1.dat',
			 'en-GB_2.dat']
run_name = [x.split('-')[1].split('.')[0] for x in file_list]

# Read in list of api keys used for data collection
if file_exists("APIKey_list"):
	apis = pd.read_csv("APIKey_list", delimiter=",")
	apis.columns = [x.strip() for x in apis.columns]
	api_keys = [key.strip() for key in apis.api_key.values]
else:
	print "Please check path to API key list..."
	sys.exit(2)

# Set up 10 separate jobs for data collection via change.org api
for cnt in range(10):

	# Delete previous submission script
	if file_exists("script.sh"):
		os.remove("script.sh")

	# Write simple script for PBS cluster submission
	with open("script.sh", "w") as f:
		f.write("#/bin/sh\n")
		f.write("#PBS -N Scan{}\n".format(run_name[cnt]))
		f.write("python {0}/get_data.py {0}/petition_urls/{1} {2}\n".format(path,
																			file_list[cnt],
																			api_keys[cnt]))

	# Submit job
	os.system("chmod +x script.sh")
	os.system("qsub -e berr.log -o bout.log script.sh")
