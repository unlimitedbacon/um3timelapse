#!/bin/python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import json
import os
import time
from getpass import getuser

## Ultimaker 3 API access class.
#  Allows for access of the Ultimaker 3 API with authentication.
#  Uses the python requests library to do the actual http requests, which does most of the work for us.
class Ultimaker3:
    # @param ip: IP address of the printer
    # @param application: name of the application in string form, used during authentication requests and is shown on the printer.
    def __init__(self, ip, application):
        self.__ip = ip
        self.__application = application
        self.__session = requests.sessions.Session()
        self.__setAuthData("", "")
    
    # Set new authentication data, authentication data is send with each HTTP request to make sure we can PUT/POST data.
    def __setAuthData(self, id, key):
        self.__auth_id = id
        self.__auth_key = key
        self.__auth = requests.auth.HTTPDigestAuth(self.__auth_id, self.__auth_key)
    
    # Load authentication data from a file. If this file does not exists, or the data in it is invalid, we request a new authentication set and store it in the file.
    def loadAuth(self, filename):
        try:
            data = json.load(open(filename, "rt"))
            self.__setAuthData(data["id"], data["key"])
        except IOError:
            self.__checkAuth()
            self.saveAuth(filename)
        if not self.__checkAuth():
            self.saveAuth(filename)

    # Save the authentication data to a file.
    def saveAuth(self, filename):
        json.dump({"id": self.__auth_id, "key": self.__auth_key}, open(filename, "wt"))
    
    # Check if our authentication is valid, and if it is not request a new ID/KEY combination, this function can block till the user selected ALLOW/DENY on the printer.
    def __checkAuth(self):
        if self.__auth_id == "" or self.get("api/v1/auth/verify").status_code != 200:
            print("Auth check failed, requesting new authentication")
            response = self.post("api/v1/auth/request", data={"application": self.__application, "user": getuser()})
            if response.status_code != 200:
                raise RuntimeError("Failed to request new API key")
            data = response.json()
            self.__setAuthData(data["id"], data["key"])
            while True:
                time.sleep(1)
                response = self.get("api/v1/auth/check/%s" % (self.__auth_id))
                data = response.json()
                print(data["message"])
                if data["message"] == "authorized":
                    print("Authorized.")
                    break
                if data["message"] == "unauthorized":
                    raise RuntimeError("Authorization denied")
            return False
        return True
    
    # Do a new HTTP request to the printer. It formats data as JSON, and fills in the IP part of the URL.
    def request(self, method, path, **kwargs):
        if "data" in kwargs:
            kwargs["data"] = json.dumps(kwargs["data"])
            if "headers" not in kwargs:
                kwargs["headers"] = {"Content-type": "application/json"}
        return self.__session.request(method, "http://%s/%s" % (self.__ip, path), auth=self.__auth, **kwargs)

    # Shorthand function to do a "GET" request.
    def get(self, path, **kwargs):
        return self.request("get", path, **kwargs)

    # Shorthand function to do a "PUT" request.
    def put(self, path, **kwargs):
        return self.request("put", path, **kwargs)

    # Shorthand function to do a "POST" request.
    def post(self, path, **kwargs):
        return self.request("post", path, **kwargs)
