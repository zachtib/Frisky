class EmojiApiClient:
    pass


class EmojiService:
    __client: EmojiApiClient

    def __init__(self, client: EmojiApiClient):
        self.__client = client
