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

class Task(object):
    context = None
    def __init__(self, **kwargs):
        self.output = "" 
        self.success = True
        self.perform_undo = True
        self.context = Task.context
        self.context.register(self)
        self.logs = []
        self.artifact_key = 'unnamed'
        self.notify_success_list = kwargs.get('notify_success', [])

    def undo(self):
        pass

    def was_successful(self):
        return self.success

    def notify_success(self, message):
        for target in self.notify_success_list:
            target.notify(message)

    def notify(self, message):
        if message == "undone":
            self.perform_undo = False

    def store_artifact(self, artifact):
        self.log_store("['%s'] <- %s" % (self.artifact_key, artifact))
        self.context.add_artifact(self.artifact_key, artifact)

    def get_artifact(self, artifact):
        artifacts = self.context.get_artifacts(artifact)
        if artifacts is None:
            self.log_fail("No artifact named ['%s']" % artifact)
            return None
        if len(artifacts) > 1:
            self.log_fail("Ambiguous retrieve for artifact ['%s']" % artifact)
            return None
        a = artifacts[0]
        self.log_retrieve("['%s'] -> %s" % (artifact, a))
        return a

    def log(self, msg):
        self.context.log("%s]%s" % (self.__class__.__name__, msg))

    def log_debug(self, msg):
        self.log("DEBUG: %s" % (msg))

    def log_ignored_exception(self, msg):
        self.log("EXCEPT(ignored): %s" % msg)

    def log_fail(self, msg):
        self.log("FAIL: %s" % msg)

    def log_store(self, msg):
        self.log("STORE: %s" % msg)

    def log_retrieve(self, msg):
        self.log("RETRIEVE: %s" % msg)


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
