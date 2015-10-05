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
import requests
import json

import sail.exceptions.common as exc


class RackspaceAuth(object):
    def __init__(self, auth):
        try:
            self.username = auth['username']
            self.api_key = auth['api_key']
        except KeyError as e:
            msg = "Missing %s in conf"
            raise exc.MissingRequiredInformation(msg % e)
        self.payload = {"auth": {"RAX-KSKEY:apiKeyCredentials": {
                        "username": self.username,
                        "apiKey": self.api_key}}}

    def __str__(self):
        return json.dumps(self.payload)


def _load_auth_method_class(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class AuthResponse(object):
    def __init__(self, json_resp):
        self.access = json_resp['access']
        self.raw = json_resp
        self.token = self.access['token']['id']
        self.catalog = self.access['serviceCatalog']
        self.tenant_id = self.access['token']['tenant']['id']


def do_auth(ctx, conf):
    if conf is None:
        raise exc.MissingRequiredInformation("Missing configuration")
    if 'auth' not in conf:
        raise exc.MissingRequiredInformation("Missing [auth] section in conf")
    auth = conf['auth']
    if 'endpoint' not in auth:
        raise exc.MissingRequiredInformation("Missing endpoint in conf")
    auth_endpoint = auth['endpoint']
    if 'auth_method' not in auth:
        raise exc.MissingRequiredInformation("Missing auth_method in conf")
    try:
        auth_method = _load_auth_method_class(auth['auth_method'])(auth)
    except AttributeError as e:
        msg = "Could not load auth_method. %s"
        raise exc.MissingRequiredInformation(msg % e)
    
    headers = {'Content-Type': auth.get('content_type', 'application/json')}
    r = requests.post(auth_endpoint, headers=headers, data=str(auth_method))
    try:
        json_resp = json.loads(r.text)
    except ValueError as e:
        raise exc.ParsingError(e)
    try:
        return AuthResponse(json_resp)
    except KeyError as e:
        raise exc.ParsingError(e)
