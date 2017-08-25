#!//usr/bin/env python

import requests
import configparser

config = configparser.RawConfigParser()
config.read('airplaces.cfg')
apiKey = config.get('credentials','fa_api_key')
username = config.get('credentials','fa_username')
fxmlUrl = "https://flightxml.flightaware.com/json/FlightXML3/"

payload = {'ident':'DL162', 'howMany':'30'}
response = requests.get(fxmlUrl + "FlightInfoStatus", params=payload, auth=(username, apiKey))

if response.status_code == 200:
	decodedResponse = response.json()
	for flight in decodedResponse['FlightInfoStatusResult']['flights']:
		print("{} ({})\t{} {} ({})\t{}\t{}".format(flight['ident'], flight['aircrafttype'],
                                                           flight['origin']['airport_name'], flight['origin']['code'],
                                                           flight['destination']['code'], flight['actual_departure_time'],
                                                           flight['status']))
else:
	print("There was an error retrieving the data from the server.")

