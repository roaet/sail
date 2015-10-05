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
import sail.exceptions.common as exc
from sail.services.base import ServiceBase


class NetworkService(ServiceBase):
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
