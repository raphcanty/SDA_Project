import requests
import pandas as pd
import time

API_URL = "https://api.tfl.gov.uk/StopPoint/Mode/bus"
pages = {}

# Works through each page
for page in range(1, 37):
    params = {'page': page}
    response = requests.get(API_URL, params=params)
    data = response.json()
    print('page:', data['page'], 'page size:', data['pageSize'])

    # Creates dataframe to store stop and relevant information
    pages[page] = pd.DataFrame(data['stopPoints'],
                               columns=['id', 'commonName', 'indicator',
                                        'stopType', 'lat', 'lon'])
    pages[page]['lines'] = [len(s['lines']) for s in data['stopPoints']]
    # Drops stops with missing information - these are mostly duplicates or
    # other non-bus stops such as stop pairs or clusters
    pages[page].dropna(inplace=True)
    time.sleep(2)  # To be kind to TfL's server

# Bundles all stops together
all_stops = pd.concat(pages.values())
all_stops.to_csv('london_stops.csv', index=False)
print('Finished:', len(all_stops), 'stops exported')

