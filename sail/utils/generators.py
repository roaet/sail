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


class ArtifactGenerator(object):
    def __init__(self):
        self.generators = {}

    def register_generator(self, generator):
        if not hasattr(generator, 'name'):
            return
        if generator.name not in self.generators:
            self.generators[generator.name] = generator

    def generate(self, resource):
        if resource not in self.generators:
            return None
        return self.generators[resource].generate()


class BaseGenerator(object):
    def __init__(self):
        self.generation_number = 0
        self.prefix = 'sail'
        self.join = '_'

    def _generate_name(self, resource):
        self.generation_number += 1
        return "%s%s%s%s%d" % (self.prefix, self.join, resource, self.join,
                               self.generation_number)


class NetworkGenerator(BaseGenerator):
    def __init__(self):
        super(NetworkGenerator, self).__init__()
        self.name = "network"

    def generate(self):
        return {"network": {"name": self._generate_name("network")}}
