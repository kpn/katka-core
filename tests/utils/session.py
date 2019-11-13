class Session:
    def post(self, *args, **kwargs):
        return Response()

    def get(self, *args, **kwargs):
        return Response()


class Response:
    def raise_for_status(self):
        pass
