'''
This file takes a list of change.org petition urls and an api key as input,
both passed as cmd line arguments. It then extrapolates the number
of days required to meet the specified signature goal and organizes this,
along with all raw petition data, into a pandas dataframe and writes it to csv.
'''

# Imports
import sys
import json
import requests
import pandas as pd
from time import sleep

# Define output path
output_path = "/home/pwinslow/changeDOTorg/daycount_results/"

# Define method to get api key and url data from cmd line arguments
def get_key_and_urls():

	# Check for country code
	try:
		file = sys.argv[1]
		output_prepend = file.split('/')[-1].split('-')[-1].split('.')[0]
		country_code = output_prepend.split('_')[0]
	except IndexError:
		print """Error: No country code given. Please use the format:\n
				 python get_data.py country_code api_key
				 country_code=US|CA|AU|GB"""
		sys.exit(2)

	# Check for api key
	try:
        api_key = sys.argv[2]
	except IndexError:
        print """Error: No API key given. Please use the following format:\n
				 python get_data.py country_code api_key
				 country_code=US|CA|AU|GB"""
        sys.exit(2)

	# Read in raw data
	with open(file, 'r+') as f:
	        data = f.readlines()

	# Return api key, name of file that data came from, and data
	return api_key, output_prepend, data

# Define method to handle api requests
def get_response(url):

	# Make api call
	r = requests.request("GET", url)

	# If status code is 429, give api a break
    while r.status_code == 429:
        sleep(2)
        r = requests.request("GET", url)

	# If there is an error code, return error. Otherwise, return api response
    if r.status_code != 200:
        return "Error: Bad status code"
	else:
		return r

# Define method to get petition_id from petition url
def get_petitionid(url, api_key):

	# Call api with petition url
	id_url = "https://api.change.org/v1/petitions/get_id?petition_url={}&api_key={}".format(url.strip(), api_key)
    response = get_response(id_url)

	# If there is an error code, return error. Otherwise, return petition id
	if response == "Error: Bad status code":
		return response
	else:
    	id_json = json.loads(response.text)
    	petition_id = id_json["petition_id"]
		return petition_id

# Define method to collect signature goal and updates from a given petition
def collect_updates(petition_id, api_key):

	# Define update and petition urls for api calls
	update_url = "https://api.change.org/v1/petitions/" + str(petition_id) + "/updates?page=1&api_key={}".format(api_key)
	petition_url = "https://api.change.org/v1/petitions/" + str(petition_id) + "?api_key={}".format(api_key)

	# Make api call for petition data
	petition_response = get_response(petition_url)

	if petition_response == "Error: Bad status code":
		return petition_response
	else:
		# Extract signature goal
		petition_json = json.loads(petition_response.text)

		# Collect updates
		updates = []
		while update_url != None:
			update_response = get_response(update_url)
			if update_response == "Error: Bad status code":
				return update_response
			else:
				update_json = json.loads(update_response.text)
				for update in update_json["updates"]:
				    if update["title"] and update["title"].isdigit():
				        updates.append( [update["created_at"], update["title"]] )
				if update_json["next_page_endpoint"] == None:
				    update_url = None
				else:
				    update_url = update_json["next_page_endpoint"] + "&api_key={}".format(api_key)

		return petition_json, updates

# Define method to calculate signature accumulation rate based on petition updates
def calc_rate(petition_goal, updates):

	# Insert update data into dataframe with columns for time (in mins) and signature count
	tmp_df = pd.DataFrame(updates, columns=("time", "count"))
	tmp_df.time = tmp_df.time.apply(pd.to_datetime)
	tmp_df["minutes"] = (tmp_df.time - tmp_df.time.shift(1)).drop(0).apply(lambda x: x.seconds * 1.0 / 60)
	tmp_df = tmp_df.drop(0)
	tmp_df.minutes = tmp_df.minutes.cumsum()

	# Assume that signature count was zero at zero minutes
	cnt_list = [0]
	for update in tmp_df["count"].tolist():
	    cnt_list.append( int( update ) )
	cnt_series = pd.Series(cnt_list)

	min_list = [0]
	for update in tmp_df.minutes.tolist():
	    min_list.append( update )
	min_series = pd.Series( min_list )

	# Perform OLS to determine slope parameter (signature accumulation rate)
	result = pd.ols(y=cnt_series, x=min_series, intercept=False)
	rate = result.beta.x

	return rate


if __name__ == "__main__":

	# Initialize dataframe to hold petition data
	df = pd.DataFrame(columns=('petition_id',
							   'title',
							   'status',
							   'url',
							   'overview',
							   'targets',
							   'letter_body',
							   'signature_count',
							   'image_url',
							   'category',
							   'goal',
							   'created_at',
							   'end_at',
							   'signature_rate',
							   'creator_name',
							   'creater_url',
							   'organization_name',
							   'organization_url'))

	# Get api key and url data
	api_key, output_prepend, urldata = get_key_and_urls()

	# Loop over urls
	for cnt, url in enumerate(urldata):

		# Get petition id
		petition_id = get_petitionid(url, api_key)
		if petition_id == "Error: Bad status code":
			continue

		# Get petition json and list of all updates
		result = collect_updates(petition_id, api_key)
		if result == "Error: Bad status code":
			continue
		petition_json, updates = result

		# If there's enough updates to extrapolate a decent slope from,
		# get day count and insert all petition data into dataframe
		if len(updates) >= 5:
			try:
				rate = calc_daycount(petition_json["goal"], updates)
				df.loc[cnt] = [str(petition_id),
							   json_result['title'],
							   json_result['status'],
							   url,
							   json_result['overview'],
							   json_result['targets'],
							   json_result['letter_body'],
							   json_result['signature_count'],
							   json_result['image_url'],
							   json_result['category'],
							   json_result['goal'],
							   json_result['created_at'],
							   json_result['end_at'],
							   rate,
							   json_result['creator_name'],
							   json_result['creator_url'],
							   json_result['organization_name'],
							   json_result['organization_url']]
			except:
				with open(output_path + "errors.dat", 'a') as f:
            		f.write( "Bad petition id: {}".format(petition_id) )

		# Export dataframe as csv every 100 entries
		if cnt % 100 == 0:
	    	df.to_csv(output_path + output_prepend + '_data.csv',
					  encoding='utf-8',
					  index=False)

	# Export full dataframe as csv
	df.to_csv(output_path + output_prepend + '_data.csv',
			  encoding='utf-8',
			  index=False)
