import os.path

import collections
from werkzeug.wrappers import Response
import create.ppruntime as ppruntime

__all__ = ("CodeManager",)

def allow_file(script_folder, path):
    ap = os.path.abspath(os.path.join(script_folder, path))

    if ".." in ap:
        return False, "Invalid path"

    prefix = os.path.commonprefix((script_folder, ap))

    if prefix != script_folder:
        return False, "Invalid path"

    if not os.path.exists(ap):
        return False, "Not found"

    return True, ap

def compile_file(path):
    with open(path, "r") as f:
        source = f.read()
    return compile(source, path, "exec")

def run_code(code, name=None):
    g = {}
    if name:
        g["__name__"] = name

    l = {}
    try:
        exec(code, g, l)
    except StandardError as ex:
        return False, ex
    else:
        return True, l


CACHE_DELTA = 0

class BadScriptError(Exception):
    pass

class Script(object):
    def __init__(self, path):
        self.path = path
        self.opts = {}
        self.mtime = 0

    def inspect(self, code):
        """Inspects the code, in order to establish if has any options"""
        success, module = run_code(code)

        if not success:
            msg = "Inspecting the script caused exception: {}".format(repr(module))
            raise BadScriptError(msg)

        if "__webopts__" in module:
            self.opts = module["__webopts__"]
        
        if "handle_request" not in module and "__webopts__" not in module:
            self.opts["mode"] = "plain-python"
            self.module = None # Remove it because caching it doesn't help!
            self.code = code
        elif "handle_request" in module:
            self.opts["request_handler"] = "handle_request"

        if self.opts.get("mode") != "plain-python":
            self.code = None
            self.module = module

    def clean(self):
        self.mtime = self.file_mtime()
        code = compile_file(self.path)
        self.inspect(code)

    def file_mtime(self):
        return os.path.getmtime(self.path)

    def update(self):
        if abs(self.file_mtime() - self.mtime) > CACHE_DELTA:
            self.clean()

    def run(self, request):
        try:
            self.update()
        except BadScriptError:
            resp = Response("Unable to run script", status=500)
            return resp

        if self.opts.get("mode") == "plain-python":
            ppruntime.run_code(self.code, request)
            return response
        else:
            response = Response()
            self.module[self.opts["request_handler"]](request, response)
            return response


class CodeManager(collections.defaultdict):
    def __init__(self, script_folder):
        self.script_folder = os.path.abspath(script_folder)

    def run_module(self, fname, request):
        allow, path = allow_file(self.script_folder, fname)

        if not allow:
            return False, path
        return True, self[path].run(request)

    def __missing__(self, key):
        x = Script(key)
        self[key] = Script(key)
        return Script(key)
