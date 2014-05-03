
def handle_request(request, response):
    response.data = "Hello there, {}".format(request.args.get("name", "anon"))