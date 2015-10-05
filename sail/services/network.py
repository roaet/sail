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

import sail.exceptions.common as exc
from sail.task import Task


class ServiceResponse(object):
    def __init__(self, success, status, body, raw):
        self.success = success
        self.status = status
        self.body = body
        self.raw = raw

    def __str__(self):
        return "%s:%s" % (self.status, self.raw)


class Network(object):
    def __init__(self, conf):
        self.name = 'network'
        if conf is None:
            raise exc.MissingRequiredInformation("Missing configuration")
        if 'network' not in conf:
            raise exc.MissingRequiredInformation("Missing [network] section "
                                                 "in conf")
        network = conf['network']
        if 'endpoint' not in network:
            raise exc.MissingRequiredInformation("Missing endpoint in conf")
        self.endpoint = network['endpoint']
        if 'version' not in network:
            raise exc.MissingRequiredInformation("Missing endpoint in conf")
        self.version = network['version']

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

    def get_networks(self, ctx):
        return self._get_collection(ctx, "networks")

    def create_network(self, ctx, net_info):
        return self._create_resource(ctx, "networks", net_info)

    def delete_network(self, ctx, id):
        return self._delete_resource(ctx, "networks", id)

    def get_subnets(self, ctx):
        return self._get_collection(ctx, "subnets")

    def create_subnet(self, ctx, subnet_info):
        return self._create_resource(ctx, "subnets", subnet_info)

    def delete_subnet(self, ctx, id):
        return self._delete_resource(ctx, "subnets", id)

    def get_ports(self, ctx):
        return self._get_collection(ctx, "ports")

    def create_port(self, ctx, port_info):
        return self._create_resource(ctx, "ports", port_info)

    def delete_port(self, ctx, id):
        return self._delete_resource(ctx, "ports", id)

    def get_ip_addresses(self, ctx):
        return self._get_collection(ctx, "ip_addresses")

    def create_ip_addresses(self, ctx, ip_info):
        return self._create_resource(ctx, "ip_addresses", ip_info)

    def delete_ip_addresses(self, ctx, id):
        return self._delete_resource(ctx, "ip_addresses", id)


class RestfulTask(Task):
    def __init__(self, status, **kwargs):
        super(RestfulTask, self).__init__(**kwargs)
        self.expected_status = status

    def check_response(self, service_response, override=None):
        srv_status = service_response.status
        check = self.expected_status if override is None else override
        self.success = check == srv_status
        if not self.success:
            self.log_fail("Status mismatch. %s != %s" %
                          (check, service_response.status))
        return service_response


class NetworkingTask(RestfulTask):
    def __init__(self, status, **kwargs):
        super(NetworkingTask, self).__init__(status, **kwargs)
        self.net = self.context.request_service('network')


class CreateNetwork(NetworkingTask):
    def __init__(self, status=201, **kwargs):
        super(CreateNetwork, self).__init__(status, **kwargs)
        self.net_id = None
        self.artifact_key = 'network'

    def __call__(self, net_info=None):
        if net_info is None:
            net_info = self.context.session.generator.generate('network')
        resp = self.net.create_network(self.context, net_info)
        self.log_debug(resp)
        self.check_response(resp)
        try:
            new_net = resp.body
            self.net_id = new_net['network']['id']
            self.store_artifact(new_net)
            return self
        except KeyError as e:
            self.log_ignored_exception(e)

    def undo(self):
        if self.perform_undo and self.net_id is not None:
            try:
                resp = self.net.delete_network(self.context, self.net_id)
                self.check_response(resp, 204)
                self.log_debug(resp)
            except Exception as e:
                self.log_ignored_exception(e)


class GetNetworks(NetworkingTask):
    def __init__(self, status=200):
        super(GetNetworks, self).__init__(status)

    def __call__(self):
        resp = self.net.get_networks(self.context)
        self.log_debug(resp)
        self.check_response(resp)
        return self


class DeleteNetwork(NetworkingTask):
    def __init__(self, status=204, **kwargs):
        super(DeleteNetwork, self).__init__(status, **kwargs)
        self.net_id = None
        self.artifact_key = 'network'

    def __call__(self, id=None):
        if id is None:
            net = self.get_artifact(self.artifact_key)
            if net is None:
                self.log_fail("No id found for delete")
                return self
            id = net['network']['id']
        resp = self.net.delete_network(self.context, id)
        self.log_debug(resp)
        self.check_response(resp)
        if self.success:
            self.notify_success("undone")
        return self
