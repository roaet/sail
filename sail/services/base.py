#
# Copyright 2015 Justin Hammond
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import json

import requests


class ServiceResponse(object):
    def __init__(self, success, status, body, raw):
        self.success = success
        self.status = status
        self.body = body
        self.raw = raw

    def __str__(self):
        return "%s:%s" % (self.status, self.raw)


class ServiceController(object):
    def __init__(self):
        self.services = {}

    def register(self, key, service):
        if key not in self.services:
            self.services[key] = service
            return True
        return False

    def get_service(self, key):
        if key not in self.service:
            return None
        return self.services[key]


class ServiceBase(object):
    def __init__(self):
        pass

    def _get_collection(self, ctx, resource):
        url = "%s/%s/%s" % (self.endpoint, self.version, resource)
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': ctx.auth_info.token}
        r = requests.get(url, headers=headers)
        res = None
        success = True
        try:
            res = json.loads(r.text)
        except ValueError:
            if r.status_code != 200:
                success = False
        return ServiceResponse(success, r.status_code, res, r.text)

    def _create_resource(self, ctx, resource, info):
        url = "%s/%s/%s" % (self.endpoint, self.version, resource)
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': ctx.auth_info.token}
        payload = json.dumps(info)
        r = requests.post(url, headers=headers, data=payload)
        res = None
        success = True
        try:
            res = json.loads(r.text)
        except ValueError:
            if r.status_code != 201:
                success = False
        return ServiceResponse(success, r.status_code, res, r.text)

    def _delete_resource(self, ctx, resource, id):
        url = "%s/%s/%s/%s" % (self.endpoint, self.version, resource, id)
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': ctx.auth_info.token}
        r = requests.delete(url, headers=headers)
        res = None
        success = True
        if r.status_code != 204:
            success = False
        return ServiceResponse(success, r.status_code, res, r.text)
