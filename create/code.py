import os.path
import sys
import collections
from werkzeug.wrappers import Response

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
    exec(code, g, l)
    return l

class Wrt(object):
    def __init__(self, resp):
        self.resp = resp

    def write(self, s):
        self.resp.response.append(s)

def run_code_plain_python(code, request, response):
    old_stdout = sys.stdout
    sys.stdout = Wrt(response)

    g = {
        "__name__": "__main__",
        "request": request,
        "response": response,
        "__web__": True
    }
    l = {}

    exec(code, g, l)

    sys.stdout = old_stdout

CACHE_DELTA = 0

class Script(object):
    def __init__(self, path):
        self.path = path
        self.opts = {}
        self.clean()

    def clean(self):
        self.mtime = self.file_mtime() 

        code = compile_file(self.path)
        module = run_code(code)

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


    def file_mtime(self):
        return os.path.getmtime(self.path)

    def update(self):
        if abs(self.file_mtime() - self.mtime) > CACHE_DELTA:
            self.clean()

    def run(self, request):
        self.update()
        if self.opts.get("mode") == "plain-python":
            response = Response([])
            run_code_plain_python(self.code, request, response)
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


class PlainPythonSys(ObjectWrapper):
    def __init__(self, response):
        ObjectWrapper.__init__(self, sys)

        

        self.stdout = Wrt()
