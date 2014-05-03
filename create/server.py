from werkzeug.wrappers import Request, Response

class ScriptServer(object):
    def __init__(self, code_mgr):
        self.code_mgr = code_mgr

    def dispatch_request(self, request):
        allow, res = self.code_mgr.run_module(request.path[1:], request)
        
        if not allow:
            return Response(res, status=404)

        return res

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)