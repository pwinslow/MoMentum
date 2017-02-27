import sys
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
from constants import api_key

def get_response(url):

	r = requests.request("GET", url)

	# If status code is 429, give api a break
	while r.status_code == 429:
	    sleep(2)
	    r = requests.request("GET", url)

	# If there is an error code, then print message but continue anyway
	if r.status_code != 200:
		return "Error: Bad status code"
	else:
		return r

def fetch(url):

    # Get petition id
	id_url = "https://api.change.org/v1/petitions/get_id?petition_url={}&api_key={}".format(url.strip(), api_key)
	response = get_response(id_url)
	if response == "Error: Bad status code":
		print "Error: Bad status code"
		sys.exit(2)
	else:
		id_json = json.loads(response.text)
		petition_id = id_json["petition_id"]

		# Generate soup, parse html to obtain json, and extract petition id
		#soup = BeautifulSoup(r.text)
		#json_data = json.loads(soup.findAll("script", {"id":"clientData"})[0].get_text())
		#petition_id = json_data['bootstrapData']['model']['data']['id']

		# Use petition id to define urls for api calls
		petition_url = "https://api.change.org/v1/petitions/" + str(petition_id) + "?api_key={}".format(api_key)
		#update_url = "https://api.change.org/v1/petitions/" + str(petition_id) + "/updates?api_key={}".format(api_key)

		# Call api and translate results to json
		#update_response = requests.request("GET", update_url)
		#update_json = json.loads(update_response.text)

		#if len(update_json["updates"]) <= 1:
		#    return "Not even enough mo'mentum in this particular petition yet to judge. Better get moving!", update_json
		#else:

		response = get_response(petition_url)
		if response == "Error: Bad status code":
			print "Error: Bad status code"
			sys.exit(2)
		else:
			petition_json = json.loads(response.text)

			#response = requests.request("GET", petition_url)
		    #petition_json = json.loads(response.text)

			#return petition_json, update_json
			return petition_json
