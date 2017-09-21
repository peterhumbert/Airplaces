#!//usr/bin/env python
from flask import Flask
import requests
import configparser
import json

app = Flask(__name__)

# get API credentials
config = configparser.RawConfigParser()
config.read('airplaces.cfg')
apiKey = config.get('credentials','fa_api_key')
username = config.get('credentials','fa_username')
fxmlUrl = "https://flightxml.flightaware.com/json/FlightXML3/"

# define app endpoint
@app.route("/<airline>/<flightno>/<date>")
def hello_user(airline, flightno, date):
	payload = {'ident':airline+flightno, 'howMany':'30'}
	response = requests.get(fxmlUrl + "FlightInfoStatus", params=payload, auth=(username, apiKey))

	if response.status_code == 200:
		decodedResponse = response.json()
		for flight in decodedResponse['FlightInfoStatusResult']['flights']:
			print("{} ({})\t{} {} ({})\t{}\t{}\n{}\n".format(flight['ident'], flight['aircrafttype'],
	                                                           flight['origin']['airport_name'], flight['origin']['code'],
	                                                           flight['destination']['code'], flight['actual_departure_time'],
	                                                           flight['status'],flight['faFlightID']))
	else:
		print("There was an error retrieving the data from the server.")

# define future app endpoint
@app.route("/<origin>/<destination>/<date>")
def locationByRoute(origin, destination, date):
	return 'NOT YET IMPLEMENTED'
