#!/usr/bin/python

#-----------------------------------------------------------------------
# twitter-search-geo
#  - performs a search for tweets by keyword and location, and outputs
#    them to a CSV file.
#-----------------------------------------------------------------------

from twitter import *

import sys
import csv
import argparse
import datetime

# command line arguments
parser = argparse.ArgumentParser(description='This is a command line twitter archiver by yohda.')
parser.add_argument('-q','--keyword', help='keyword string to search on',required=False)
parser.add_argument('-l','--location', help='location as lat,lng',required=False)
parser.add_argument('-lat','--latitude', help='latitude',required=True)
parser.add_argument('-lng','--longitude', help='longitude',required=True)
parser.add_argument('-o','--output',help='Output file name', required=True)
parser.add_argument('-r','--radius',help='Radius in km', required=False)
parser.add_argument('-n','--num',help='minimum results to obtain', required=False)
parser.add_argument('-f','--format',help='file format: csv (default) or kml', required=False)
args = parser.parse_args()

# set default parameters
if not args.radius:
	args.radius = 10
if not args.num:
	args.num = 100
if not args.keyword:
	args.keyword = ''
if not args.format:
	args.format = 'csv'

## show values ##
print  sys.argv[1:]

keyword = args.keyword
location = args.location
latitude = float(args.latitude)	# geographical centre of search
longitude = float(args.longitude)	# geographical centre of search
max_range = int(args.radius)			# search range in kilometres
num_results = int(args.num)		# minimum results to obtain
outfile = args.output

#-----------------------------------------------------------------------
# load our API credentials 
#-----------------------------------------------------------------------
config = {}
execfile("config.py", config)

#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
twitter = Twitter(
		        auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))

#-----------------------------------------------------------------------
# open a file to write (mode "w"), and create a CSV writer object
#-----------------------------------------------------------------------
csvfile = file(outfile, "w")
csvwriter = csv.writer(csvfile)

kmlfile = open(outfile+'.kml','w')
kmlheader = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""
kmlfile.write(kmlheader) # python will convert \n to os.linesep
#-----------------------------------------------------------------------
# add headings to our CSV file
#-----------------------------------------------------------------------
row = [ "created_at", "user", "text", "latitude", "longitude" ]
csvwriter.writerow(row)

#-----------------------------------------------------------------------
# the twitter API only allows us to query up to 100 tweets at a time.
# to search for more, we will break our search up into 10 "pages", each
# of which will include 100 matching tweets.
#-----------------------------------------------------------------------
result_count = 0
last_id = None
not_enough_results_flag = False

while result_count <  num_results and not not_enough_results_flag:

	#-----------------------------------------------------------------------
	# perform a search based on latitude and longitude
	# twitter API docs: https://dev.twitter.com/docs/api/1/get/search
	#-----------------------------------------------------------------------
	query = twitter.search.tweets(q = keyword, geocode = "%f,%f,%dkm" % (latitude, longitude, max_range), count = 100, max_id = last_id)
	# print(query["search_metadata"])

	for result in query["statuses"]:



		#-----------------------------------------------------------------------
		# only process a result if it has a geolocation
		#-----------------------------------------------------------------------
		if result["geo"]:

			if last_id == result["id"]:
				not_enough_results_flag = True
				break

			created_at = result["created_at"]
			# Sun May 17 22:23:19 +0000 2015
			kmldate = datetime.datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")
			kmldate = kmldate.strftime("%Y-%m-%dT%H:%M:%SZ")
			user = result["user"]["screen_name"]
			image = result["user"]["profile_image_url"]
			text = result["text"].encode('utf-8')
			# replace carraige returns
			text = text.replace("\n"," ")
			text = text.replace("\r"," ")
			latitude = result["geo"]["coordinates"][0]
			longitude = result["geo"]["coordinates"][1]

			# now write this row to our CSV file
			row = [ created_at, user, text, latitude, longitude ]
			csvwriter.writerow(row)
			# and write the kml file

			kmlplacemark = """
				<Style id="{user}">
					<IconStyle>
						<scale>1.1</scale>
						<Icon>
							<href>{image}</href>
						</Icon>
					</IconStyle>
				</Style>
				<Placemark>
					<name>{user}</name>
				 	<styleUrl>#{user}</styleUrl>
					<description>
						{created_at}
						{text}
					</description>
					<TimeStamp>
					  <when>{kmldate}</when>
					</TimeStamp>
					<Point>
						<coordinates>{longitude},{latitude},0</coordinates>
					</Point>
				</Placemark>
			"""
			context = {
				"user": user,
				"text": text,
				"created_at": created_at,
				"kmldate": kmldate,
				"latitude": latitude,
				"longitude": longitude,
				"image": image
			}
			kmlfile.write(kmlplacemark.format(**context))
			result_count += 1


			last_id = result["id"]

	#-----------------------------------------------------------------------
	# let the user know where we're up to
	#-----------------------------------------------------------------------
	print "got %d results" % result_count




#-----------------------------------------------------------------------
# we're all finished, clean up and go home.
#-----------------------------------------------------------------------
csvfile.close()
kmlfile.write("</Document></kml>")
kmlfile.close() # you can omit in most cases as the destructor will call if

print "written to %s" % outfile

