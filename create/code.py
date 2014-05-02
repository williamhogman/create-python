import os.path

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

def run_code(code):
    g = {"__name__": "__web__"}
    l = {}
    exec(code, g, l)
    return l

class CodeManager(object):
    def __init__(self, script_folder):
        self.script_folder = os.path.abspath(script_folder)
        self.code_objects = {}
        self.modules = {}

    def get_code(self, fname):
        if fname not in self.code_objects:
            self.code_objects[fname] = compile_file(fname)

        return self.code_objects[fname]

    def get_module(self, fname):
        if fname not in self.modules:
            self.modules[fname] = run_code(self.get_code(fname))

        return self.modules[fname]

    def run_module(self, fname, nargs=[], kwargs={}):
        allow, path = allow_file(self.script_folder, fname)

        if not allow:
            return False, path

        mod = self.get_module(path)

        return True, mod["main"](*nargs, **kwargs)
