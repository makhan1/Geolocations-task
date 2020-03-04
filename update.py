import redis
import json
#import urllib2 # The following statement works instead
import urllib.request
import datetime
from calendar import timegm
import time
import os
import sys


REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r = redis.StrictRedis.from_url(REDIS_URL)

# NASA's station FDO updates this page with very precise data. Only using a
# small bit of it for now.
url = "http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html"


def update_tle():
    # Open a http request
#    req = urllib2.Request(url) # These may work with urlib2 
#    response = urllib2.urlopen(req)
    response = urllib.request.urlopen(url) # R has been converted to lowercase
    data = response.read()

    # parse the HTML
    data = data.split(b"<PRE>")[1]    # b specifies it as bytes
    data = data.split(b"</PRE>")[0]    # b specifies it as bytes 
    data = str(data.split(b"Vector Time (GMT): ")[1:])  # b specifies it as bytes
    data = data.replace("[b'2019","2019")      # Replacing 
    data = data.replace(", b'2019",",2019")    # Replacing  

    for group in data.split(","):     # Instead of data, data plitted with , as delimiter has been used in the loop     
        # Time the vector is valid for
        datestr = group[0:17]   # Groups together the string to be passed to striptime in the following format
#        print(datestr)
        # parse date string
        tm = time.strptime(datestr, "%Y/%j/%H:%M:%S")

        # change into more useful datetime object
        dt = datetime.datetime(tm[0], tm[1], tm[2], tm[3], tm[4], tm[5])

        # Debug
        #print (dt)

        # More parsing
        tle = group.split("TWO LINE MEAN ELEMENT SET")[1]
        tle = tle[8:163]  # Instead of 160, 163 has been used for the sake of completion
#        print(tle)
        lines = tle.split('\\n')[0:3]  # splits the lines into list with three values
 #       print(lines)
#        print(lines[0].strip())
        # Most recent TLE
        now = datetime.datetime.utcnow()
#        print((dt - now).days)
        if (dt - now).days >= 0: # Select Only the recent one
            # Debug Printing
            """
            print (dt)
            for line in lines:
                print (line.strip())
            print ("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            """

            tle = json.dumps([lines[0].strip(), lines[1].strip(), lines[2].strip()]) 
#            print(tle)
            r.set("iss_tle", tle)
            r.set("iss_tle_time", timegm(dt.timetuple()))
            r.set("iss_tle_last_update", timegm(now.timetuple()))
            break


if __name__ == '__main__':
    print ("Updating ISS TLE from JSC...") # Print commands have been updated to correct syntax
    try:
        update_tle()
    except:
        exctype, value = sys.exc_info()[:2]
        print("Error:", exctype, value)
