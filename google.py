import googlemaps

gmaps = googlemaps.Client(key='AIzaSyDd7rRS3BjA5UhFJSJhaFgNLZmqHF4OCWo')



def google_geocoding(location):
    try:
        geocode_result = gmaps.geocode(location)
        # print(pprint(geocode_result))
        return geocode_result[0]['geometry']['location']
    except:
        return -1#Fail

google_geocoding('1600 Amphitheatre Parkway, Mountain View, CA')