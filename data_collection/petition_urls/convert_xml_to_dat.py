'''
This file takes xml files directly from the change.org sitemap as input.
It parses this content and extracts all available petition urls, concentrating
solely on petitions that are in english and from countries that are close
culturally.
'''

# Imports
import xmltodict

# Define method to convert xml data to python dictionary
def convert(xml_file, xml_attribs=True):
    with open(xml_file, "rb") as f:
        xml_dict = xmltodict.parse(f, xml_attribs=xml_attribs)
        return xml_dict

# Change.org sitemap data is segmented by country so loop over relevant countries
for country_code in ['CA', 'AU', 'GB', 'US']:

	# Convert xml to list
	file = "en-{}.xml".format(country_code)
	data = [url['loc'] for url in convert(file)['urlset']['url']]

	# Filter for non-english pages (special characters always include a %)
	data = filter(lambda x: "%" not in x, data)

	# Split dataset to enable parallelized data collection
	if country_code == 'US':

		# Split data into 4 parts
		split_point = len(data)/4
		data = [data[0:split_point], data[split_point:2*split_point], data[split_point*2:split_point*3], data[split_point*3:]]

		# Write urls to new dat files
		for part in range(4):
			with open("en-{0}_{1}.dat".format(country_code, part+1), "w") as f:
			    for url in data[part]:
			        f.write(url + "\n")

	else:

		# Split data into 2 parts
		split_point = len(data)/2
		data = [data[0:split_point], data[split_point:]]

		# Write urls to new dat files
		for part in range(2):
			with open("en-{0}_{1}.dat".format(country_code, part+1), "w") as f:
			    for url in data[part]:
			        f.write(url + "\n")
