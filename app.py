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
@app.route("/")
def test():
	return username

@app.route("/<airline>/<flightno>")
def flightDataTest(airline, flightno):
	return airline + flightno

@app.route("/<airline>/<flightno>/<date>")
def hello_user(airline, flightno, date):
	try:
		payload = {'ident':airline+flightno, 'howMany':'30'}
		response = requests.get(fxmlUrl + "FlightInfoStatus", params=payload, auth=(username, apiKey))
	except Exception as inst:
		return inst

	if response.status_code == 200:
		decodedResponse = response.json()
		return decodedResponse
		# for flight in decodedResponse['FlightInfoStatusResult']['flights']:
		# 	print("{} ({})\t{} {} ({})\t{}\t{}\n{}\n".format(flight['ident'], flight['aircrafttype'],
	    #                                                        flight['origin']['airport_name'], flight['origin']['code'],
	    #                                                        flight['destination']['code'], flight['actual_departure_time'],
	    #                                                        flight['status'],flight['faFlightID']))
	else:
		return "There was an error retrieving the data from the server."

# define future app endpoint
@app.route("/<origin>/<destination>/<date>")
def locationByRoute(origin, destination, date):
	return 'NOT YET IMPLEMENTED'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
