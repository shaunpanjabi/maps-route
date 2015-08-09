#############################################################################################
# Maps Trip Duration Data Collector
# Author: Shaun Panjabi
#
# Description:
#   -Plot all trip durations within a time period
#
# See Bing Routes API for more info on what parameters to use.
#     https://msdn.microsoft.com/en-us/library/ff701717.aspx
#
#############################################################################################

from datetime import datetime, timedelta
from time import sleep
import json, requests
import os.path
import pickle

class MapsRoute():
    """
    Class is used to build proper URL for Bing Maps API and collect traffic data for a route.
    The idea is to get poll Bing Maps for a route and get the total duration in traffic. These
    data points are stored in pickle, and can be reopened later and examined visually.

    See Bing Routes API for more info on what parameters to use.
    https://msdn.microsoft.com/en-us/library/ff701717.aspx
    """
    def __init__(self, file_name, base_url, parameters, api_key):
        """
        :param file_name: {string} Name of pickle file to write data to.
        :param base_url: {string} Base URL of whatever Maps API is being used.
        :param parameters: {dictionary} See link above for info on parameters that can be used.
        :param api_key: {string} API key for whatever Maps API is being used.
        """
        self.parameters = parameters
        self.file_name = file_name
        self.base_url = base_url
        self.api_key = api_key
        self.all_data = []

        # Load any previous data pickle if it exists...
        if not os.path.isfile(self.file_name):
            pickle.dump(self.all_data, open(self.file_name, "wb"))
        else:
            self.all_data = pickle.load( open(self.file_name, "rb"))

    def build_url(self, params):
        """
        Builds a url by using base url and parameters.

        :param params: {dict} Dictionary containing url parameters.
                        -> See document link above for more details on how this works.
        :return: {string} Returns compiled url
        """
        url = self.base_url
        for param in params:
            if params[param] != None:
                url+=(param+'='+str(params[param])+'&')

        url+=('key='+self.api_key)
        return url

    def send_request(self, url):
        """
        Send a basic get request to a url and return a json.

        :param url: {string} URL to send get request to.
        :return: {dict} json in dictionary format
        """
        resp = requests.get(url)
        data = json.loads(resp.text)
        return data

    def parse_json(self, json):
        """
        Removes unnecessary data from received json.

        :param json: JSON received from send_request.
        :return: parsed json
        """
        return json['resourceSets'][0]['resources'][0]

    def get_packet(self, url, return_json, print_url = False):
        """
        :param url: {string }url to send packet to
        :param return_json: {bool} return all json data or just the travel duration traffic.
        :param print_url: {bool} whether or not you want to print the url to the console.
        :return: {tuple} Returns the timestamp of the packet as well as the received data (which could be in either
                         json format or an integer)
        """
        if print_url:
            print "Sending request to: {} ...".format(url)
        received_data = self.send_request(url)
        timestamp = datetime.now()
        duration = self.parse_json(received_data)['travelDurationTraffic']
        if not return_json:
            received_data = duration
        print "Trip time @ {} is {} seconds".format(timestamp, duration)
        return (timestamp, received_data)

    def collect_data(self, interval, store_json):
        """
        Use this collect data at a specified interval.
        :param interval: datetime.timedelta object. Used to specify how often a trip duration request should be made.
        """
        curr_time = datetime.now()
        while datetime.now() - curr_time < interval:
            sleep(10) # How often should it check the time
            if datetime.now() - curr_time >= interval:
                url = self.build_url(self.parameters)
                packet = self.get_packet(url, return_json=store_json)
                self.all_data.append(packet)
                pickle.dump(self.all_data, open(self.file_name, "wb"))

# TODO: Add plotting data feature...
def plot_data():
    pass

if __name__ == '__main__':

    # EXAMPLE USAGE
    BASE_URL = 'http://dev.virtualearth.net/REST/v1/Routes?'
    API_KEY = 'YOUR API KEY GOES HERE'

    FILE_NAME = "maps_data.p"

    PARAMETERS = {
        'waypoint.1': '39.345974, -120.161018',
        'waypoint.2': '37.508873, -105.984524',
        'distanceUnit': 'mi'
    }

    INTERVAL = timedelta(0, 0, 0 , 0, 1) # How often you want to get a data point (Currently set to one minute)

    mr = MapsRoute(api_key=API_KEY,
                   base_url=BASE_URL,
                   file_name=FILE_NAME,
                   parameters=PARAMETERS)

    # CAUTION. Setting store_json=True will take a lot more space. This has not been fully tested.
    while True:
        mr.collect_data(interval=INTERVAL, store_json=False)


