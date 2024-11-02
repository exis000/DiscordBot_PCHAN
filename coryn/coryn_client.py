import aiohttp

from coryn.methods import Methods

from .initializable import Initializable


class CorynClient(Methods, Initializable):
    def __init__(self) -> None:
        super().__init__()

    async def __aenter__(self) -> "CorynClient":
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        if self.session:
            await self.session.close()
