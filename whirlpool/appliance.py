import requests
import base64
import logging
import json
from datetime import datetime, timedelta, timedelta
from whirlpool.eventsocket import EventSocket

LOGGER = logging.getLogger(__name__)

class Appliance():
    def __init__(self, auth, said):
        self._auth = auth
        self._said = said
        self._data_dict = None
        self._event_socked = EventSocket(
            auth.get_access_token(), said, self._event_socket_handler)

    def _event_socket_handler(self, msg):
        json_msg = json.loads(msg)
        timestamp = json_msg["timestamp"]
        for (attr, val) in json_msg["attributeMap"].items():
            if not self.has_attribute(attr):
                continue
            self.set_attribute(attr, str(val), timestamp)

    def _create_headers(self):
        return {
            'Authorization': 'Bearer ' + self._auth.get_access_token(),
            'Content-Type': 'application/json',
            'Host': 'api.whrcloud.eu',
            'User-Agent': 'okhttp/3.12.0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

    def send_attributes(self, attributes):
        cmd_data = {
            "body": attributes,
            "header":{
                "said": self._said,
                "command": "setAttributes"
            }
        }

        headers = self._create_headers()
        with requests.session() as s:
            r = s.post('https://api.whrcloud.eu/api/v1/appliance/command', headers=headers, json=cmd_data)
            print(r.text)

    def get_attribute(self, attribute):
        return self._data_dict["attributes"][attribute]["value"]

    def has_attribute(self, attribute):
        return attribute in self._data_dict["attributes"]

    def set_attribute(self, attribute, value, timestamp):
        logging.debug(f"Updating attribute {attribute} with {value} ({timestamp})")
        self._data_dict["attributes"][attribute]["value"] = value
        self._data_dict["attributes"][attribute]["updateTime"] = timestamp

    def fetch_data(self):
        headers = self._create_headers()
        self._data_dict = None
        with requests.session() as s:
            r = s.get('https://api.whrcloud.eu/api/v1/appliance/{0}'.format(self._said), headers=headers)
            self._data_dict = json.loads(r.text)

    async def start_event_listener(self):
        self.fetch_data()
        self._event_socked.start()

    async def stop_event_listener(self):
        await self._event_socked.stop()

    #def get_account_id(self, user_details):
        #return user_details["accountId"]

    #def fetch_said(self, account_id):
        #headers = self._create_headers()
        #with requests.session() as s:
            #r = s.get('https://api.whrcloud.eu/api/v1/appliancebyaccount/{0}'.format(accountId), headers=headers)
            #print(r.text)
            #device_said = json.loads(r.text)["accountId"]

    #def fetch_user_details(self):
        #headers = self._create_headers()
        #with requests.session() as s:
            #r = s.get('https://api.whrcloud.eu/api/v1/getUserDetails', headers=headers)
            #return json.loads(r.text)
        #return None
