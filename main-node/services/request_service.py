import json
import asyncio
import aiohttp

from application.custom_logger import logger
from application.count_down_latch import CountDownLatch


class RequestService:
    def __init__(self, write_concern, timeout=20):
        self.timeout = timeout
        self.latch = CountDownLatch(write_concern)

    async def send_payload(self, urls, payload):
        for url in urls:
            asyncio.create_task(self.async_request(url, payload=payload))

        await self.latch.wait()

    async def async_request(self, url, payload):
        conn = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
        session = aiohttp.ClientSession(connector=conn)

        async with session.put(url, json=payload, ssl=False) as response:
            obj = await response.read()
            json_response = json.loads(obj.decode('utf-8'))
            logger.info(f"Response code received: {json_response}")
            if json_response['status'] == 'ok':
                await self.latch.count_down()
                logger.info(f"done")

        await session.close()
        await conn.close()
