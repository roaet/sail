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


class BaseContext(object):
    def __init__(self, auth_info, services):
        self.service_list = {}
        for service in services:
            if not hasattr(service, 'name'):
                continue
            self.service_list[service.name] = service
        self.tasks = []
        self.session = None
        self.auth_info = auth_info
        self.state = "Do"
        self.artifacts = {}

    def add_artifact(self, key, artifact):
        if key not in self.artifacts:
            self.artifacts[key] = []
        self.artifacts[key].append(artifact) 

    def get_artifacts(self, key):
        if key not in self.artifacts:
            return None
        return self.artifacts[key]

    def log(self, msg):
        self.session.log("[%s%s" % (self.state, msg))

    def set_session(self, session):
        self.session = session

    def register(self, task):
        self.tasks.append(task)

    def request_service(self, service_name):
        return self.service_list.get(service_name)

    def __enter__(self):
        self.state = "Do"

    def __exit__(self, type, value, tb):
        self.state = "Undo"
        while self.tasks:
            task = self.tasks.pop()
            task.undo()
        return False


class SetupContext(BaseContext):
    def __init__(self, auth_info, services):
        super(SetupContext, self).__init__(auth_info, services)
        self.ignore_errors = False

    def __enter__(self):
        super(SetupContext, self).__enter__()

    def __exit__(self, type, value, tb):
        super(SetupContext, self).__exit__(type, value, tb)
        return False
