import sys
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
from constants import api_key


def fetch(url):

    # Get url of petition
	r = requests.get(url)

	# If status code is 429, give api a break
	while r.status_code == 429:
	    sleep(2)
	    r = requests.get(url)

	# If there is an error code, then stop and print message
	if r.status_code != 200:
        print "HTML status code {0} has occurred while requesting content from {1}".format(r.status_code, url)
        sys.exit(2)

	# Generate soup, parse html to obtain json, and extract petition id
	soup = BeautifulSoup(r.text)
	json_data = json.loads(soup.findAll("script", {"id":"clientData"})[0].get_text())
	petition_id = json_data['bootstrapData']['model']['data']['id']

	# Use petition id to define url for api call
	api_url = "https://api.change.org/v1/petitions/" + str(petition_id) + "?api_key={}".format(api_key)

	# Call api and translate results to json
	response = requests.request("GET", api_url)
 	json_result = json.loads(response.text)

    return json_result
