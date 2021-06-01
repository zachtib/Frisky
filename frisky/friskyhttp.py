from django.http import HttpResponse


class PostProcessingResponse(HttpResponse):

    def __init__(self, block, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block = block

    def close(self):
        super().close()
        self.block()
