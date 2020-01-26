


def radar_geocoding(location):
    import requests

    headers = {
        'Authorization': 'prj_live_sk_97e3dcf111b9c25af024c95bf1b695ed087dc411',
    }

    params = (
        ('query', location),
    )
    try:
        response = requests.get('https://api.radar.io/v1/geocode/forward', headers=headers, params=params)
        print (response.json())
        country=response.json()['addresses'][0]['country']
        if country=='United States':

            return {'lat':response.json()['addresses'][0]['latitude'], 'lng': response.json()['addresses'][0]['longitude']}
    except:
        return -1#Fail Condition




location='Mount Pleasant, SC'

print (radar_geocoding(location))