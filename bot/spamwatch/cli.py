import aiohttp

from .. import config
from .types import BanInfo


class SpamWatchClinet:
    def __init__(self):
        self._host = "https://api.spamwat.ch"
        self.token = config.spamwatch.token
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(headers={"Authorization": f"Bearer {self.token}"})

    async def destroy(self):
        if self.session is not None:
            if not self.closed:
                await self.session.close()

    @property
    def closed(self):
        if self.session is None:
            return
        return self.session.closed

    async def request(self, path: str) -> object:
        async with self.session.get(url=f"{self._host}/{path}") as req:
            if req.status in [200, 201]:
                try:
                    return await req.json()
                except Exception:
                    return await req.text()

    async def get_ban(self, user_id: int):
        res = await self.request(f"banlist/{user_id}")
        if res:
            return BanInfo(**res)
