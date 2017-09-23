#!//usr/bin/env python
from flask import Flask
import requests
import configparser
import json
from datetime import datetime

app = Flask(__name__)

# get API credentials
config = configparser.RawConfigParser()
config.read('airplaces.cfg')
apiKey = config.get('credentials','fa_api_key')
username = config.get('credentials','fa_username')
fxmlUrl = "https://flightxml.flightaware.com/json/FlightXML3/"

# define app endpoint for testing
@app.route("/<airline>/<flightno>")
def flightDataTest(airline, flightno):
	return airline + flightno

# define main app endpoint
@app.route("/<airline>/<flightno>/<timestamp>")
def locationByFlightNo(airline, flightno, timestamp):
	# convert inputted date to datetime
	photoTime = convertAPITimestamp(timestamp)

	# lookup the requested flight
	payload = {'ident':airline + flightno, 'howMany':'30'}
	response = requests.get(fxmlUrl + "FlightInfoStatus", params=payload,
		auth=(username, apiKey))

	output = ""
	if response.status_code == 200:
		decodedResponse = response.json()
		i = 0
		matchFAID = None
		while (i < len(decodedResponse['FlightInfoStatusResult']['flights']))
			and (matchFAID == None):
			flight = decodedResponse['FlightInfoStatusResult']['flights'][i]

			if flight['status'] == 'En':
				# considering an en-route flight
				departTime = convertFATimestamp(flight['actual_departure_time'])

				if (photoTime > departTime):
					matchFAID = flight['faFlightID']
			elif flight['status'] == 'Arrived':
				# consider an arrived flight
				arriveTime = convertFATimestamp(flight['actual_arrival_time'])
				arriveTime = tzConversionFactor(flight['actual_departure_time'],
					flight['actual_arrival_time'])
				departTime = convertFATimestamp(flight['actual_departure_time'])

				# 	check if photo was taken while i-th flight was airborne
				# assumption: flight numbers associated with two routes won't
				# cause overlap between the ranges of airborne times for their
				# respective timezones because these flight numbers are
				# expected to only cover A-to-B and B-to-C routes. They
				# therefore use different timezones.
				if (photoTime > departTime) and (photoTime < arriveTime):
					matchFAID = flight['faFlightID']

			# output = output + "{} ({})\t{} {} ({})\t{}\t{}\n{}\n".format(flight['ident'], flight['aircrafttype'],
	        #                                                    flight['origin']['airport_name'], flight['origin']['code'],
	        #                                                    flight['destination']['code'], flight['actual_departure_time'],
	        #                                                    flight['status'],flight['faFlightID'])
			i += 1

		if (not matchFAID == None):
			# the flight was found

		else:
			# no matching flight was found
			return json.dumps({'APAPI_status':-2})
		return output
	else:
		return json.dumps({'APAPI_status':-1})

# define future app endpoint
@app.route("/<origin>/<destination>/<date>")
def locationByRoute(origin, destination, date):
	# TODO consider using FindFlight API endpoint
	return 'NOT YET IMPLEMENTED'

# ==================================================
# HELPER FUNCTIONS
# ==================================================

# for a specified datetime, interpolate the positions (lat,long) associated with
# the two immediately adjacent datetimes
def interpolatePosition(specifieddt, dt1, dt2, pos1, pos2):
	# TODO
	return 'NOT YET IMPLEMENTED'

# convert a string of formay YYYYMMDDhhmmss to a datetime object
def convertAPITimestamp(timestamp):
	return datetime(int(timestamp[0:4]), int(timestamp[4:6]),
		int(timestamp[6:8]), int(timestamp[8:10]), int(timestamp[10:12]),
		int(timestamp[12:14]))

# convert a FlightAware timestamp to a datetime object
def convertFATimestamp(timestamp):
	date = timestamp['date']
	time = timestamp['time']
	hour = int(time[0:2])
	minute = int(time[3:5])

	if time[5:] == 'pm' or time[5:] == 'pm':
		hour += 12

	return datetime(int(date[6:10]), int(date[0:2]), int(date[3:5]),
		hour, minute)

# convert arriveTime to departTime's timezone
def tzConversionFactor(departTime, arriveTime):
	# TODO


# run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
