import json
from typing import Any, Dict

import aiohttp


class BaseService:
    def __init__(self, host: str, port: int, api_key: str = None):
        self.session = aiohttp.ClientSession()
        self.base_url = f"http://{host}:{port}"
        self.headers = {"Authorization": f"{api_key}"} if api_key else None

    async def request(self, method: str, url: str, **kwargs) -> Any:
        async with self.session.request(method, url, headers=self.headers, **kwargs) as response:
            text = await response.text()
            try:
                response.raise_for_status()
                return json.loads(text)
            except aiohttp.ClientResponseError as e:
                try:
                    error_body = json.loads(text)
                    detail = error_body.get("detail", text)
                except json.JSONDecodeError:
                    detail = text
                e.message = detail
                raise
            except Exception as e:
                print(f"An error occurred: {e}")
                raise

    async def get(self, url: str, params: Dict[str, Any] = None) -> Any:
        return await self.request("GET", url, params=params)

    async def post(self, url: str, data: Dict[str, Any] = None) -> Any:
        return await self.request("POST", url, json=data)

    async def close(self):
        await self.session.close()
