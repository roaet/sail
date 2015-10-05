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

from sail.tasks import task


class CreateNetwork(task.NetworkingTask):
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


class GetNetworks(task.NetworkingTask):
    def __init__(self, status=200):
        super(GetNetworks, self).__init__(status)

    def __call__(self):
        resp = self.net.get_networks(self.context)
        self.log_debug(resp)
        self.check_response(resp)
        return self


class DeleteNetwork(task.NetworkingTask):
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
