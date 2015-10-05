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
from functools import wraps

from sail.context import SetupContext
from sail.utils.generators import ArtifactGenerator
from sail.utils.generators import NetworkGenerator
from sail.tasks.task import Task

#TODO(roaet): might be dead code here
def doublewrap(f):
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return f(args[0])
        else:
            return lambda realf: f(realf, *args, **kwargs)
    return new_dec

#TODO(roaet): might be dead code here
@doublewrap
def sessionwrap(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ignore_errors = False
        if(len(args) >= 2 and hasattr(args[1], 'session') and
                type(args[1].session) is Session):
            ignore_errors = args[1].session.ignore_errors()
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if not ignore_errors:
                    raise e
            return None
    return wrap

class Session(object):
    def __init__(self):
        self.context = None
        self.logs = []
        self.generator = ArtifactGenerator()
        self.generator.register_generator(NetworkGenerator())

    def ignore_errors(self):
        return False if self.context is None else self.context.ignore_errors

    def setUp(self, auth_info, services):
        self.context = SetupContext(auth_info, services)
        self.context.session = self
        #TODO(roaet): This is probably not safe to do. Find better way.
        Task.context = self.context
        return self.context

    def log(self, msg):
        print msg
        self.logs.append(msg)
