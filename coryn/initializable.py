import aiohttp


class Initializable:
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()
        self.base_url = "https://coryn.club"
