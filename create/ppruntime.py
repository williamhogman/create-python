"""Module containing classes for the plain python runtime"""
__all__ = ("run_code",)
import sys
from contextlib import contextmanager
from werkzeug.wrappers import Response

class ResponseAdapter(object):
    """Proxy object for writable files to a HTTP response"""
    def __init__(self, resp):
        self.resp = resp

    def write(self, s):
        self.resp.response.append(s)

DEFAULT_GLOBALS = {
    "__name__": "__main__",
    "__web__": True
}

def _create_context(request, response):
    g = {
        "request": request,
        "response": response,
    }
    g.update(DEFAULT_GLOBALS)

    l = {}
    return g, l


@contextmanager
def patch_stdout(proxy):
    old_stdout = sys.stdout
    sys.stdout = proxy
    yield
    sys.stdout = old_stdout


def run_code(code, request):
    response = Response([])
    globs, locs  = _create_context(request, response)
    with patch_stdout(ResponseAdapter(response)):
        try:
            exec(code, globs, locs)
        except StandardError as ex:
            print(ex)
