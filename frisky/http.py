from django.http import HttpResponse


class FriskyResponse(HttpResponse):

    def __init__(self, callback, content=b'', *args, **kwargs):
        super().__init__(content, *args, **kwargs)
        self.callback = callback

    def close(self):
        super().close()
        self.callback()
