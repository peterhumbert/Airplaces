#!//usr/bin/env python
from flask import Flask
import requests
import configparser
import json
from datetime import datetime, tzinfo, timedelta

app = Flask(__name__)

# get API credentials
config = configparser.RawConfigParser()
config.read('airplaces.cfg')
apiKey = config.get('credentials','fa_api_key')
username = config.get('credentials','fa_username')
fxmlUrl = "https://flightxml.flightaware.com/json/FlightXML3/"

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)

utc = UTC()

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
		try:
			while (i < len(decodedResponse['FlightInfoStatusResult']['flights'])
				and matchFAID == None):
				flight = decodedResponse['FlightInfoStatusResult']['flights'][i]

				if 'En' in flight['status']:
					# considering an en-route flight
					departTime = convertFATimestamp(flight['actual_departure_time'])

					if (photoTime > departTime):
						# flight found!
						matchFAID = flight['faFlightID']
						photoTime -= getUTCoffset(flight['actual_departure_time'])
				elif 'Arrived' in flight['status']:
					# consider an arrived flight
					arriveTime = convertFATimestamp(flight['actual_arrival_time'])
					arriveTime += tzConversionFactor(
						flight['actual_departure_time'],
						flight['actual_arrival_time'])  # convert arriveTime to
														# departure timezone
					departTime = convertFATimestamp(flight['actual_departure_time'])

					# check if photo was taken while i-th flight was airborne
					# assumption: flight numbers associated with two routes won't
					# cause overlap between the ranges of airborne times for their
					# respective timezones because these flight numbers are
					# expected to only cover A-to-B and B-to-C routes. They
					# therefore use different timezones.
					if (photoTime > departTime) and (photoTime < arriveTime):
						# flight found!
						matchFAID = flight['faFlightID']
						photoTime -= getUTCoffset(flight['actual_departure_time'])
				i += 1
				## end of while loop
		except Exception as e:
			# FlightInfoStatus call succeeded but didn't find any matching flights
			return json.dumps({'APAPI_status':-5})

		if (matchFAID != None):
			# the flight was found
			payload = {'ident':matchFAID}
			response = requests.get(fxmlUrl + "GetFlightTrack", params=payload,
				auth=(username, apiKey))

			if response.status_code == 200:
				decodedResponse = response.json()

				try:
					j = 0
					tBefore = None	# for timestamp immediately Before photoTime
					tAfter = None	# for timestamp immediately After photoTime
					posBefore = None
					posAfter = None
					while (j < (len(decodedResponse['GetFlightTrackResult']['tracks']) - 1)
						and (tBefore == None) and (tAfter == None)):
						track1 = decodedResponse['GetFlightTrackResult']['tracks'][j]
						track2 = decodedResponse['GetFlightTrackResult']['tracks'][j+1]

						if (datetime.fromtimestamp(track1['timestamp'],utc) < photoTime and
							datetime.fromtimestamp(track2['timestamp'],utc) > photoTime):
							# photo was taken between the two current track entries
							tBefore = datetime.fromtimestamp(track1['timestamp'],utc)
							tAfter = datetime.fromtimestamp(track2['timestamp'],utc)

							posBefore = {'longitude': track1['longitude'],
								'latitude': track1['latitude']}
							posAfter = {'longitude': track2['longitude'],
								'latitude': track2['latitude']}

							photoPos = interpolatePosition(photoTime, tBefore,
								tAfter, posBefore, posAfter)

							return json.dumps({'APAPI_status':0,
								'latitude':photoPos['latitude'],
								'longitude':photoPos['longitude']})
						j += 1
						## end of the while loop
					# outside the while loop = position not determined
					return json.dumps({'APAPI_status':-4})
				except Exception as e:
					# GetFlightTrack call succeeded but didn't find track data
					return json.dumps({'APAPI_status':-6})
			else:
				# GET failed
				return json.dumps({'APAPI_status':-3})
		else:
			# no matching flight was found
			return json.dumps({'APAPI_status':-2})
		return output
	else:
		# GET failed
		return json.dumps({'APAPI_status':-1})

# define future app endpoint
# @app.route("/<origin>/<destination>/<date>")
# def locationByRoute(origin, destination, date):
# 	# TODO consider using FindFlight API endpoint
# 	return 'NOT YET IMPLEMENTED'

# ==================================================
# HELPER FUNCTIONS
# ==================================================

# for a specified datetime, interpolate the positions (lat,long) associated with
# the two immediately adjacent datetimes
def interpolatePosition(specifieddt, dt1, dt2, pos1, pos2):
	multiplier = (specifieddt-dt1)/(dt2-dt1)
	latdiff = pos2['latitude']-pos1['latitude']
	londiff = pos2['longitude']-pos1['longitude']
	return {'latitude':pos1['latitude'] + multiplier*latdiff,
		'longitude':pos1['longitude'] + multiplier*londiff}

# convert a string of formay YYYYMMDDhhmmss to a datetime object
def convertAPITimestamp(timestamp):
	return datetime(int(timestamp[0:4]), int(timestamp[4:6]),
		int(timestamp[6:8]), int(timestamp[8:10]), int(timestamp[10:12]),
		int(timestamp[12:14]), 0, utc)

# convert a FlightAware timestamp to a datetime object
def convertFATimestamp(timestamp):
	date = timestamp['date']
	time = timestamp['time']
	hour = int(time[0:2])
	minute = int(time[3:5])

	if (time[5:] == 'PM' or time[5:] == 'pm') and hour < 12:
		hour += 12

	return datetime(int(date[6:10]), int(date[0:2]), int(date[3:5]),
		hour, minute, 0, 0, utc)

# convert arriveTime to departTime's timezone
def tzConversionFactor(departTimestamp, arriveTimestamp):
	departUTCoffset = (departTimestamp['localtime']
		- departTimestamp['epoch'])/3600
	arriveUTCoffset = (arriveTimestamp['localtime']
		- arriveTimestamp['epoch'])/3600
	return timedelta(hours=departUTCoffset-arriveUTCoffset)

# return the UTC offset of a {localtime, epoch} timestamp;
# to be used with departure time to convert photo time to UTC
def getUTCoffset(timestamp):
	return timedelta(hours=(timestamp['localtime']-timestamp['epoch'])/3600)

# run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
