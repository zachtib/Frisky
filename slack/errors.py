class UnsupportedSlackEventTypeError(RuntimeError):

    def __init__(self, event_type: str, *args: object) -> None:
        super().__init__(*args)
        self.event_type = event_type
