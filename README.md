# pytweet
pytweet a geotagged twitter archiver
![pytweet kml output](https://github.com/yohman/pytweet/blob/master/images/pytweet.png "pytweet kml output")

## What is pytweet?
pytweet borrows from the github python-twitter-example project, but focuses only on the archival process of geotagged tweets.  With this command line tool, you can specify a search paramater, a geo location (as latitude and longitude coordinates) a radius (in meters) and the number of tweets you want to archive.

## What does pytweet produce?
pytweet outputs results in both a csv file and a kml file.  The kml files is spatially and temporally marked up, allowing you to animate time in Google Earth to see the progression of tweets over time.

##Examples
```
python twitter-search-geo.py -lat 34.02109014442118 -lng -118.41173249999997 -q FIFA -r 100 -n 200 -o FIFA.csv
```
